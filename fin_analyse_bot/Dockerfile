# Stage 1 - Build

FROM python:3.11-slim-bullseye AS builder
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix="/usr/src/app" -r requirements.txt

# Stage 2 - Runtime

FROM python:3.11-slim-bullseye AS runtime
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app /usr/local
COPY . .
CMD ["python", "main.py"]