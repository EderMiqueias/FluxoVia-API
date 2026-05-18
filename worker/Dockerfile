FROM python:3.11-slim

WORKDIR /app

COPY worker/requirements.txt .
RUN pip install --no-cache-dir pika==1.3.2 requests==2.31.0 python-dotenv==1.0.1

COPY worker/worker.py .

CMD ["python", "worker.py"]
