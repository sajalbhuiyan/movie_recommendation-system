# Base image with Python 3.9
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for building scikit-surprise
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Default command to run your app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
