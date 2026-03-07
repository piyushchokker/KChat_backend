FROM python:3.10-slim

# System dependencies for unstructured, tesseract, and PDF/image processing
RUN apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Copy .env if you use it (optional, for local dev)
# COPY .env .env

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI and worker
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & python -m app.services.rag "]