FROM python:3.11-slim

WORKDIR /app

# Install system dependencies in a single layer to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libpthread-stubs0-dev \
    curl \
    libespeak1 \
    espeak \
    espeak-data \
    libportaudio2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -r gaia && useradd -r -g gaia -m gaia

# Upgrade pip and install Python dependencies with version pinning
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir cmake && \
    CMAKE_ARGS="-DLLAMA_CUBLAS=OFF -DCMAKE_C_LINK_FLAGS=-pthread -DCMAKE_CXX_LINK_FLAGS=-pthread" \
    pip install --no-cache-dir \
        markdown==3.4.4 \
        sentence-transformers>=2.2.2 \
        huggingface_hub>=0.17.0 \
        chromadb>=0.4.18 \
        langchain>=0.1.0 \
        langchain-community>=0.1.0 \
        langchain-huggingface>=0.0.10 \
        langchain-core>=0.1.0 \
        langchain-text-splitters==0.0.1 \
        huggingface_hub>=0.17.0 \
        llama-cpp-python>=0.2.18 \
        striprtf==0.0.23 \
        python-docx==0.8.11 \
        pyttsx3==2.90 \
        typing-extensions==4.7.1 \
        flask==2.3.3 \
        werkzeug==2.3.7

# Create necessary directories
RUN mkdir -p /app/campaign-data/core-documentation \
             /app/campaign-data/converted_raw \
             /app/campaign-data/raw-data \
             /app/chroma_db \
             /app/logs \
             /app/app \
             /app/app/models \
             /app/app/utils \
             /app/app/web \
             /app/static \
             /app/templates

# Copy application files
COPY app /app/app/
COPY main.py web_app.py /app/
COPY gaia_instructions.txt /app/
COPY templates /app/templates
COPY static /app/static

# Set permissions
RUN chown -R gaia:gaia /app

# Set environment variables with defaults
ENV MODEL_PATH=/app/model.gguf \
    DATA_PATH=/app/campaign-data/core-documentation \
    RAW_DATA_PATH=/app/campaign-data/raw-data \
    OUTPUT_PATH=/app/campaign-data/converted_raw \
    VECTOR_DB_PATH=/app/chroma_db \
    CORE_INSTRUCTIONS_FILE=/app/gaia_instructions.txt \
    N_GPU_LAYERS=0 \
    N_BATCH=512 \
    N_CTX=2048 \
    N_THREADS=6 \
    PORT=7860 \
    FLASK_ENV=production \
    SKIP_TTS_SELECTION=true

# Switch to non-root user
USER gaia

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:7860/ || exit 1

# Set the entrypoint
CMD ["python", "web_app.py"]