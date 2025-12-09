# Dockerfile für UIDT v3.5.6 Reproduzierbarkeit
FROM python:3.10-slim

# Metadaten
LABEL maintainer="Philipp Rietz <badbugs.arts@gmail.com>"
LABEL description="Official container for UIDT v3.5.6 verification simulations"
LABEL version="3.5.6"

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Abhängigkeiten für wissenschaftliche Berechnungen
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten Code
COPY . .

# Standardbefehl: Führe die Verifikation aus
CMD ["python", "UIDT-3.5-Verification.py"]
