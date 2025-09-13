#!/usr/bin/env python3
"""
Test script to simulate traffic and test traffic monitoring functionality
"""

import time
from datetime import datetime
from permguard_auth import permguard_auth

def simulate_traffic():
    """Simulate some traffic data for testing"""
    print("Simulating traffic data...")

    # Simulate some traffic entries
    test_entries = [
        {
            'id': f"traffic_test_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'method': 'GET' if i % 2 == 0 else 'POST',
            'path': f'/test/path/{i}',
            'endpoint': f'test_endpoint_{i}',
            'status_code': 200 if i < 8 else 404,
            'duration_ms': 50 + (i * 10),
            'ip_address': '127.0.0.1',
            'user_agent': 'Test User Agent',
            'user': f'test_user_{i % 3}',
            'content_length': 1024,
            'referrer': None,
            'args': {},
        }
        for i in range(10)
    ]

    # Add entries to traffic log
    permguard_auth.traffic_log.extend(test_entries)

    print(f"Added {len(test_entries)} test traffic entries")
    print(f"Total traffic entries: {len(permguard_auth.traffic_log)}")

    # Test stats
    stats = permguard_auth.get_traffic_stats()
    print("\nTraffic Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test logs
    logs = permguard_auth.get_traffic_logs(limit=5)
    print(f"\nRecent Traffic Logs ({len(logs)} entries):")
    for log in logs:
        print(f"  {log['timestamp']} - {log['method']} {log['path']} - {log['status_code']} ({log['duration_ms']}ms)")

if __name__ == "__main__":
    simulate_traffic()