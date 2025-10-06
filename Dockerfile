# Use official Python image (3.10 is fine)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
