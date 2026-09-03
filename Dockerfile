FROM python:3.10-slim

WORKDIR /app

# Install essential system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Grant execution permissions to startup script
RUN chmod +x startup.sh

# Expose Streamlit frontend port
EXPOSE 7860

# Execute container startup script
CMD ["/bin/bash", "startup.sh"]
