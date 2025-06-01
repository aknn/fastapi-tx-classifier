from fastapi_tx_classifier.models import TransactionCategory

# client is now provided as a fixture from conftest.py


def test_classify_transaction_route_and_list(client):
    payload = {"text": "Lunch at a restaurant", "amount": 12.50}
    r = client.post("/classify-transaction", json=payload)
    assert r.status_code == 200
    body = r.json()
    txn = body["transaction"]
    assert txn["id"] == 1
    assert txn["text"] == payload["text"]
    assert txn["amount"] == payload["amount"]
    assert txn["category"] == TransactionCategory.FOOD.value

    # now GET /transactions
    r2 = client.get("/transactions")
    assert r2.status_code == 200
    all_txns = r2.json()["transactions"]
    assert "1" in all_txns
    assert all_txns["1"]["category"] == TransactionCategory.FOOD.value


def test_transaction_stats_empty(client):
    r = client.get("/transaction-stats")
    assert r.status_code == 200
    assert r.json() == {"message": "No transactions found"}


def test_transaction_stats_counts(client):
    # add two food txns and one other
    client.post("/classify-transaction", json={"text": "Dinner", "amount": 20})
    client.post(
        "/classify-transaction", json={"text": "Grocery shopping", "amount": 30}
    )
    client.post("/classify-transaction", json={"text": "XYZ", "amount": 5})

    r = client.get("/transaction-stats")
    stats = r.json()["stats"]
    # FOOD = 2, OTHER = 1, others zero
    assert stats["food"] == 2
    assert stats["other"] == 1
    for cat, count in stats.items():
        if cat not in ("food", "other"):
            assert count == 0


def test_classify_transaction_empty_text(client):
    """Empty description should default to OTHER with low confidence."""
    r = client.post("/classify-transaction", json={"text": "", "amount": 10})
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.OTHER.value
    assert txn["confidence"] == 0.6


def test_classify_transaction_multiple_keywords(client):
    """If text contains keywords from multiple categories, first match (alphabetical) wins."""
    r = client.post(
        "/classify-transaction", json={"text": "Movie Uber Night", "amount": 15}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    # 'entertainment' comes before 'transport' alphabetically
    assert txn["category"] == TransactionCategory.ENTERTAINMENT.value


def test_classify_transaction_case_insensitive(client):
    """Classification should ignore case."""
    r = client.post(
        "/classify-transaction", json={"text": "GaS BiLl Payment", "amount": 50}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.UTILITIES.value
    assert txn["confidence"] == 1.0


def test_classify_transaction_numeric_only(client):
    """Numeric-only or non-matching text returns OTHER."""
    r = client.post("/classify-transaction", json={"text": "12345", "amount": 5})
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.OTHER.value
    assert txn["confidence"] == 0.6


def test_edge_case_dinner_at_ms(client):
    """'DinNER at M&S' should be classified as FOOD with 1.0 confidence."""
    r = client.post(
        "/classify-transaction", json={"text": "DinNER at M&S", "amount": 10}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.FOOD.value
    assert txn["confidence"] == 1.0


def test_edge_case_groceries_and_toiletries(client):
    """'groceries and toiletries' should be FOOD with 1.0 confidence."""
    r = client.post(
        "/classify-transaction", json={"text": "groceries and toiletries", "amount": 25}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.FOOD.value
    assert txn["confidence"] == 1.0


def test_edge_case_uber_waitrose_food(client):
    """'£20 uber to waitrose for food' currently classifies as TRANSPORT with 1.0 confidence."""
    r = client.post(
        "/classify-transaction",
        json={"text": "£20 uber to waitrose for food", "amount": 20},
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.TRANSPORT.value
    assert txn["confidence"] == 1.0


def test_edge_case_punctuation(client):
    """Text with punctuation like commas should still match keywords."""
    # Assuming 'lunch' is a keyword for FOOD
    r = client.post(
        "/classify-transaction", json={"text": "Lunch, with friends", "amount": 30}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.FOOD.value
    assert txn["confidence"] == 0.9  # Now 0.9 for token match instead of 1.0


def test_edge_case_partial_keyword(client):
    """Partial keywords (substrings) should not match unless they are keywords themselves."""
    # Assuming 'super' is not a keyword, but 'supermarket' might be.
    # This should default to OTHER.
    r = client.post(
        "/classify-transaction", json={"text": "Super savings", "amount": 5}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.OTHER.value
    # Confidence might vary depending on implementation, assuming default low confidence
    assert txn["confidence"] == 0.6


def test_edge_case_zero_amount(client):
    """A transaction with zero amount should still be classified based on text."""
    # Assuming 'coffee' is a keyword for FOOD
    r = client.post(
        "/classify-transaction", json={"text": "Free coffee voucher", "amount": 0}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.FOOD.value
    assert txn["confidence"] == 0.9  # Now 0.9 for token match instead of 1.0


def test_edge_case_negative_amount(client):
    """A transaction with a negative amount (e.g., refund) should classify based on text."""
    # 'Amazon' is a keyword for SHOPPING even in a refund context
    r = client.post(
        "/classify-transaction", json={"text": "Amazon refund", "amount": -15}
    )
    assert r.status_code == 200
    txn = r.json()["transaction"]
    assert txn["category"] == TransactionCategory.SHOPPING.value
    assert txn["confidence"] == 0.9  # Confidence for token match
