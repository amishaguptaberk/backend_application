# ---------- build stage ----------
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    BASE_URL=https://your-domain-or-cloudrun-url

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy your application code
COPY app/ app/

# Expose the correct port for Cloud Run
EXPOSE 8080

# Start the FastAPI app on port 8080, bind to 0.0.0.0
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
