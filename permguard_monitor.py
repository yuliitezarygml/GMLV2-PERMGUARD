#!/usr/bin/env python3
"""
PermGuard Real-time Log Monitor
Отслеживает логи PermGuard в реальном времени
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

def clear_console():
    """Очистить консоль"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Вывести заголовок монитора"""
    print("=" * 80)
    print("  PERMGUARD REAL-TIME MONITOR")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log file: permguard_detailed.log")
    print("Monitoring... (Press Ctrl+C to stop)")
    print("=" * 80)
    print()

def format_log_line(line, line_number):
    """Форматировать строку лога для красивого вывода"""
    line = line.strip()
    if not line:
        return None

    # Получить текущее время для отметки
    current_time = datetime.now().strftime('%H:%M:%S')

    # Добавить номер строки и время
    formatted = f"[{line_number:04d}] [{current_time}] {line}"

    # Цветовое кодирование для разных типов логов (адаптировано для Windows)
    if 'ALLOWED' in line or 'successful' in line or 'initialized successfully' in line:
        return f"{formatted}"  # Зеленый - убираем цвета для Windows
    elif 'DENIED' in line or 'ERROR' in line or 'Failed' in line:
        return f"!!! {formatted}"  # Красный - используем символы
    elif 'WARNING' in line or 'warning' in line:
        return f"*** {formatted}"  # Желтый - используем символы
    elif 'AUTH REQUEST' in line or 'Making authorization request' in line:
        return f">>> {formatted}"  # Голубой - используем символы
    elif 'TRAFFIC' in line or 'GET ' in line or 'POST ' in line:
        return f"~~~ {formatted}"  # Пурпурный - используем символы
    elif 'ADMIN ACCESS' in line or 'admin' in line.lower():
        return f"### {formatted}"  # Жирный синий - используем символы
    elif 'INFO' in line or 'DEBUG' in line:
        return formatted  # Обычный текст
    else:
        return formatted

def show_recent_logs(num_lines=5):
    """Показать последние несколько строк логов"""
    log_file_path = Path("permguard_detailed.log")

    if not log_file_path.exists():
        print("No recent logs available yet...")
        return

    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            recent_lines = lines[-num_lines:] if len(lines) >= num_lines else lines

            print("RECENT ACTIVITY:")
            print("-" * 60)
            for i, line in enumerate(recent_lines):
                formatted_line = format_log_line(line, len(lines) - len(recent_lines) + i + 1)
                if formatted_line:
                    print(formatted_line)
            print("-" * 60)
            print(f"Now monitoring for new logs... (Total lines: {len(lines)})")
    except Exception as e:
        print(f"Error reading recent logs: {e}")

def monitor_log_file():
    """Мониторинг файла логов в реальном времени"""
    log_file_path = Path("permguard_detailed.log")

    # Создать файл если не существует
    if not log_file_path.exists():
        print("Log file not found. Creating...")
        log_file_path.touch()
        return

    # Показать недавние логи при запуске
    show_recent_logs(10)

    line_number = 0

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            # Получить текущее количество строк
            lines = f.readlines()
            line_number = len(lines)

            # Перейти к концу файла для мониторинга новых строк
            f.seek(0, 2)

            while True:
                line = f.readline()
                if line:
                    line_number += 1
                    formatted_line = format_log_line(line, line_number)
                    if formatted_line:
                        print(f"\n>>> NEW: {formatted_line}")
                        sys.stdout.flush()
                else:
                    time.sleep(0.1)  # Короткая пауза если нет новых строк

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("⏹️  Monitoring stopped by user")
        print(f"[STATS] Total lines processed: {line_number}")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] Error monitoring log file: {e}")

def show_stats():
    """Показать статистику логов"""
    log_file_path = Path("permguard_detailed.log")

    if not log_file_path.exists():
        print("📄 No log file found yet.")
        return

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        total_lines = len(lines)
        auth_requests = len([l for l in lines if '🛡️' in l or 'AUTH REQUEST' in l])
        allowed = len([l for l in lines if '✅' in l or 'ALLOWED' in l])
        denied = len([l for l in lines if '[X]' in l and 'DENIED' in l])
        errors = len([l for l in lines if 'ERROR' in l])
        warnings = len([l for l in lines if 'WARNING' in l])
        traffic = len([l for l in lines if '🌐' in l or 'TRAFFIC' in l])

        print("LOG STATISTICS:")
        print(f"   Total lines: {total_lines}")
        print(f"   Auth requests: {auth_requests}")
        print(f"   ✅ Allowed: {allowed}")
        print(f"   [X] Denied: {denied}")
        print(f"   🌐 Traffic logs: {traffic}")
        print(f"   ⚠️  Warnings: {warnings}")
        print(f"   💥 Errors: {errors}")
        print()

    except Exception as e:
        print(f"[ERROR] Error reading stats: {e}")

def main():
    """Главная функция монитора"""
    clear_console()
    print_header()

    # Показать начальную статистику
    show_stats()

    print("\n" + "=" * 80)
    print("LIVE LOG STREAM (Press Ctrl+C to stop)")
    print("=" * 80)

    # Начать мониторинг
    monitor_log_file()

if __name__ == "__main__":
    main()