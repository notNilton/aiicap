FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for opencv
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Set PYTHONPATH to include /app so imports work
ENV PYTHONPATH=/app

CMD ["python", "main.py"]
