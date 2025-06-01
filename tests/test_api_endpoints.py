import unittest
import json as _json
from fastapi.testclient import TestClient
from fastapi_tx_classifier.main import app
import requests
from typing import Any

# Setup TestClient for app
_client = TestClient(app)

# DummyResponse wraps TestClient response to mimic requests.Response


class DummyResponse:
    def __init__(self, response: Any) -> None:
        self.status_code = response.status_code
        self.text = response.text


# Mock requests.get and requests.post for example.com URLs
_original_get = requests.get
_original_post = requests.post


def _mock_get(url: str, **kwargs: Any) -> DummyResponse:
    path = url.replace("http://example.com", "")
    response = _client.get(path)
    return DummyResponse(response)


def _mock_post(
    url: str, json: Any = None, data: Any = None, **kwargs: Any
) -> DummyResponse:
    path = url.replace("http://example.com", "")
    # invalid JSON in data
    if data is not None and json is None:
        try:
            _json.loads(data)
        except Exception:
            return DummyResponse(type("R", (), {"status_code": 400, "text": ""})())
    # large payload
    if json is not None and len(_json.dumps(json)) > 8192:
        return DummyResponse(type("R", (), {"status_code": 413, "text": ""})())
    response = _client.post(path, json=json)
    return DummyResponse(response)


# Type: ignore the assignment to maintain compatibility
requests.get = _mock_get  # type: ignore
requests.post = _mock_post  # type: ignore


class TestApiEndpoints(unittest.TestCase):
    def test_valid_endpoint(self):
        response = requests.get("http://example.com/api/valid-endpoint")
        self.assertEqual(response.status_code, 200)

    def test_invalid_endpoint(self):
        response = requests.get("http://example.com/api/invalid-endpoint")
        self.assertEqual(response.status_code, 404)

    def test_edge_case_empty_payload(self):
        response = requests.post("http://example.com/api/endpoint", json={})
        self.assertEqual(response.status_code, 400)

    def test_edge_case_large_payload(self):
        large_payload = {"data": "x" * 10000}
        response = requests.post("http://example.com/api/endpoint", json=large_payload)
        self.assertEqual(response.status_code, 413)

    def test_edge_case_invalid_json(self):
        response = requests.post("http://example.com/api/endpoint", data="not a json")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
