# Use Ubuntu 22.04 as base image for better compiler support
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    wget \
    git \
    ca-certificates \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    libtool \
    make \
    pkg-config \
    libprotobuf-dev \
    protobuf-compiler \
    libnl-3-dev \
    libnl-route-3-dev \
    uthash-dev \
    && rm -rf /var/lib/apt/lists/*

# Install nsjail for sandboxing (pinned to version 3.4)
RUN git clone --depth 1 --branch 3.4 https://github.com/google/nsjail.git /tmp/nsjail && \
    cd /tmp/nsjail && \
    make && \
    cp nsjail /usr/local/bin/ && \
    rm -rf /tmp/nsjail

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python3", "app.py"] 