# Use official Python base image
FROM --platform=linux/amd64 python:3.10-slim

# Set work directory
WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model directories and script
COPY script.py .
COPY SummarizerModel/ ./SummarizerModel/
COPY SentenceTransformerModel/ ./SentenceTransformerModel/

# Create input/output directories
RUN mkdir -p /app/PDFs

# Copy input.json
COPY /input/input.json .

# Define default command
CMD ["python", "script.py"]
