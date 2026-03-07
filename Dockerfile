# -------------------------------
# Base image
# -------------------------------
FROM python:3.11-slim

# -------------------------------
# Environment settings
# -------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# -------------------------------
# System dependencies
# -------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    git \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Work directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Install Python dependencies
# -------------------------------
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# -------------------------------
# Copy project
# -------------------------------
COPY . .

# -------------------------------
# Port (Fly/Railway detect it)
# -------------------------------
EXPOSE 8080

# -------------------------------
# Run API
# -------------------------------
CMD ["python", "run.py"]
