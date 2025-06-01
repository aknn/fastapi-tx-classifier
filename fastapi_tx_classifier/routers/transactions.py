import json
import logging
from fastapi import APIRouter, Depends
from pydantic import ValidationError
from redis.asyncio import Redis
from typing import Dict, Any

from ..models import Transaction, TransactionCategory
from .. import redis_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/transactions")
async def list_transactions(
    redis: Redis = Depends(redis_client.get_redis),
) -> Dict[str, Any]:
    """Lists all stored transactions."""
    transactions = {}
    # Fetch all keys and filter numeric transaction IDs
    keys = await redis.keys("tx:*")
    tx_keys = [k for k in keys if k.startswith("tx:") and k.split(":")[1].isdigit()]
    if not tx_keys:
        return {"message": "No transactions found"}
    values = await redis.mget(*tx_keys)
    for key, value_json in zip(tx_keys, values):
        if not value_json:
            logger.warning(f"Missing value for key {key}")
            continue
        try:
            tx_id = key.split(":")[1]
            transaction_data = json.loads(value_json)
            transaction = Transaction.model_validate(transaction_data)
            transactions[tx_id] = transaction.model_dump()
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON for key {key}")
        except (ValidationError, KeyError, IndexError) as e:
            logger.warning(f"Invalid data for key {key}: {e}")
    return {"transactions": transactions}


@router.get("/transaction-stats")
async def transaction_stats(
    redis: Redis = Depends(redis_client.get_redis),
) -> Dict[str, Any]:
    """Calculates statistics based on transaction categories."""
    # Initialize counts to zero
    category_counts = {cat.value: 0 for cat in TransactionCategory}
    # Fetch all transaction keys
    keys = await redis.keys("tx:*")
    tx_keys = [k for k in keys if k.startswith("tx:") and k.split(":")[1].isdigit()]
    if not tx_keys:
        return {"message": "No transactions found"}
    # Count categories
    values = await redis.mget(*tx_keys)
    for key, value_json in zip(tx_keys, values):
        if not value_json:
            logger.warning(f"Missing value for key {key}")
            continue
        try:
            data = json.loads(value_json)
            txn = Transaction.model_validate(data)
            category_counts[txn.category.value] += 1
        except Exception as e:
            logger.warning(f"Error processing key {key}: {e}")
    total = sum(category_counts.values())
    return {"total_transactions": total, "stats": category_counts}
