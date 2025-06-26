# backend/Dockerfile

# 1. Start with an official Python base image.
FROM python:3.11-slim

# 2. Set environment variables to make Python run smoothly in Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set a working directory inside the container.
WORKDIR /app

# Copy the requirements file from the backend folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code from the backend/app subfolder
COPY backend/app /app/app

# 6. Expose the port the app will run on.
# FastAPI/uvicorn runs on port 8000 by default.
EXPOSE 8000

# 7. Define the command to run the web server.
# This starts the Uvicorn server, pointing to the 'app' object inside our 'main.py' file.
# The host '0.0.0.0' is important to make it accessible from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]