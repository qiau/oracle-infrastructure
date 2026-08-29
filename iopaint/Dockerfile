FROM python:3.11-slim

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libjpeg62-turbo \
        libgomp1 \
        curl \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only PyTorch
RUN pip install --no-cache-dir \
    torch==2.4.1 \
    torchvision==0.19.1 \
    --index-url https://download.pytorch.org/whl/cpu

# IOPaint
RUN pip install --no-cache-dir iopaint

# Download LaMa model into the Docker image
RUN iopaint download --model lama

EXPOSE 8083

CMD ["iopaint", "start", \
     "--model=lama", \
     "--device=cpu", \
     "--host=0.0.0.0", \
     "--port=8083"]