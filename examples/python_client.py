#!/usr/bin/env python3
"""
Full-featured Python client for the FastAPI Transaction Classifier API.

This client provides:
- Type-safe API interactions
- Automatic retry logic
- Connection pooling
- Comprehensive error handling
- Async support
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union, Sequence
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import aiohttp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TransactionCategory(Enum):
    """Transaction categories."""

    FOOD_DINING = "food_dining"
    TRANSPORTATION = "transportation"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    BILLS_UTILITIES = "bills_utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    TRAVEL = "travel"
    OTHER = "other"


@dataclass
class Transaction:
    """Transaction data model."""

    description: str
    amount: float
    category: Optional[str] = None
    confidence: Optional[float] = None
    transaction_id: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ClassificationResult:
    """Classification result from API."""

    category: str
    confidence: float
    transaction_id: str
    timestamp: str
    original_transaction: Transaction


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class TransactionClassifierClient:
    """Synchronous client for the Transaction Classifier API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"} if data else None,
            )

            # Handle HTTP errors
            if not response.ok:
                try:
                    error_data = response.json()
                    message = error_data.get("detail", f"HTTP {response.status_code}")
                except (json.JSONDecodeError, KeyError):
                    message = f"HTTP {response.status_code}: {response.text}"

                raise APIError(
                    message,
                    response.status_code,
                    error_data if "error_data" in locals() else {},
                )

            return response.json()

        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        return self._make_request("GET", "/health")

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return self._make_request("GET", "/status")

    def classify_transaction(
        self, transaction: Union[Transaction, Dict[str, Any]]
    ) -> ClassificationResult:
        """Classify a single transaction."""
        # Prepare payload with 'text' and 'amount'
        # Normalize input into text (str) and amount (float)
        if isinstance(transaction, Transaction):
            text_val: str = transaction.description
            amount_val: float = transaction.amount
            original = transaction
        else:
            text_val = transaction.get("text") or transaction.get("description") or ""
            amount_val = float(transaction.get("amount") or 0.0)
            original = Transaction(description=text_val, amount=amount_val)
        payload = {"text": text_val, "amount": amount_val}

        res = self._make_request("POST", "/classify-transaction", payload)
        # Expecting {'transaction': {...}, 'message': ...}
        if "transaction" not in res or not isinstance(res["transaction"], dict):
            raise APIError(
                "Invalid response from server: missing 'transaction' field", details=res
            )
        tx_dict = res["transaction"]
        try:
            category = tx_dict["category"]
            confidence = tx_dict["confidence"]
            transaction_id = str(tx_dict["id"])
            timestamp = tx_dict.get("timestamp", "")
        except KeyError as e:
            raise APIError(f"Missing field in transaction response: {e}", details=res)

        return ClassificationResult(
            category=category,
            confidence=confidence,
            transaction_id=transaction_id,
            timestamp=timestamp,
            original_transaction=original,
        )

    def classify_batch(
        self, transactions: Sequence[Union[Transaction, Dict[str, Any]]]
    ) -> List[ClassificationResult]:
        """Classify multiple transactions."""
        results = []
        for txn in transactions:
            try:
                result = self.classify_transaction(txn)
                results.append(result)
            except APIError as e:
                # Log error but continue with other transactions
                print(f"Failed to classify transaction: {e}")
                continue
        return results

    def get_transactions(self) -> List[Transaction]:
        """Get all stored transactions."""
        response = self._make_request("GET", "/transactions")

        transactions = []
        if "transactions" in response:
            for tx_id, tx_data in response["transactions"].items():
                transaction = Transaction(
                    description=tx_data["description"],
                    amount=tx_data["amount"],
                    category=tx_data.get("category"),
                    confidence=tx_data.get("confidence"),
                    transaction_id=tx_id,
                    timestamp=tx_data.get("timestamp"),
                )
                transactions.append(transaction)

        return transactions

    def get_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics."""
        return self._make_request("GET", "/transaction-stats")

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncTransactionClassifierClient:
    """Asynchronous client for the Transaction Classifier API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_concurrent: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make async HTTP request."""
        if not self.session:
            raise APIError(
                "Client session not initialized. Use 'async with' context manager."
            )

        url = f"{self.base_url}{endpoint}"

        async with self.semaphore:
            try:
                async with self.session.request(
                    method=method, url=url, json=data, params=params
                ) as response:
                    if not response.ok:
                        try:
                            error_data = await response.json()
                            message = error_data.get(
                                "detail", f"HTTP {response.status}"
                            )
                        except (aiohttp.ContentTypeError, KeyError):
                            message = f"HTTP {response.status}: {await response.text()}"

                        raise APIError(message, response.status)

                    return await response.json()

            except aiohttp.ClientError as e:
                raise APIError(f"Request failed: {str(e)}")

    async def classify_transaction(
        self, transaction: Union[Transaction, Dict[str, Any]]
    ) -> ClassificationResult:
        """Classify a single transaction asynchronously."""
        if isinstance(transaction, Transaction):
            data = transaction.to_dict()
            original = transaction
        else:
            data = transaction
            original = Transaction(**transaction)

        result = await self._make_request("POST", "/classify-transaction", data)

        return ClassificationResult(
            category=result["category"],
            confidence=result["confidence"],
            transaction_id=result["transaction_id"],
            timestamp=result["timestamp"],
            original_transaction=original,
        )

    async def classify_batch(
        self, transactions: Sequence[Union[Transaction, Dict[str, Any]]]
    ) -> List[ClassificationResult]:
        """Classify multiple transactions concurrently."""
        tasks = [self.classify_transaction(txn) for txn in transactions]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return successful results
        successful_results = [r for r in results if isinstance(r, ClassificationResult)]
        failed_count = len(results) - len(successful_results)

        if failed_count > 0:
            print(
                f"Warning: {failed_count} out of {len(transactions)} classifications failed"
            )

        return successful_results


def main():
    """Example usage of the client."""
    print("🚀 FastAPI Transaction Classifier - Python Client Examples\n")

    # Example transactions
    sample_transactions = [
        Transaction("Starbucks Coffee", 4.85),
        Transaction("Shell Gas Station", 52.30),
        Transaction("Amazon Purchase", 29.99),
        Transaction("Walmart Grocery", 87.42),
        Transaction("Netflix Subscription", 15.99),
    ]

    # Synchronous client example
    print("1. Synchronous Client Example")
    print("-" * 30)

    try:
        with TransactionClassifierClient() as client:
            # Health check
            health = client.health_check()
            print(f"API Status: {health.get('status', 'unknown')}")

            # Classify transactions
            print("\nClassifying transactions:")
            for txn in sample_transactions[:3]:
                try:
                    result = client.classify_transaction(txn)
                    print(
                        f"  {txn.description} → {result.category} (confidence: {result.confidence:.3f})"
                    )
                except APIError as e:
                    print(f"  Error classifying {txn.description}: {e}")

            # Get statistics
            stats = client.get_statistics()
            if "stats" in stats:
                print(f"\nTotal transactions: {stats['total_transactions']}")

    except APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Asynchronous client example
    print("\n\n2. Asynchronous Client Example")
    print("-" * 31)

    async def async_example():
        try:
            async with AsyncTransactionClassifierClient() as client:
                # Batch classification
                print("Batch classifying transactions asynchronously...")
                start_time = time.time()

                results = await client.classify_batch(sample_transactions)

                end_time = time.time()
                print(
                    f"Classified {len(results)} transactions in {end_time - start_time:.2f} seconds"
                )

                for result in results:
                    txn = result.original_transaction
                    print(
                        f"  {txn.description} → {result.category} (confidence: {result.confidence:.3f})"
                    )

        except APIError as e:
            print(f"API Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    # Run async example
    try:
        asyncio.run(async_example())
    except Exception as e:
        print(f"Async example failed: {e}")

    print("\n✅ Client examples completed!")
    print("💡 Use the synchronous client for simple scripts")
    print("💡 Use the async client for high-throughput applications")


if __name__ == "__main__":
    main()
