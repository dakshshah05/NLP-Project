FROM python:3.11-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install python packages
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download spaCy English model to speed up container boot
RUN python -m spacy download en_core_web_sm || true

# Copy all repository contents
COPY . .

# Hugging Face Spaces exposes port 7860 by default for container deployments
EXPOSE 7860

# Launch FastAPI app with Uvicorn
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
