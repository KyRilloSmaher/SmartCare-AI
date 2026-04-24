# -------------------------------
# Builder
# -------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt .

RUN pip install --upgrade pip

# install torch CPU separately
RUN pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --prefix=/install -r requirements-prod.txt

# -------------------------------
# Final image
# -------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp/hf_cache

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8080

CMD ["python", "run.py"]
