# Use an official lightweight Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for venv and Streamlit
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and upgrade pip
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

# Copy project files
COPY . .

# Install Python dependencies within the venv
RUN pip install -r requirements.txt
RUN pip install inference_sdk

# Run csv1.py during build
RUN python csv1.py

# Expose Streamlit port
EXPOSE 8501

# Run the app via Streamlit using the virtual environment
CMD ["streamlit", "run", "stream.py", "--server.address=0.0.0.0"]