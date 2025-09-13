#!/usr/bin/env python3
"""Остановить все Python процессы"""

import os
import sys
import psutil
import signal

def stop_all_python_processes():
    """Остановить все Python процессы кроме текущего"""
    current_pid = os.getpid()
    stopped_count = 0

    print("[SEARCH] Поиск Python процессов...")

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_info = proc.info
            if proc_info['name'] and 'python' in proc_info['name'].lower():
                if proc_info['pid'] != current_pid:
                    try:
                        print(f"[STOP] Остановка процесса: PID {proc_info['pid']}")
                        if proc_info['cmdline']:
                            print(f"       Команда: {' '.join(proc_info['cmdline'][:3])}")

                        # Попытка мягкого завершения
                        proc.terminate()

                        # Ждем 3 секунды, затем принудительное завершение
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            print(f"       Принудительное завершение PID {proc_info['pid']}")
                            proc.kill()

                        stopped_count += 1

                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        print(f"       [WARN] Не удалось остановить PID {proc_info['pid']}: {e}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue

    print(f"\n[OK] Остановлено процессов: {stopped_count}")
    return stopped_count

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("ОСТАНОВКА ВСЕХ PYTHON ПРОЦЕССОВ")
        print("=" * 50)

        count = stop_all_python_processes()

        if count > 0:
            print(f"\n[SUCCESS] Успешно остановлено {count} процессов Python")
        else:
            print("\n[INFO] Активных Python процессов не найдено")

    except KeyboardInterrupt:
        print("\n\n[WARN] Прервано пользователем")

    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")

    finally:
        print("\n[EXIT] Завершение работы...")