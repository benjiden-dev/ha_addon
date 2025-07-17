FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh smarthq
RUN chown -R smarthq:smarthq /app
USER smarthq

# Expose port
EXPOSE 8080
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3\
    CMD python -cimportrequests; requests.get(http://localhost:8080/health') || exit 1

# Run the application
CMD [python", "main.py"] 