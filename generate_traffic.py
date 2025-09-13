#!/usr/bin/env python3
"""
Generate real traffic to test the monitoring system
"""

import requests
import time
import random
from datetime import datetime

def generate_traffic():
    base_url = "http://127.0.0.1:5000"

    print("🚀 Starting traffic generation...")
    print(f"Target server: {base_url}")

    # List of endpoints to hit
    endpoints = [
        "/",
        "/gamelist",
        "/about",
        "/premium",
        "/profile",
        "/admin",
        "/admin/traffic",
        "/api/admin/traffic/stats",
        "/api/admin/traffic/logs"
    ]

    methods = ["GET", "GET", "GET", "POST"]  # More GETs than POSTs

    try:
        for i in range(15):
            endpoint = random.choice(endpoints)
            method = random.choice(methods) if endpoint not in ["/api/admin/traffic/stats", "/api/admin/traffic/logs"] else "GET"

            print(f"📡 Request {i+1}/15: {method} {endpoint}")

            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{base_url}{endpoint}", json={"test": "data"}, timeout=5)

                print(f"    ✅ Response: {response.status_code} ({len(response.content)} bytes)")

            except requests.exceptions.RequestException as e:
                print(f"    ❌ Error: {e}")

            # Small delay between requests
            time.sleep(0.5)

        print("\n🔍 Checking traffic stats...")
        try:
            stats_response = requests.get(f"{base_url}/api/admin/traffic/stats", timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"📊 Total requests tracked: {stats.get('total_requests', 0)}")
                print(f"📊 Error rate: {stats.get('error_rate', 0)}%")
                print(f"📊 Avg duration: {stats.get('avg_duration_ms', 0)}ms")
            else:
                print(f"❌ Could not get stats: {stats_response.status_code}")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")

    except KeyboardInterrupt:
        print("\n⏹️  Traffic generation stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("  TRAFFIC GENERATOR FOR SWAWEB MONITORING")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print()

    generate_traffic()

    print()
    print("✅ Traffic generation completed!")
    print(f"Finished at: {datetime.now()}")
    print()
    print("🌐 Now visit http://127.0.0.1:5000/admin/traffic to see the results!")