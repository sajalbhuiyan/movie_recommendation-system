# -----------------------------
# Dockerfile for Movie Recommendation System
# -----------------------------

# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Set Streamlit config to allow running inside Docker
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the app
CMD ["streamlit", "run", "app.py"]
