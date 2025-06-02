#!/usr/bin/env python3
"""
Basic usage examples for the FastAPI Transaction Classifier API.

This script demonstrates the most common API operations:
- Health check
- Transaction classification
- Retrieving transactions
- Getting statistics
"""

import json
import requests
from typing import Dict, Any

# API base URL - adjust if running on different host/port
BASE_URL = "http://localhost:8000"


def health_check() -> Dict[str, Any]:
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Health check failed: {e}")
        return {"status": "error", "message": str(e)}


def classify_transaction(description: str, amount: float) -> Dict[str, Any]:
    """Classify a single transaction."""
    payload = {"description": description, "amount": amount}

    try:
        response = requests.post(
            f"{BASE_URL}/classify",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Classification failed: {e}")
        return {"error": str(e)}


def get_all_transactions() -> Dict[str, Any]:
    """Retrieve all stored transactions."""
    try:
        response = requests.get(f"{BASE_URL}/transactions")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to get transactions: {e}")
        return {"error": str(e)}


def get_transaction_stats() -> Dict[str, Any]:
    """Get transaction category statistics."""
    try:
        response = requests.get(f"{BASE_URL}/transaction-stats")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to get stats: {e}")
        return {"error": str(e)}


def main():
    """Run example API calls."""
    print("🚀 FastAPI Transaction Classifier - Basic Examples\n")

    # 1. Health Check
    print("1. Health Check")
    health = health_check()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   Response: {json.dumps(health, indent=2)}\n")

    # 2. Classify some sample transactions
    print("2. Transaction Classification")

    sample_transactions = [
        {"description": "Starbucks Coffee", "amount": 4.85},
        {"description": "Shell Gas Station", "amount": 52.30},
        {"description": "Amazon Purchase", "amount": 29.99},
        {"description": "Walmart Grocery", "amount": 87.42},
        {"description": "Netflix Subscription", "amount": 15.99},
    ]

    for i, txn in enumerate(sample_transactions, 1):
        print(f"   {i}. Classifying: {txn['description']} (${txn['amount']})")
        result = classify_transaction(txn["description"], txn["amount"])

        if "error" not in result:
            category = result.get("category", "unknown")
            confidence = result.get("confidence", 0)
            print(f"      → Category: {category} (confidence: {confidence:.2f})")
        else:
            print(f"      → Error: {result['error']}")
        print()

    # 3. Get all transactions
    print("3. Retrieving All Transactions")
    all_transactions = get_all_transactions()

    if "transactions" in all_transactions:
        count = len(all_transactions["transactions"])
        print(f"   Found {count} stored transactions")

        # Show first few transactions
        if count > 0:
            print("   Sample transactions:")
            for tx_id, tx_data in list(all_transactions["transactions"].items())[:3]:
                print(
                    f"     ID {tx_id}: {tx_data.get('description', 'N/A')} → {tx_data.get('category', 'N/A')}"
                )
    else:
        print(f"   {all_transactions.get('message', 'No transactions found')}")
    print()

    # 4. Get statistics
    print("4. Transaction Statistics")
    stats = get_transaction_stats()

    if "stats" in stats:
        total = stats.get("total_transactions", 0)
        print(f"   Total transactions: {total}")
        print("   Category breakdown:")

        for category, count in stats["stats"].items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"     {category}: {count} ({percentage:.1f}%)")
    else:
        print(f"   {stats.get('message', 'No statistics available')}")

    print("\n✅ Examples completed!")
    print(f"🌐 View interactive docs at: {BASE_URL}/docs")


if __name__ == "__main__":
    main()
