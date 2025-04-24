import requests
import argparse
import logging
import json  # Add missing import

logging.basicConfig(level=logging.INFO)


def test_endpoint(url, method, data=None):
    try:
        if method.lower() == 'get':
            response = requests.get(url)
        elif method.lower() == 'post':
            response = requests.post(url, json=data)
        else:
            logging.error("Unsupported method: %s", method)
            return

        logging.info("Response from %s: %s", url, response.status_code)
        logging.info("Response body: %s", response.text)
    except requests.exceptions.RequestException as e:
        logging.error("Error testing endpoint %s: %s", url, e)


def run_predefined_tests(base_url):
    logging.info("Running predefined test cases...")
    # Test 1: Get all transactions
    test_endpoint(f"{base_url}/transactions/", "get")
    # Test 2: Post valid transaction
    test_endpoint(f"{base_url}/transactions/", "post", {"amount": 100.50,
                  "merchant": "Test Shop", "description": "Valid purchase"})
    # Test 3: Edge case: huge amount
    test_endpoint(f"{base_url}/transactions/", "post",
                  {"amount": 999999, "merchant": "Unknown", "description": ""})
    # Test 4: Invalid transaction (negative amount)
    test_endpoint(f"{base_url}/transactions/", "post",
                  {"amount": -100, "merchant": "Test"})
    # Test 5: Malformed transaction (missing fields)
    test_endpoint(f"{base_url}/transactions/",
                  "post", {"merchant": "No Amount"})


def main():
    parser = argparse.ArgumentParser(description='API Tester')
    parser.add_argument('url', type=str, help='API endpoint URL')
    parser.add_argument('method', type=str, choices=[
                        'get', 'post'], help='HTTP method to use')
    parser.add_argument('--data', type=str, help='JSON data for POST requests')
    parser.add_argument('--run-all', action='store_true',
                        help='Run all predefined test cases')
    parser.add_argument('--base-url', type=str, default='http://localhost:8000',
                        help='Base URL for predefined tests')

    args = parser.parse_args()

    if args.run_all:
        run_predefined_tests(args.base_url)
        return

    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            logging.error("Invalid JSON data: %s", args.data)
            return

    test_endpoint(args.url, args.method, data)


if __name__ == '__main__':
    main()
