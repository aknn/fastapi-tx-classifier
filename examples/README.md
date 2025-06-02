# API Examples

This directory contains practical examples of how to interact with the FastAPI Transaction Classifier API.

## Quick Start

1. Start the API server:
   ```bash
   python main.py
   ```

2. API will be available at: `http://localhost:8000`
3. Interactive docs at: `http://localhost:8000/docs`

## Examples Included

- **`basic_usage.py`** - Simple transaction classification
- **`batch_operations.py`** - Bulk transaction processing
- **`curl_examples.sh`** - Command-line API calls
- **`postman_collection.json`** - Postman collection for testing
- **`python_client.py`** - Full Python client implementation

## Authentication

Currently, the API doesn't require authentication. In production, you would typically include:

```python
headers = {
    "Authorization": "Bearer your-api-key",
    "Content-Type": "application/json"
}
```

## Error Handling

All examples include proper error handling patterns. Common error responses:

- `400 Bad Request` - Invalid input data
- `404 Not Found` - Transaction not found
- `500 Internal Server Error` - Server issues

## Performance Tips

- Use batch operations for multiple transactions
- Implement client-side caching for repeated queries
- Monitor response times and adjust timeouts accordingly
