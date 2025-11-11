# UTAC Modular API - Production Dockerfile
#
# Multi-stage build for minimal image size
# Final image: ~600MB (Python + scientific stack)

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY api/requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user (security best practice)
RUN useradd -m -u 1000 utac && \
    mkdir -p /app && \
    chown -R utac:utac /app

# Set working directory
WORKDIR /app

# Copy application code
# (Assuming we're building from repo root)
COPY --chown=utac:utac api/ /app/api/
COPY --chown=utac:utac sonification/ /app/sonification/
COPY --chown=utac:utac models/ /app/models/
COPY --chown=utac:utac analysis/ /app/analysis/
COPY --chown=utac:utac data/ /app/data/
COPY --chown=utac:utac simulator/ /app/simulator/

# Switch to non-root user
USER utac

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run uvicorn
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
