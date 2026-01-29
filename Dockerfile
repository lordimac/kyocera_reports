FROM python:3.9-slim

WORKDIR /app

# Create data directory with proper permissions
RUN mkdir -p data && chmod 777 data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Use Gunicorn for production with background scheduler
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]