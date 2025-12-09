# --- UIDT v3.5.6 Master Container ---
# Base Image: Python 3.10 Slim (Scientific Standard)
FROM python:3.10-slim

# Metadaten für wissenschaftliche Reproduzierbarkeit und Zitierbarkeit
LABEL maintainer="Philipp Rietz <badbugs.arts@gmail.com>"
LABEL description="Official verification container for UIDT v3.5.6 (Canonical Framework)"
LABEL version="3.5.6"
LABEL license="CC-BY-4.0"
LABEL doi="10.5281/zenodo.17835200"
LABEL org.opencontainers.image.source="https://github.com/badbugsarts-hue/UIDT-Framework-V3.2-Canonical"

# Umgebungsvariablen für Python (Performance & Logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Abhängigkeiten für numerische Bibliotheken (numpy/scipy build dependencies)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Requirements installieren (Caching-Layer nutzen)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Den gesamten Projektcode kopieren
COPY . .

# Sicherheit: Non-Root User erstellen
RUN useradd -m researcher
USER researcher

# Standardbefehl: Führt die kanonische Verifikation aus
# Hinweis: Passt zur Master-Class Struktur (src/verification/)
CMD ["python", "src/verification/UIDT-3.5-Verification.py"]