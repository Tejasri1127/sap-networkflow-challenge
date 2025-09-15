FROM python:3.13-slim

WORKDIR /app
COPY . /app

# Install system + Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir click pandas dash plotly azure-storage-blob azure-identity tenacity \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add project to PYTHONPATH
ENV PYTHONPATH=/app

# Default command
CMD ["python", "-m", "networkflow.cli"]


# ✅ CMD: default to launching the dashboard
CMD ["dashboard"]
