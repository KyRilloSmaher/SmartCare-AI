# -------------------------------
# Builder
# -------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt .

RUN pip install --upgrade pip

# install torch CPU
RUN pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu

# install remaining deps
RUN pip install -r requirements.txt

# -------------------------------
# Final image
# -------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp/hf_cache

WORKDIR /app

# copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy app
COPY . .

EXPOSE 8080

CMD ["python", "run.py"]
