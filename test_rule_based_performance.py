#!/usr/bin/env python3
"""
Comprehensive test script for rule-based transaction classification system
"""
from fastapi_tx_classifier.classification_logic import classify_transaction_detailed
import asyncio
import pandas as pd
from typing import Dict, List, Any
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_test_dataset() -> List[Dict[str, Any]]:
    """Create comprehensive test dataset matching real-world scenarios"""
    return [
        # Food & Dining
        {"description": "Starbucks Coffee Shop", "amount": 5.50, "expected": "Food"},
        {"description": "McDonald's Restaurant", "amount": 8.99, "expected": "Food"},
        {"description": "Waitrose Supermarket", "amount": 65.20, "expected": "Food"},
        {
            "description": "Asda Groceries Weekly Shop",
            "amount": 45.00,
            "expected": "Food",
        },
        {"description": "Tesco Metro", "amount": 12.50, "expected": "Food"},
        {"description": "Pizza Express Dinner", "amount": 35.00, "expected": "Food"},
        {
            "description": "groceries and toiletries",
            "amount": 25.00,
            "expected": "Food",
        },
        {"description": "DinNER at M&S", "amount": 10.00, "expected": "Food"},
        # Transport
        {
            "description": "Uber Ride to Airport",
            "amount": 12.30,
            "expected": "Transport",
        },
        {"description": "Shell Gas Station", "amount": 40.00, "expected": "Transport"},
        {
            "description": "London Underground TfL",
            "amount": 15.00,
            "expected": "Transport",
        },
        {"description": "BP Petrol Station", "amount": 55.00, "expected": "Transport"},
        {
            "description": "£20 uber to waitrose for food",
            "amount": 20.00,
            "expected": "Transport",
        },
        # Food delivery (should be Food, not Transport)
        {"description": "Uber Eats Delivery", "amount": 18.50, "expected": "Food"},
        # Entertainment
        {
            "description": "Netflix Monthly Subscription",
            "amount": 15.99,
            "expected": "Entertainment",
        },
        {"description": "Spotify Premium", "amount": 9.99, "expected": "Entertainment"},
        {
            "description": "Cinema Tickets Vue",
            "amount": 24.00,
            "expected": "Entertainment",
        },
        {
            "description": "Amazon Prime Video",
            "amount": 8.99,
            "expected": "Entertainment",
        },
        {
            "description": "Movie Uber Night",
            "amount": 15.00,
            "expected": "Entertainment",
        },
        # Shopping
        {"description": "Amazon UK Purchase", "amount": 45.99, "expected": "Shopping"},
        {"description": "Apple Store", "amount": 89.00, "expected": "Shopping"},
        {
            "description": "John Lewis Department Store",
            "amount": 125.50,
            "expected": "Shopping",
        },
        {"description": "Zara Fashion", "amount": 79.99, "expected": "Shopping"},
        # Bills & Utilities
        {
            "description": "British Gas Electricity Bill",
            "amount": 75.00,
            "expected": "Bills",
        },
        {"description": "Thames Water Bill", "amount": 45.00, "expected": "Bills"},
        {"description": "BT Broadband Monthly", "amount": 32.99, "expected": "Bills"},
        {"description": "Council Tax Payment", "amount": 150.00, "expected": "Bills"},
        {"description": "GaS BiLl Payment", "amount": 50.00, "expected": "Utilities"},
        # Rent & Housing
        {
            "description": "London Rent Payment Landlord",
            "amount": 1200.00,
            "expected": "Rent",
        },
        {
            "description": "Monthly Rent Direct Debit",
            "amount": 1200.00,
            "expected": "Rent",
        },
        # Transfers
        {
            "description": "Transfer to Savings Account",
            "amount": 200.00,
            "expected": "Transfer",
        },
        {"description": "Payment to Friend", "amount": 50.00, "expected": "Transfer"},
        {
            "description": "ISA Monthly Contribution",
            "amount": 500.00,
            "expected": "Transfer",
        },
        # Edge cases
        {"description": "", "amount": 10.00, "expected": "Other"},
        {"description": "12345", "amount": 5.00, "expected": "Other"},
        {"description": "PAYPAL *UNKNOWN", "amount": 25.99, "expected": "Other"},
        {"description": "Cash Withdrawal ATM", "amount": 100.00, "expected": "Other"},
        {"description": "Super savings", "amount": 5.00, "expected": "Other"},
        # Refunds and negative amounts
        {"description": "Amazon refund", "amount": -15.99, "expected": "Shopping"},
        {"description": "Bank Interest Credit", "amount": -2.50, "expected": "Other"},
        {"description": "Free coffee voucher", "amount": 0.00, "expected": "Food"},
        # Punctuation tests
        {"description": "Lunch, with friends", "amount": 30.00, "expected": "Food"},
    ]


