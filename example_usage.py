import requests
import json

# Example usage of the Stock Availability API

# API endpoint
url = "http://localhost:8000/api/stock-availability"

# Example 1: Basic search
example_1 = {
    "city": "chennai",
    "skus": ["SKU4"],
    "page": 1,
    "pageSize": 2,
    "sortBy": "TOTAL STOCK",
    "sortOrder": "DESC",
    "dateFrom": "2025-09-01",
    "dateTo": "2025-09-30",
    "search": "toothbrush"
}

# Example 2: Search without city filter
example_2 = {
    "skus": ["SKU4", "SKU5"],
    "page": 1,
    "pageSize": 10,
    "sortBy": "INSTOCK DARKSTORES",
    "sortOrder": "ASC",
    "search": "baby"
}

# Example 3: Search with date range only
example_3 = {
    "page": 1,
    "pageSize": 5,
    "sortBy": "DAYS OF STOCK",
    "sortOrder": "DESC",
    "dateFrom": "2025-09-10",
    "dateTo": "2025-09-20",
    "search": "cleaning"
}

example_4 = {
  "city": "delhi",
  "skus": ["SKU1", "SKU2"],
  "page": 1,
  "pageSize": 2,
  "sortBy": "TOTAL STOCK",
  "sortOrder": "DESC",
  "dateFrom": "2025-09-01",
  "dateTo": "2025-09-30",
  "search": "baby wipes"
}


def test_api(example_data, example_name):
    """Test the API with example data"""
    print(f"\n=== {example_name} ===")
    print("Request JSON:")
    print(json.dumps(example_data, indent=2))
    
    try:
        response = requests.post(url, json=example_data)
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Stock Availability API Test Examples")
    print("=" * 50)
    
    # Test all examples
    test_api(example_1, "Example 1: Chennai toothbrush search")
    test_api(example_2, "Example 2: Baby products search")
    test_api(example_3, "Example 3: Cleaning products with date range")
    test_api(example_4, "Example 4: Delhi baby wipes search")

    print("\n" + "=" * 50)