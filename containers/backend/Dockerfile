FROM python:3.12-slim

ENV LANG C.UTF-8

WORKDIR /app

COPY containers/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend /app/backend

WORKDIR /app/backend

EXPOSE 9090
CMD uvicorn --host 0.0.0.0 --port 9090 --reload backend.asgi:application
