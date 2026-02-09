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

# Copy image generator code
COPY apps/image_generator /app/apps/image_generator

# Install image generator dependencies
RUN pip install -e /app/apps/image_generator

WORKDIR /app/apps/image_generator

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
