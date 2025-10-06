# Use Python 3.10.12 official image
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (to leverage caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
