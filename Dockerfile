FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system-level dependencies and TTS tools
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
    pciutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r gaia && useradd -r -g gaia -m gaia

# Install Python packages (with full pinning where known)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir cmake && \
    CMAKE_ARGS="-DLLAMA_CUBLAS=OFF -DCMAKE_C_LINK_FLAGS=-pthread -DCMAKE_CXX_LINK_FLAGS=-pthread" \
    pip install --no-cache-dir \
        flask==2.3.3 \
        werkzeug==2.3.7 \
        markdown==3.4.4 \
        sentence-transformers>=2.2.2 \
        huggingface_hub>=0.17.0 \
        chromadb>=0.4.18 \
        langchain>=0.1.0 \
        langchain-community>=0.1.0 \
        langchain-huggingface>=0.0.10 \
        langchain-core>=0.1.0 \
        langchain-text-splitters==0.0.1 \
        llama-cpp-python>=0.2.18 \
        striprtf==0.0.23 \
        python-docx==0.8.11 \
        pyttsx3==2.90 \
        typing-extensions==4.7.1

# Copy full GAIA project into /app
COPY . /app

# Set permissions for non-root user
RUN chown -R gaia:gaia /app

# Environment variable defaults
ENV MODEL_PATH=/app/model.gguf \
    CODE_MODEL_PATH=/app/model-c.gguf \
    DATA_PATH=/app/projects/dnd-campaign/core-documentation \
    RAW_DATA_PATH=/app/projects/dnd-campaign/raw-data \
    OUTPUT_PATH=/app/projects/dnd-campaign/converted_raw \
    VECTOR_DB_PATH=/app/shared/chroma_db \
    PROJECTS_DIR=/app/shared \
    N_GPU_LAYERS=0 \
    N_BATCH=768 \
    N_CTX=8192 \
    N_THREADS=6 \
    PORT=7860 \
    FLASK_ENV=production \
    SKIP_TTS_SELECTION=true

# Switch to non-root user
USER gaia

# Health check to ensure web service is up
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:7860/ || exit 1

# Launch the GAIA web application via Python module path
CMD ["python", "-m", "app.web.web_app"]
