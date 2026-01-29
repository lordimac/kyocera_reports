FROM python:3.9-slim

WORKDIR /app

# Create data directory with proper permissions
RUN mkdir -p data && chmod 777 data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]