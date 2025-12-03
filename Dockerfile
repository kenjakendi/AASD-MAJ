FROM python:3.9-slim

# Metadane
LABEL maintainer="Team MAJ"
LABEL description="Animal Shelter Management System - Multi-Agent System"

# Ustaw workdir
WORKDIR /app

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements
COPY requirements.txt .

# Zainstaluj zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Utwórz katalog na logi
RUN mkdir -p /app/logs

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Domyślne polecenie
CMD ["python", "-u", "main.py"]

