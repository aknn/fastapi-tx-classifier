from fastapi import APIRouter, Depends
from models import TransactionRequest, Transaction, TransactionResponse
import redis_client
import json
import time
import logging
from prometheus_client import Histogram, Counter  # Import Counter

# Import the new classification logic
from classification_logic import classify_transaction_detailed
from config import Settings
import mlflow

# Initialize MLflow tracking
settings = Settings()
mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
mlflow.set_experiment(settings.mlflow_experiment_name)

router = APIRouter(prefix="/classify-transaction", tags=["classification"])

# Metrics
# Latency histogram measures the *entire* route execution time
latency = Histogram(
    "classify_latency_seconds", "Latency of classify_transaction endpoint in seconds"
)
# Cache requests counter remains relevant
cache_requests = Counter(
    "cache_requests_total",
    "Cache requests labeled by result (hit or miss)",
    ["result"],
)

# Logger
logger = logging.getLogger("app")


@router.post(
    "",
    response_model=TransactionResponse,
    summary="Classify a transaction text",
)
async def classify_transaction_route(
    request: TransactionRequest, redis=Depends(redis_client.get_redis)
) -> TransactionResponse:
    start_time = time.perf_counter()
    amount_str = f"{request.amount:.2f}" if request.amount is not None else "0.00"
    cache_key = f"tx_classified:{request.text.strip().lower()}:{amount_str}"
    # Skip cache for refunds (negative amounts)
    is_refund = request.amount is not None and request.amount < 0

    # --- Cache Check (skip for refunds) ---
    if not is_refund:
        cached_data = await redis.get(cache_key)
        if cached_data:
            cache_requests.labels(result="hit").inc()
            duration = time.perf_counter() - start_time
            latency.observe(duration)
            logger.info(
                json.dumps(
                    {
                        "event": "cache_hit",
                        "key": cache_key,
                        "duration_ms": duration * 1000,
                    }
                )
            )
            # Log cache hit inference to MLflow
            mlflow.start_run()
            mlflow.log_param("text", request.text)
            mlflow.log_param("amount", request.amount)
            mlflow.set_tag("cache_result", "hit")
            mlflow.log_metric("latency", duration)
            mlflow.end_run()
            try:
                cached_result = json.loads(cached_data)
                transaction_data = cached_result.get("transaction")
                if transaction_data:
                    transaction_obj = Transaction(**transaction_data)
                    return TransactionResponse(
                        transaction=transaction_obj,
                        message=cached_result.get(
                            "message", "Transaction loaded from cache"
                        ),
                    )
                else:
                    logger.warning(
                        f"Cache data for key {cache_key} missing 'transaction' field."
                    )
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.error(
                    f"Error decoding/validating cache data for key {cache_key}: {e}"
                )
        # Fall through to classify if no valid cache

    # --- Cache Miss - Classification ---
    cache_requests.labels(result="miss").inc()

    # Should start at 1 if reset to 0
    transaction_id = await redis.incr("tx:id_counter")

    # Pass the transaction amount into classification logic
    category, confidence, hit_type = await classify_transaction_detailed(
        request.text, request.amount
    )

    transaction = Transaction(
        id=transaction_id,
        text=request.text,
        amount=request.amount,
        category=category,
        confidence=confidence,
    )

    message = (
        f"Transaction classified as {category.value} via {hit_type} ({confidence:.2f})"
    )
    # This is the object returned to the user
    response_data = TransactionResponse(transaction=transaction, message=message)
    # This is what gets stored in the classification cache (keyed by text+amount)
    # Use .dict() for older Pydantic or .model_dump() for v2
    result_data_for_cache = response_data.model_dump()

    # --- Store Results ---

    # Store ONLY the transaction data keyed by ID for list/stats endpoints
    # Use model_dump_json() for Pydantic v2+ or .json() for older versions
    await redis.set(f"tx:{transaction_id}", transaction.model_dump_json())

    # Store the full response data (transaction + message) keyed by text+amount for classification caching (skip refunds)
    if not is_refund:
        CACHE_TTL_SECONDS = 3600
        await redis.set(
            cache_key, json.dumps(result_data_for_cache), ex=CACHE_TTL_SECONDS
        )

    # --- Logging and Metrics ---
    duration = time.perf_counter() - start_time
    latency.observe(duration)
    logger.info(
        json.dumps(
            {
                "event": "cache_miss",
                "key": cache_key,
                "transaction_id": transaction_id,
                "category": category.value,
                "confidence": confidence,
                "hit_type": hit_type,
                "duration_ms": duration * 1000,
            }
        )
    )
    # Log cache miss inference to MLflow
    mlflow.start_run()
    mlflow.log_param("text", request.text)
    mlflow.log_param("amount", request.amount)
    mlflow.set_tag("cache_result", "miss")
    mlflow.set_tag("hit_type", hit_type)
    mlflow.set_tag("category", category.value)
    mlflow.log_metric("confidence", confidence)
    mlflow.log_metric("latency", duration)
    mlflow.end_run()

    return response_data  # Return the Pydantic model instance
