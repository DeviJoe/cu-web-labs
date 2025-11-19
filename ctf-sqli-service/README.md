# CTF SQL Injection Challenge Service

Сервис для студенческого CTF с уязвимостью Blind SQL Injection и защитой WAF.

## Описание

Это веб-приложение для поиска пользователей по ID, которое содержит уязвимость Blind SQL Injection. Приложение защищено простым Web Application Firewall (WAF), который блокирует распространенные SQL injection паттерны.

**Задача участников**: найти и эксплуатировать уязвимость для получения флага формата `centralctf{...}`

## Требования

- Docker
- Docker Compose

## Быстрый запуск

### Вариант 1: Docker Compose (рекомендуется)

```bash
cd ctf-sqli-service
docker-compose up -d
```

Сервис будет доступен по адресу: `http://localhost:5050`

### Вариант 2: Docker напрямую

```bash
cd ctf-sqli-service

# Сборка образа
docker build -t ctf-sqli-service .

# Запуск контейнера
docker run -d -p 5050:5050 --name ctf-sqli ctf-sqli-service
```

## Проверка работы

```bash
# Проверка healthcheck
curl http://localhost:5050/health

# Открыть в браузере
open http://localhost:5050
```

## Управление сервисом

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

### Просмотр логов
```bash
docker-compose logs -f
```

### Полная очистка (включая данные)
```bash
docker-compose down -v
rm -rf data/
```

## Структура проекта

```
ctf-sqli-service/
├── app.py                  # Основное Flask приложение
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose конфигурация
├── templates/
│   ├── index.html        # Главная страница
│   └── search.html       # Страница результатов поиска
├── SOLUTION.md           # ⚠️ РЕШЕНИЕ (не показывать участникам!)
└── README.md             # Этот файл
```

## Функциональность

- **Главная страница** (`/`): Форма для поиска пользователей
- **Поиск** (`/search?id=X`): Поиск пользователя по ID
- **Health check** (`/health`): Проверка работоспособности сервиса

## Доступные пользователи

В базе данных есть следующие тестовые пользователи:
- ID 1: alice
- ID 2: bob
- ID 3: charlie
- ID 4: david

## Подсказки для участников (опционально)

Если участники застряли, можно дать следующие подсказки:

1. **Уровень 1**: "Попробуйте разные значения параметра `id`"
2. **Уровень 2**: "Приложение защищено WAF. Как можно обойти фильтры?"
3. **Уровень 3**: "URL encoding может помочь обойти некоторые фильтры"
4. **Уровень 4**: "Это Blind SQL Injection - ищите способы задавать вопросы типа да/нет"

## Для организаторов

⚠️ **ВАЖНО**: Файл `SOLUTION.md` содержит полное решение с флагом и эксплойтами. 
**НЕ ПУБЛИКУЙТЕ** его вместе с челленджем!

### Смена флага

Чтобы изменить флаг, отредактируйте строку в `app.py`:

```python
cursor.execute("""
    INSERT INTO secrets (id, secret_key, secret_value)
    VALUES (1, 'flag', 'centralctf{ваш_новый_флаг}')
""")
```

После изменения пересоберите контейнер:
```bash
docker-compose down
docker-compose up -d --build
```

## Безопасность

Этот сервис **намеренно уязвим** для образовательных целей. 

⚠️ **НЕ ИСПОЛЬЗУЙТЕ** в продакшене или на публичных серверах без надлежащей изоляции!

## Рекомендации по развертыванию на CTF

1. Используйте изолированную сеть Docker
2. Ограничьте rate limiting на уровне nginx/reverse proxy
3. Используйте отдельный инстанс для каждой команды (если требуется)
4. Мониторьте логи на предмет DoS атак
5. Установите лимиты ресурсов контейнера:

```yaml
services:
  ctf-sqli:
    # ... остальная конфигурация
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

## Сложность

- **Категория**: Web Security
- **Сложность**: Medium/Hard
- **Навыки**: SQL Injection, WAF Bypass, Blind SQLi techniques
- **Время решения**: 30-60 минут (опытный участник)

## Лицензия

Для образовательных целей. Свободное использование.

## Поддержка

При возникновении проблем проверьте:
1. Порт 5050 свободен: `netstat -an | grep 5050`
2. Docker работает: `docker ps`
3. Логи контейнера: `docker-compose logs`
