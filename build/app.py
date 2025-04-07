import json
import os
import subprocess
import tempfile
import logging
import sys
from flask import Flask, jsonify

app = Flask(__name__)

# Logging konfigurieren
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ENV-Variablen einlesen
username = os.getenv('CARCONNECTIVITY_USERNAME')
password = os.getenv('CARCONNECTIVITY_PASSWORD')
vin = os.getenv('CARCONNECTIVITY_VIN')

if not all([username, password, vin]):
    logging.error("Die Umgebungsvariablen CARCONNECTIVITY_USERNAME, CARCONNECTIVITY_PASSWORD und CARCONNECTIVITY_VIN müssen gesetzt sein.")
    sys.exit(1)

# Erstelle das JSON-Konfigurations-Dictionary
config_data = {
    "carConnectivity": {
        "connectors": [
            {
                "type": "volkswagen",
                "config": {
                    "username": username,
                    "password": password
                }
            }
        ]
    }
}

# Schreibe die JSON-Konfiguration in eine temporäre Datei
try:
    temp_config = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_test.json")
    json.dump(config_data, temp_config)
    temp_config.close()
    config_filepath = temp_config.name
    logging.info("Konfigurationsdatei erstellt: %s", config_filepath)
except Exception as e:
    logging.error("Fehler beim Erstellen der Konfigurationsdatei: %s", e)
    sys.exit(1)

def run_carconnectivity_cli(command_value):
    """
    Führt den carconnectivity-cli-Befehl aus.
    Beispiel: carconnectivity-cli <config_filepath> set /garage/<vin>/climatization/commands/start-stop start
    """
    cli_command = [
        "carconnectivity-cli",
        config_filepath,
        "set",
        f"/garage/{vin}/climatization/commands/start-stop",
        command_value
    ]
    try:
        result = subprocess.run(cli_command, capture_output=True, text=True, check=True)
        logging.info("Befehl erfolgreich ausgeführt: %s", " ".join(cli_command))
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error("Fehler beim Ausführen von %s: %s", " ".join(cli_command), e.stderr)
        return None

@app.route('/climatization/start', methods=['POST'])
def start_climatization():
    """Startet die Klimatisierung des Fahrzeugs."""
    output = run_carconnectivity_cli("start")
    if output is not None:
        return jsonify({"status": "starting", "output": output})
    return jsonify({"error": "Fehler beim Starten der Klimatisierung"}), 500

@app.route('/climatization/stop', methods=['POST'])
def stop_climatization():
    """Stoppt die Klimatisierung des Fahrzeugs."""
    output = run_carconnectivity_cli("stop")
    if output is not None:
        return jsonify({"status": "stopping", "output": output})
    return jsonify({"error": "Fehler beim Stoppen der Klimatisierung"}), 500