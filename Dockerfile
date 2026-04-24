# -------------------------------
# Builder Stage
# -------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt .
RUN pip install --upgrade pip

# Install torch CPU first
RUN pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Install remaining deps (Ensure opencv-python-headless is in requirements-prod.txt)
RUN pip install -r requirements-prod.txt

# -------------------------------
# Final Image Stage
# -------------------------------
FROM python:3.11-slim

# 1. Install System Dependencies for OpenCV, YOLO, and MSSQL
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libgl1-mesa-glx \
    curl \
    gnupg \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Microsoft ODBC Driver 17 for SQL Server (Required for your mssql-conn)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
# Forces headless mode for libraries that check for a display
ENV QT_QPA_PLATFORM=offscreen 

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
