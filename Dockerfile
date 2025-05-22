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
COPY --from=builder /install /usr/local
COPY app app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]