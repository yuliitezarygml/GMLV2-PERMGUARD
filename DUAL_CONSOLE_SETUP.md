# 🖥️ Dual Console Setup для SwaWeb + PermGuard

## Обзор
Реализована система запуска с **двумя консолями**:
1. **Консоль 1**: Flask веб-сервер
2. **Консоль 2**: Real-time PermGuard мониторинг с детальными логами

## 🚀 Способы запуска

### 1. Python Launcher (Рекомендуется)
```bash
python launcher.py
```

### 2. Windows Batch Script
```bash
start_with_monitoring.bat
```

### 3. PowerShell Script
```powershell
.\start_with_monitoring.ps1
```

## 📊 Что вы увидите

### 🖥️ Консоль 1 - Flask Server
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
INFO:werkzeug:127.0.0.1 - - [13/Sep/2025 14:27:40] "GET /admin/traffic HTTP/1.1" 200 -
```

### 📈 Консоль 2 - PermGuard Monitor
```
================================================================================
🛡️  PERMGUARD REAL-TIME MONITOR
================================================================================
📅 Started at: 2025-09-13 14:32:15
📁 Log file: permguard_detailed.log
🔄 Monitoring... (Press Ctrl+C to stop)
================================================================================

[0001] 2025-09-13 14:32:15 [    INFO] permguard_detailed: === PERMGUARD INITIALIZATION ===
[0002] 2025-09-13 14:32:15 [    INFO] permguard_detailed: 🛡️ AUTH REQUEST: user=admin@swaweb.com action=admin::access resource=admin::dashboard
[0003] 2025-09-13 14:32:15 [    INFO] permguard_detailed: ✅ AUTH RESULT: admin@swaweb.com -> admin::access on admin::dashboard = ALLOWED (12.5ms)
[0004] 2025-09-13 14:32:16 [    INFO] permguard_detailed: 🌐 TRAFFIC: GET /admin/traffic -> 200 (89ms) user: admin@swaweb.com IP: 127.0.0.1
```

## 🎯 Что логируется в PermGuard

### 🔐 Авторизация
- ✅ Успешные авторизации
- ❌ Отклоненные запросы
- 🛡️ Детали запросов авторизации
- ⚡ Время выполнения

### 🌐 Веб-трафик
- 🔐 Доступ к админ панели
- 🌐 Все HTTP запросы (кроме статических файлов)
- 📊 Производительность запросов
- 👤 Пользовательская активность

### 🚨 Системные события
- ⚠️ Предупреждения
- ❌ Ошибки подключения
- 🔄 Переключение в fallback режим
- 🗑️ Очистка старых логов

## 🎨 Цветовое кодирование

| Тип лога | Цвет | Пример |
|----------|------|---------|
| ✅ Успех | Зеленый | AUTH RESULT: ALLOWED |
| ❌ Ошибка | Красный | ACCESS DENIED |
| ⚠️ Предупреждение | Желтый | Fallback mode |
| 🛡️ Авторизация | Голубой | AUTH REQUEST |
| 🌐 Трафик | Пурпурный | TRAFFIC |
| 🔐 Админ доступ | Синий жирный | ADMIN ACCESS |

## 📂 Структура файлов

```
swaweb/
├── launcher.py                    # Кросс-платформенный лаунчер
├── start_with_monitoring.bat      # Windows batch скрипт
├── start_with_monitoring.ps1      # PowerShell скрипт
├── permguard_monitor.py          # Real-time монитор логов
├── logging.conf                  # Конфигурация логирования
├── permguard_detailed.log        # Детальные логи (автосоздается)
└── app.log                       # Основные логи приложения
```

## ⚙️ Конфигурация логирования

### Уровни логирования
- **DEBUG**: Детальная информация (только в файл)
- **INFO**: Общая информация
- **WARNING**: Предупреждения
- **ERROR**: Ошибки

### Форматы логов
- **Консольный**: `14:32:15 [INFO] permguard_detailed: сообщение`
- **Файловый**: `2025-09-13 14:32:15 [INFO] permguard_detailed (permguard_auth.py:125): детальное сообщение`

## 🛠️ Настройка

### Изменить уровень логирования
В `permguard_auth.py`:
```python
# Для более детального логирования
console_handler.setLevel(logging.DEBUG)

# Для менее детального логирования
console_handler.setLevel(logging.WARNING)
```

### Изменить размер лога трафика
В `permguard_auth.py`:
```python
# Увеличить лимит записей в памяти
if len(self.traffic_log) > 2000:  # Было 1000
    self.traffic_log.pop(0)
```

## 🎯 Использование

1. **Запустите систему**:
   ```bash
   python launcher.py
   ```

2. **Откройте браузер**:
   - Главная: http://localhost:5000
   - Админ: http://localhost:5000/admin
   - Трафик: http://localhost:5000/admin/traffic

3. **Наблюдайте логи в реальном времени** во второй консоли

4. **Остановите мониторинг**: `Ctrl+C` во второй консоли

## 🔍 Отладка

### Если логи не появляются:
1. Проверьте, что файл `permguard_detailed.log` создается
2. Убедитесь, что уровень логирования не слишком высокий
3. Проверьте права доступа к файлам

### Если консоли не открываются:
1. Проверьте наличие Python в PATH
2. Убедитесь, что все файлы на месте
3. Запустите `python launcher.py` вручную для диагностики

## 💡 Советы

- **Используйте фильтры** в `/admin/traffic` для поиска конкретных событий
- **Проверяйте файл логов** `permguard_detailed.log` для полной истории
- **Мониторьте ошибки** по красным сообщениям в логах
- **Следите за производительностью** по времени выполнения запросов

---

## ✅ Система готова!

Теперь у вас есть полноценная система мониторинга с двумя консолями:
- 🖥️ **Сервер работает** в одной консоли
- 📊 **Логи PermGuard** отображаются в реальном времени в другой
- 🌐 **Веб-интерфейс** доступен для детального анализа трафика

**Запускайте и наслаждайтесь полным контролем над системой!** 🎉