# -------------------------------
# Builder
# -------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-prod.txt .

RUN pip install --upgrade pip

# install torch CPU
RUN pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cpu

# Install opencv-headless first to prevent ultralytics from installing full opencv
RUN pip install opencv-python-headless==4.9.0.80

# install remaining deps
RUN pip install -r requirements-prod.txt

# -------------------------------
# Final image
# -------------------------------
FROM python:3.11-slim

# Install runtime system dependencies for OpenCV headless
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV OPENCV_OPENCL_RUNTIME=

WORKDIR /app

# copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy app
COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
