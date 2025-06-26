# worker/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker/ .
CMD ["python", "daily_job.py"]