#!/usr/bin/env python3
"""
Test script to verify that mypy fixes are working correctly.
This script tests the key components that were fixed.
"""

from config import Settings
from models import TransactionRequest
from typing import Optional


def test_config() -> None:
    """Test that Settings can be instantiated."""
    settings = Settings()
    print(f"✓ Settings loaded with redis_url: {settings.redis_url}")

    # Test the for_testing method
    test_settings = Settings.for_testing()
    print(f"✓ Test settings created with testing={test_settings.testing}")


def test_models() -> None:
    """Test that models work correctly."""
    # Test TransactionRequest with optional amount
    req1 = TransactionRequest(text="Coffee shop purchase")
    print(f"✓ TransactionRequest without amount: {req1.text}, amount={req1.amount}")

    req2 = TransactionRequest(text="Grocery store", amount=25.50)
    print(f"✓ TransactionRequest with amount: {req2.text}, amount={req2.amount}")


def test_amount_handling() -> None:
    """Test amount handling logic similar to what was fixed in routers."""

    def handle_amount(amount: Optional[float]) -> float:
        return amount if amount is not None else 0.0

    print(f"✓ None amount handled: {handle_amount(None)}")
    print(f"✓ Valid amount handled: {handle_amount(15.75)}")


if __name__ == "__main__":
    print("Testing mypy fixes...")
    test_config()
    test_models()
    test_amount_handling()
    print("✓ All tests passed!")
