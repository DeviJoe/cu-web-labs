FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/

# Create directory for database
RUN mkdir -p /app/data

# Expose port 5050
EXPOSE 5050

# Run the application
CMD ["python", "app.py"]
