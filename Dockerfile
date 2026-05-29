# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set initial working directory
WORKDIR /code

# Install system dependencies and clean up apt cache to keep image lean
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages to leverage build cache
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining project files
COPY . /code/

# Set the final working directory to where manage.py is located
WORKDIR /code/src

# Expose port
EXPOSE 8000
