#!/usr/bin/env python3
"""
Batch operations    try:
        response = requests.post(
            f"{BASE_URL}/classify-transa        async with session.post(
            f"{BASE_URL}/classify-transaction",
            json=transaction,
            headers={"Content-Type": "application/json"}
        ) as response:",
            json=transaction,
            headers={"Content-Type": "application/json"},
            timeout=10
        )e for the FastAPI Transaction Classifier API.

This script demonstrates:
- Processing multiple transactions efficiently
- Bulk classification operations
- Performance monitoring
- Error handling for batch operations
"""

import time
import asyncio
import aiohttp
from typing import List, Dict, Any, cast
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# API base URL
BASE_URL = "http://localhost:8000"

# Sample transaction data for batch processing
SAMPLE_TRANSACTIONS = [
    {"text": "Starbucks Coffee Morning", "amount": 4.85},
    {"text": "Shell Gas Station Fill Up", "amount": 52.30},
    {"text": "Amazon Prime Purchase", "amount": 29.99},
    {"text": "Walmart Grocery Shopping", "amount": 87.42},
    {"text": "Netflix Monthly Subscription", "amount": 15.99},
    {"text": "McDonald's Lunch", "amount": 8.75},
    {"text": "Target Home Goods", "amount": 45.20},
    {"text": "Uber Ride Downtown", "amount": 12.50},
    {"text": "Home Depot Tools", "amount": 156.78},
    {"text": "Spotify Premium", "amount": 9.99},
    {"text": "CVS Pharmacy", "amount": 23.45},
    {"text": "Chipotle Dinner", "amount": 11.20},
    {"text": "Best Buy Electronics", "amount": 299.99},
    {"text": "Costco Bulk Shopping", "amount": 167.83},
    {"text": "Apple App Store", "amount": 2.99},
]


def classify_single_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Classify a single transaction synchronously."""
    try:
        response = requests.post(
            f"{BASE_URL}/classify-transaction",
            json=transaction,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        result["original"] = transaction
        return result
    except requests.RequestException as e:
        return {"error": str(e), "original": transaction}


def batch_classify_sequential(
    transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Process transactions sequentially."""
    print(f"Processing {len(transactions)} transactions sequentially...")

    start_time = time.time()
    results = []

    for i, transaction in enumerate(transactions, 1):
        print(f"  Processing {i}/{len(transactions)}: {transaction['text']}")
        result = classify_single_transaction(transaction)
        results.append(result)

    end_time = time.time()
    print(f"Sequential processing completed in {end_time - start_time:.2f} seconds")

    return results


def batch_classify_parallel(
    transactions: List[Dict[str, Any]], max_workers: int = 5
) -> List[Dict[str, Any]]:
    """Process transactions in parallel using threads."""
    print(
        f"Processing {len(transactions)} transactions in parallel (max_workers={max_workers})..."
    )

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_transaction = {
            executor.submit(classify_single_transaction, txn): txn
            for txn in transactions
        }

        # Collect results as they complete
        for i, future in enumerate(as_completed(future_to_transaction), 1):
            transaction = future_to_transaction[future]
            try:
                result = future.result()
                print(f"  Completed {i}/{len(transactions)}: {transaction['text']}")
                results.append(result)
            except Exception as e:
                print(f"  Error processing {transaction['text']}: {e}")
                results.append({"error": str(e), "original": transaction})

    end_time = time.time()
    print(f"Parallel processing completed in {end_time - start_time:.2f} seconds")

    return results


async def classify_single_async(
    session: aiohttp.ClientSession, transaction: Dict[str, Any]
) -> Dict[str, Any]:
    """Classify a single transaction asynchronously."""
    try:
        async with session.post(
            f"{BASE_URL}/classify-transaction",
            json=transaction,
            headers={"Content-Type": "application/json"},
        ) as response:
            response.raise_for_status()
            result = await response.json()
            result["original"] = transaction
            return result
    except Exception as e:
        return {"error": str(e), "original": transaction}


async def batch_classify_async(
    transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Process transactions asynchronously."""
    print(f"Processing {len(transactions)} transactions asynchronously...")

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [classify_single_async(session, txn) for txn in transactions]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results: List[Dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {"error": str(result), "original": transactions[i]}
                )
            else:
                processed_results.append(cast(Dict[str, Any], result))

    end_time = time.time()
    print(f"Async processing completed in {end_time - start_time:.2f} seconds")

    return processed_results


def analyze_results(results: List[Dict[str, Any]]) -> None:
    """Analyze and display batch processing results."""
    print("\n📊 Batch Processing Analysis")
    print("=" * 40)

    total = len(results)
    successful = len([r for r in results if "error" not in r])
    failed = total - successful

    print(f"Total transactions: {total}")
    print(f"Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")

    if successful > 0:
        # Category distribution
        categories: Dict[str, int] = {}
        confidences = []

        for result in results:
            if "error" not in result:
                category = result.get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1

                if "confidence" in result:
                    confidences.append(result["confidence"])

        print("\nCategory Distribution:")
        for category, count in sorted(categories.items()):
            percentage = count / successful * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")

        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            print(f"\nAverage Confidence: {avg_confidence:.3f}")

    if failed > 0:
        print("\nErrors:")
        for result in results:
            if "error" in result:
                original = result.get("original", {})
                desc = original.get("text", "Unknown")
                print(f"  {desc}: {result['error']}")


def main():
    """Run batch processing examples."""
    print("🚀 FastAPI Transaction Classifier - Batch Operations\n")

    # Test API availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print("✅ API is available\n")
    except requests.RequestException as e:
        print(f"❌ API is not available: {e}")
        print("Please start the API server with: python main.py")
        return

    # 1. Sequential Processing
    print("1. Sequential Processing")
    print("-" * 25)
    sequential_results = batch_classify_sequential(SAMPLE_TRANSACTIONS[:5])
    analyze_results(sequential_results)

    # 2. Parallel Processing
    print("\n\n2. Parallel Processing")
    print("-" * 22)
    parallel_results = batch_classify_parallel(SAMPLE_TRANSACTIONS[:10])
    analyze_results(parallel_results)

    # 3. Async Processing
    print("\n\n3. Asynchronous Processing")
    print("-" * 26)
    async_results = asyncio.run(batch_classify_async(SAMPLE_TRANSACTIONS))
    analyze_results(async_results)

    # 4. Performance Comparison
    print("\n\n4. Performance Comparison")
    print("-" * 25)

    test_data = SAMPLE_TRANSACTIONS[:8]

    # Time each method
    start = time.time()
    batch_classify_sequential(test_data)
    sequential_time = time.time() - start

    start = time.time()
    batch_classify_parallel(test_data, max_workers=4)
    parallel_time = time.time() - start

    start = time.time()
    asyncio.run(batch_classify_async(test_data))
    async_time = time.time() - start

    print(f"\nPerformance for {len(test_data)} transactions:")
    print(f"  Sequential: {sequential_time:.2f} seconds")
    print(
        f"  Parallel:   {parallel_time:.2f} seconds ({sequential_time/parallel_time:.1f}x faster)"
    )
    print(
        f"  Async:      {async_time:.2f} seconds ({sequential_time/async_time:.1f}x faster)"
    )

    print("\n✅ Batch operations completed!")
    print("💡 For best performance, use async processing for I/O-bound operations")


if __name__ == "__main__":
    main()
