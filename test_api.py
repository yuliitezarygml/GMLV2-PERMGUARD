#!/usr/bin/env python3
"""
Test API endpoints
"""

import requests
import json

def test_traffic_apis():
    base_url = "http://127.0.0.1:5000"

    print("Testing Traffic API endpoints...")

    try:
        # Test stats endpoint
        print("\n1. Testing /api/admin/traffic/stats")
        response = requests.get(f"{base_url}/api/admin/traffic/stats")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"   Error: {response.text}")

        # Test logs endpoint
        print("\n2. Testing /api/admin/traffic/logs")
        response = requests.get(f"{base_url}/api/admin/traffic/logs?limit=3")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} log entries")
            if data:
                print(f"   First entry: {data[0]}")
        else:
            print(f"   Error: {response.text}")

        # Test admin page
        print("\n3. Testing /admin/traffic page")
        response = requests.get(f"{base_url}/admin/traffic")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Length: {len(response.content)} bytes")

    except requests.exceptions.ConnectionError:
        print("Error: Flask server is not running on http://127.0.0.1:5000")
        print("Please run: python app.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_traffic_apis()