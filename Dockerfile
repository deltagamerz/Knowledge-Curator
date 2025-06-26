# Dockerfile

# 1. Start with an official Python base image.
# Using 'slim' makes our final container smaller and more efficient.
FROM python:3.11-slim

# 2. Set a working directory inside the container.
# This is where our code will live.
WORKDIR /app

# 3. Copy the requirements file into the container first.
COPY requirements.txt .

# 4. Install the Python dependencies.
# We run this before copying the rest of our code. This is a caching optimization.
# If we don't change our requirements, Docker won't re-run this slow step.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of our application code into the container.
COPY . .

# 6. Define the command that will run when the container starts.
# This is the command our Render Cron Job will execute.
CMD ["python", "main.py"]