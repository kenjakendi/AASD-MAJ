# Dashboard Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy only visualization requirements first (not main requirements.txt)
COPY visualization/requirements.txt /app/visualization/requirements.txt

# Install dashboard dependencies
RUN pip install --no-cache-dir -r visualization/requirements.txt

# Copy application files
COPY visualization/ /app/visualization/
COPY config/ /app/config/
COPY utils/ /app/utils/
COPY models/ /app/models/
COPY agents/ /app/agents/

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# Run dashboard
CMD ["python", "-u", "visualization/dashboard_main.py", "--host", "0.0.0.0", "--port", "5000"]

