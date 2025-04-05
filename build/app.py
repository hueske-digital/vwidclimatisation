import json
import os
import subprocess
import tempfile
from flask import Flask, jsonify

app = Flask(__name__)

username = os.getenv('CARCONNECTIVITY_USERNAME')
password = os.getenv('CARCONNECTIVITY_PASSWORD')
vin = os.getenv('CARCONNECTIVITY_VIN')

if not all([username, password, vin]):
    raise Exception("CARCONNECTIVITY_USERNAME, CARCONNECTIVITY_PASSWORD und CARCONNECTIVITY_VIN müssen gesetzt sein.")

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

temp_config = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_mycarconnectivity_config.json")
json.dump(config_data, temp_config)
temp_config.close()
config_filepath = temp_config.name

def run_carconnectivity_cli(command_path, command_value):
    """
    Führt den carconnectivity-cli-Befehl mit dem erstellten JSON-Config aus.
    Beispiel-Aufruf:
      carconnectivity-cli <config_filepath> /garage/<vin>/climatisation/command stop
    """
    cli_command = [
        "carconnectivity-cli",
        config_filepath,
        f"/garage/{vin}/climatisation/command",
        command_value
    ]
    result = subprocess.run(cli_command, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return None

@app.route('/climatisation/start', methods=['POST'])
def start_climatisation():
    """Startet die Klimatisierung des Fahrzeugs."""
    output = run_carconnectivity_cli(f"/garage/{vin}/climatisation/command", "start")
    if output is not None:
        return jsonify({"status": "starting", "output": output})
    return jsonify({"error": "Fehler beim Starten der Klimatisierung"}), 500

@app.route('/climatisation/stop', methods=['POST'])
def stop_climatisation():
    """Stoppt die Klimatisierung des Fahrzeugs."""
    output = run_carconnectivity_cli(f"/garage/{vin}/climatisation/command", "stop")
    if output is not None:
        return jsonify({"status": "stopping", "output": output})
    return jsonify({"error": "Fehler beim Stoppen der Klimatisierung"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')