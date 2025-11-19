FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY app.py .
COPY templates/ templates/

# Копируем флаг в корень контейнера и в /app
COPY flag.txt /flag.txt
COPY flag.txt /app/flag.txt

# Создаем непривилегированного пользователя для безопасности
RUN useradd -m -u 1000 ctfuser && \
    chown -R ctfuser:ctfuser /app

# Запускаем от имени непривилегированного пользователя
USER ctfuser

# Открываем порт
EXPOSE 5000

# Переменные окружения
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Запускаем приложение
CMD ["python", "app.py"]
