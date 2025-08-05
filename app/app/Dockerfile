# Dockerfile – builds the FastAPI API + `rembg` model
FROM python:3.12-slim

# System libs needed by `rembg` (ONNX runtime) and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Create app folder in container
WORKDIR /app

# 1️⃣ Copy only the Python requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 2️⃣ Copy the Python source (app folder)
COPY app ./app

# Expose the port that Render will assign at runtime
EXPOSE 10000

# Entry point – use the PORT that Render provides
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
