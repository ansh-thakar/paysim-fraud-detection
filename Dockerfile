FROM python:3.10-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and model artifacts
COPY artifacts/ ./artifacts/
COPY api/ ./api/
COPY frontend/ ./frontend/
COPY start.sh .

# Format script permissions and line endings
RUN dos2unix start.sh && chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]