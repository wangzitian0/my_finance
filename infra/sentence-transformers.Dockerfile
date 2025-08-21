FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Install Python ML dependencies
RUN pip install --no-cache-dir \
    sentence-transformers==5.1.0 \
    torch==2.2.2 \
    numpy==1.26.4 \
    scikit-learn==1.3.0 \
    faiss-cpu==1.9.0 \
    transformers \
    tqdm

# Create service user
RUN useradd -m -u 1000 ml-service
USER ml-service

# Create Python service script
COPY --chown=ml-service:ml-service sentence_transformers_service.py /app/

# Expose port for service
EXPOSE 8888

# Start the service
CMD ["python", "sentence_transformers_service.py"]