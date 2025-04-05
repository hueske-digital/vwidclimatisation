# Nutze das offizielle Python-Image als Basis
FROM python:3-slim

# Setzen Sie das Arbeitsverzeichnis im Container
WORKDIR /app

# Installiere curl für Debugging
RUN apt-get update && apt-get install -y curl
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Installation der Abhängigkeiten
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Anwendung ins Arbeitsverzeichnis kopieren
COPY app.py .

# Starten der Anwendung
CMD ["python", "./app.py"]
