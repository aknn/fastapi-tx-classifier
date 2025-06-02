#!/bin/bash

# FastAPI Transaction Classifier - cURL Examples
# These examples show how to interact with the API using command-line tools

API_URL="http://localhost:8000"

echo "🚀 FastAPI Transaction Classifier - cURL Examples"
echo "================================================="
echo

# Function to pretty print JSON responses
pretty_json() {
    if command -v jq >/dev/null 2>&1; then
        echo "$1" | jq '.'
    else
        echo "$1"
    fi
}

# 1. Health Check
echo "1. Health Check"
echo "   Command: curl -s $API_URL/health"
response=$(curl -s "$API_URL/health")
pretty_json "$response"
echo

# 2. System Status
echo "2. System Status"
echo "   Command: curl -s $API_URL/status"
response=$(curl -s "$API_URL/status")
pretty_json "$response"
echo

# 3. Classify a single transaction
echo "3. Classify Transaction"
echo "   Command: curl -X POST $API_URL/classify -H 'Content-Type: application/json'"
echo "   Data: {'description': 'Starbucks Coffee', 'amount': 4.85}"

response=$(curl -s -X POST "$API_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Starbucks Coffee",
    "amount": 4.85
  }')
pretty_json "$response"
echo

# 4. Classify another transaction
echo "4. Classify Another Transaction"
echo "   Command: curl -X POST $API_URL/classify"
echo "   Data: {'description': 'Shell Gas Station', 'amount': 52.30}"

response=$(curl -s -X POST "$API_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Shell Gas Station",
    "amount": 52.30
  }')
pretty_json "$response"
echo

# 5. Get all transactions
echo "5. Get All Transactions"
echo "   Command: curl -s $API_URL/transactions"
response=$(curl -s "$API_URL/transactions")
pretty_json "$response"
echo

# 6. Get transaction statistics
echo "6. Transaction Statistics"
echo "   Command: curl -s $API_URL/transaction-stats"
response=$(curl -s "$API_URL/transaction-stats")
pretty_json "$response"
echo

# 7. Error example - invalid data
echo "7. Error Example - Invalid Data"
echo "   Command: curl -X POST $API_URL/classify (with invalid amount)"
echo "   Data: {'description': 'Test', 'amount': 'invalid'}"

response=$(curl -s -X POST "$API_URL/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Test Transaction",
    "amount": "invalid"
  }')
pretty_json "$response"
echo

echo "✅ cURL examples completed!"
echo "💡 Tip: Install 'jq' for better JSON formatting: sudo apt-get install jq"
echo "🌐 View interactive docs at: $API_URL/docs"
