import json
import os
import subprocess
import tempfile
from flask import Flask, jsonify

app = Flask(__name__)

# ENV-Variablen einlesen
username = os.getenv('CARCONNECTIVITY_USERNAME')
password = os.getenv('CARCONNECTIVITY_PASSWORD')
vin = os.getenv('CARCONNECTIVITY_VIN')

if not all([username, password, vin]):
    raise Exception("CARCONNECTIVITY_USERNAME, CARCONNECTIVITY_PASSWORD und CARCONNECTIVITY_VIN müssen gesetzt sein.")

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
temp_config = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_test.json")
json.dump(config_data, temp_config)
temp_config.close()
config_filepath = temp_config.name

def run_carconnectivity_cli(command_value):
    """
    Führt den carconnectivity-cli-Befehl aus, wobei der Pfad und das Kommando (start/stop)
    dynamisch anhand der ENV-Variablen gesetzt werden.
    Beispiel:
      carconnectivity-cli <config_filepath> set /garage/<vin>/climatization/commands/start-stop start
    """
    cli_command = [
        "carconnectivity-cli",
        config_filepath,
        "set",
        f"/garage/{vin}/climatization/commands/start-stop",
        command_value
    ]
    result = subprocess.run(cli_command, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')