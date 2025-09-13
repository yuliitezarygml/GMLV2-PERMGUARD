#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации улучшенного монитора PermGuard
"""

import time
import requests
import threading

def generate_test_traffic():
    """Генерирует тестовый трафик для демонстрации мониторинга"""
    base_url = "http://localhost:5001"

    test_urls = [
        "/",
        "/api/game_stats",
        "/admin/traffic",
        "/gamelist",
        "/about",
        "/premium",
        "/api/admin/traffic/stats",
        "/api/admin/traffic/logs",
    ]

    print("🚀 Начинаем генерацию тестового трафика...")
    print("📊 Проверьте монитор PermGuard для просмотра логов в реальном времени!")
    print("=" * 60)

    for i, url in enumerate(test_urls):
        try:
            print(f"[{i+1:02d}/08] Запрос: {url}")
            response = requests.get(base_url + url, timeout=5)
            print(f"         Ответ: {response.status_code}")

            # Пауза между запросами для лучшей видимости в мониторе
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"         Ошибка: {e}")

        except Exception as e:
            print(f"         Неожиданная ошибка: {e}")

    print("=" * 60)
    print("✅ Генерация трафика завершена!")
    print("📋 Проверьте монитор PermGuard - вы должны видеть все запросы!")

def continuous_traffic():
    """Генерирует непрерывный трафик для длительного тестирования"""
    base_url = "http://localhost:5001"
    urls = ["/", "/api/game_stats", "/admin/traffic"]

    print("🔄 Запуск непрерывной генерации трафика...")
    print("   Нажмите Ctrl+C для остановки")

    try:
        counter = 1
        while True:
            for url in urls:
                try:
                    response = requests.get(base_url + url, timeout=2)
                    print(f"[{counter:04d}] {url} -> {response.status_code}")
                    counter += 1
                    time.sleep(3)
                except:
                    pass
    except KeyboardInterrupt:
        print("\n⏹️  Генерация трафика остановлена пользователем")

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("🛡️  ТЕСТИРОВАНИЕ МОНИТОРА PERMGUARD")
    print("=" * 60)
    print()
    print("Выберите режим тестирования:")
    print("1. Одноразовая генерация трафика (8 запросов)")
    print("2. Непрерывная генерация трафика")
    print("3. Выход")
    print()

    try:
        choice = input("Ваш выбор (1-3): ").strip()

        if choice == "1":
            generate_test_traffic()
        elif choice == "2":
            continuous_traffic()
        elif choice == "3":
            print("👋 До свидания!")
        else:
            print("❌ Неверный выбор. Используйте 1, 2 или 3.")

    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")