async def test_rule_based_performance():
    """Test the rule-based classification system comprehensively"""

    print("=== Rule-Based Transaction Classification Test ===\n")

    test_data = create_test_dataset()
    results = []
    correct_predictions = 0
    total_tests = len(test_data)

    print(f"Testing {total_tests} transactions...\n")

    # Track performance by category
    category_performance = {}
    hit_type_counts = {}

    for i, test_case in enumerate(test_data, 1):
        description = test_case["description"]
        amount = test_case["amount"]
        expected = test_case["expected"]

        # Classify using rule-based system
        predicted_category, confidence, hit_type = await classify_transaction_detailed(
            description, amount
        )
        predicted = predicted_category.value

        # Check if prediction is correct
        is_correct = predicted.lower() == expected.lower()
        if is_correct:
            correct_predictions += 1

        # Track category performance
        if expected not in category_performance:
            category_performance[expected] = {"correct": 0, "total": 0}
        category_performance[expected]["total"] += 1
        if is_correct:
            category_performance[expected]["correct"] += 1

        # Track hit types
        hit_type_counts[hit_type] = hit_type_counts.get(hit_type, 0) + 1

        results.append(
            {
                "description": description,
                "amount": amount,
                "expected": expected,
                "predicted": predicted,
                "confidence": confidence,
                "hit_type": hit_type,
                "correct": is_correct,
            }
        )

        # Show progress for longer descriptions
        desc_display = (
            description[:40] + "..." if len(description) > 40 else description
        )
        status = "✓" if is_correct else "✗"
        print(
            f"{i:2d}. {status} {desc_display:<45} Expected: {expected:<12} Got: {predicted:<12} ({confidence:.2f}, {hit_type})"
        )

    # Overall accuracy
    accuracy = correct_predictions / total_tests * 100
    print("\n=== OVERALL RESULTS ===")
    print(f"Total Tests: {total_tests}")
    print(f"Correct: {correct_predictions}")
    print(f"Accuracy: {accuracy:.1f}%")

    # Category-wise performance
    print("\n=== CATEGORY PERFORMANCE ===")
    print(f"{'Category':<15} {'Correct':<8} {'Total':<8} {'Accuracy':<10}")
    print("-" * 45)
    for category in sorted(category_performance.keys()):
        stats = category_performance[category]
        cat_accuracy = stats["correct"] / stats["total"] * 100
        print(
            f"{category:<15} {stats['correct']:<8} {stats['total']:<8} {cat_accuracy:>7.1f}%"
        )

    # Hit type analysis
    print("\n=== HIT TYPE ANALYSIS ===")
    print(f"{'Hit Type':<20} {'Count':<8} {'Percentage':<12}")
    print("-" * 42)
    for hit_type in sorted(hit_type_counts.keys()):
        count = hit_type_counts[hit_type]
        percentage = count / total_tests * 100
        print(f"{hit_type:<20} {count:<8} {percentage:>9.1f}%")

    # Confidence analysis
    df = pd.DataFrame(results)
    print("\n=== CONFIDENCE ANALYSIS ===")
    print(f"Average Confidence: {df['confidence'].mean():.3f}")
    print("Confidence by Correctness:")
    print(f"  Correct predictions: {df[df['correct']]['confidence'].mean():.3f}")
    print(f"  Incorrect predictions: {df[~df['correct']]['confidence'].mean():.3f}")

    # Show misclassified transactions
    incorrect = df[~df["correct"]]
    if len(incorrect) > 0:
        print("\n=== MISCLASSIFIED TRANSACTIONS ===")
        print(
            f"{'Description':<40} {'Expected':<12} {'Predicted':<12} {'Confidence':<12} {'Hit Type'}"
        )
        print("-" * 90)
        for _, row in incorrect.iterrows():
            desc = (
                row["description"][:37] + "..."
                if len(row["description"]) > 40
                else row["description"]
            )
            print(
                f"{desc:<40} {row['expected']:<12} {row['predicted']:<12} {row['confidence']:<12.2f} {row['hit_type']}"
            )

    # Suggestions for improvement
    print("\n=== RECOMMENDATIONS ===")
    if accuracy < 90:
        print("• Consider adding more specific keywords to classification_config.json")
        print("• Review misclassified transactions for pattern recognition")

    low_confidence = df[df["confidence"] < 0.8]
    if len(low_confidence) > 0:
        print(f"• {len(low_confidence)} transactions have low confidence (<0.8)")
        print("• Consider fuzzy matching improvements or ML fallback")

    high_other_count = hit_type_counts.get("default_other", 0)
    if high_other_count > total_tests * 0.1:  # More than 10% default to OTHER
        print(f"• {high_other_count} transactions defaulted to OTHER category")
        print("• Expand keyword coverage or improve text normalization")

    return df


if __name__ == "__main__":
    try:
        results_df = asyncio.run(test_rule_based_performance())

        # Save results for further analysis
        results_df.to_csv(
            "/workspaces/fastapi-template/rule_based_test_results.csv", index=False
        )
        print("\nResults saved to rule_based_test_results.csv")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()
