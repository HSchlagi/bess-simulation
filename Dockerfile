# BESS-Simulation Docker Container
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Pakete aktualisieren und installieren
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Port freigeben
EXPOSE 5000

# Umgebungsvariablen setzen
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Datenbank-Verzeichnis erstellen
RUN mkdir -p /app/instance

# Berechtigungen setzen
RUN chmod +x /app/run.py

# Health-Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/performance/health || exit 1

# Anwendung starten
CMD ["python", "run.py"]
