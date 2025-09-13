#!/usr/bin/env python3
"""
SwaWeb Server Launcher with PermGuard Monitoring
Cross-platform launcher for Flask server and PermGuard monitor
"""

import sys
import subprocess
import time
import os
import platform
from pathlib import Path

def print_header():
    """Вывести заголовок лаунчера"""
    print("=" * 60)
    print("SWAWEB SERVER WITH PERMGUARD MONITORING")
    print("=" * 60)
    print(f"Python: {sys.version.split()[0]}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Directory: {os.getcwd()}")
    print("=" * 60)

def check_requirements():
    """Проверить наличие необходимых файлов"""
    required_files = [
        "app.py",
        "permguard_monitor.py",
        "permguard_auth.py"
    ]

    missing_files = []

    for file in required_files:
        if Path(file).exists():
            print(f"[OK] Found: {file}")
        else:
            print(f"[ERROR] Missing: {file}")
            missing_files.append(file)

    if missing_files:
        print(f"\n[ERROR] Missing required files: {', '.join(missing_files)}")
        return False

    return True

def start_flask_server():
    """Запустить Flask сервер"""
    print("\n[START] Starting Flask server...")

    if platform.system() == "Windows":
        # Windows
        subprocess.Popen([
            'start', 'cmd', '/k',
            'title SwaWeb Flask Server && python app.py'
        ], shell=True)
    else:
        # Linux/macOS
        subprocess.Popen([
            'gnome-terminal', '--title=SwaWeb Flask Server',
            '--', 'python3', 'app.py'
        ])

def start_permguard_monitor():
    """Запустить монитор PermGuard"""
    print("[MONITOR] Starting PermGuard monitor...")

    if platform.system() == "Windows":
        # Windows
        subprocess.Popen([
            'start', 'cmd', '/k',
            'title PermGuard Monitor && python permguard_monitor.py'
        ], shell=True)
    else:
        # Linux/macOS
        subprocess.Popen([
            'gnome-terminal', '--title=PermGuard Monitor',
            '--', 'python3', 'permguard_monitor.py'
        ])

def show_success_message():
    """Показать сообщение об успешном запуске"""
    print("\n" + "=" * 60)
    print("SUCCESS: BOTH APPLICATIONS LAUNCHED!")
    print("=" * 60)
    print("Window 1: Flask Server")
    print("   URL: http://localhost:5000")
    print("   Admin: http://localhost:5000/admin")
    print("   Traffic: http://localhost:5000/admin/traffic")
    print()
    print("Window 2: PermGuard Real-time Monitor")
    print("   Log file: permguard_detailed.log")
    print("   Colored output with emojis")
    print("   Real-time updates")
    print()
    print("TIPS:")
    print("   - Use Ctrl+C to stop monitor")
    print("   - Check permguard_detailed.log for full logs")
    print("   - Visit /admin/traffic for web-based monitoring")
    print("=" * 60)

def main():
    """Главная функция лаунчера"""
    try:
        print_header()

        print("\n[CHECK] Checking requirements...")
        if not check_requirements():
            input("\nPress Enter to exit...")
            return 1

        print("\n[START] Starting applications...")

        # Запустить Flask сервер
        start_flask_server()

        # Пауза чтобы сервер успел запуститься
        time.sleep(2)

        # Запустить монитор PermGuard
        start_permguard_monitor()

        # Показать сообщение об успехе
        show_success_message()

        input("\nPress Enter to close this launcher...")
        return 0

    except KeyboardInterrupt:
        print("\n\n[STOP] Launcher interrupted by user")
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)