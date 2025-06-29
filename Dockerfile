FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /gaia-assistant

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
    libopenblas-dev \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Optional: ensure recent CMake
RUN curl -sSL https://github.com/Kitware/CMake/releases/download/v3.27.7/cmake-3.27.7-linux-x86_64.sh -o cmake.sh \
    && chmod +x cmake.sh && ./cmake.sh --skip-license --prefix=/usr/local


# Copy core files
COPY ./app ./app
COPY ./main.py .
COPY ./runserver.py .
COPY ./requirements.txt .
COPY ./gaia_rescue.py .

# Install SQLite 3.45.1 (latest as of now)
RUN apt-get update && apt-get install -y wget build-essential \
 && wget https://www.sqlite.org/2024/sqlite-autoconf-3450100.tar.gz \
 && tar -xzf sqlite-autoconf-3450100.tar.gz \
 && cd sqlite-autoconf-3450100 \
 && ./configure --prefix=/usr/local \
 && make -j$(nproc) && make install \
 && ldconfig \
 && cd .. && rm -rf sqlite-autoconf-3450100*

# Install llama-cpp-python (latest, from source)
ENV LLAMA_CUBLAS=0
RUN pip install --no-cache-dir --force-reinstall --upgrade llama-cpp-python

ENV PYTHONPATH=/gaia-assistant
RUN pip install --no-cache-dir --upgrade pip setuptools

# Install Python packages with llama-cpp build flags
RUN pip install --no-cache-dir cmake && \
    CMAKE_ARGS="-DLLAMA_CUBLAS=OFF -DCMAKE_C_LINK_FLAGS=-pthread -DCMAKE_CXX_LINK_FLAGS=-pthread" \
    pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir llama-index-readers-file

# Default command: run Flask server
CMD ["python", "runserver.py"]
