# Use an official Python base image
FROM python:3.11-slim

# Install the system dependencies required for pycairo
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libcairo2-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy your files and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Set the startup command
CMD ["python", "stt.py"]