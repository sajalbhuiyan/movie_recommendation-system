# -----------------------------
# 1) Use Python 3.9 base image
# -----------------------------
FROM python:3.9-slim

# -----------------------------
# 2) Set working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# 3) Install system dependencies for building Python packages
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 4) Copy requirements first (for caching)
# -----------------------------
COPY requirements.txt .

# -----------------------------
# 5) Upgrade pip and install Python dependencies
# -----------------------------
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 6) Copy the rest of the app
# -----------------------------
COPY . .

# -----------------------------
# 7) Expose the port your app runs on
# -----------------------------
EXPOSE 8501

# -----------------------------
# 8) Start your app
# -----------------------------
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
