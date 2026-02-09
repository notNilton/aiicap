FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY packages/shared /app/packages/shared

# Install shared package
RUN pip install -e /app/packages/shared

# Copy backend code
COPY apps/backend /app/apps/backend

# Install backend dependencies
RUN pip install -e /app/apps/backend

WORKDIR /app/apps/backend

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
