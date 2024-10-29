from flask import Flask, jsonify
import subprocess
import os
from threading import Thread

app = Flask(__name__)

# Environment variables for WeConnect login
username = os.getenv('WECONNECT_USERNAME')
password = os.getenv('WECONNECT_PASSWORD')
vin = os.getenv('WECONNECT_VIN')

def run_weconnect_cli(action, path, command=None):
    """
    Run weconnect-cli with a specified action ('get' or 'set') on a specific path.
    If 'set' is the action, a command must be provided.
    """
    cli_command = ["weconnect-cli", "--username", username, "--password", password, action, path]
    if command:
        cli_command.append(command)

    result = subprocess.run(cli_command, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None

@app.route('/climatisation/start', methods=['POST'])
def start_climatisation():
    """Start the vehicle's climate control."""
    thread = Thread(target=run_weconnect_cli, args=("set", f"/vehicles/{vin}/controls/climatisation", "start"))
    thread.start()
    return {"status": "starting"}

@app.route('/climatisation/stop', methods=['POST'])
def stop_climatisation():
    """Stop the vehicle's climate control."""
    thread = Thread(target=run_weconnect_cli, args=("set", f"/vehicles/{vin}/controls/climatisation", "stop"))
    thread.start()
    return {"status": "stopping"}

@app.route('/range', methods=['GET'])
def get_range():
    """Get the vehicle's cruising range in kilometers, returned as an integer."""
    path = f"/vehicles/{vin}/domains/charging/batteryStatus/cruisingRangeElectric_km"
    range_km = run_weconnect_cli("get", path)
    try:
        range_km_int = int(float(range_km))  # Convert to float first to handle decimals, then to int
        return jsonify({"cruisingRangeElectric_km": range_km_int})
    except (ValueError, TypeError):
        return jsonify({"error": "Unable to fetch cruising range as an integer"}), 500

@app.route('/soc', methods=['GET'])
def get_soc():
    """Get the vehicle's current state of charge (SOC) percentage, returned as an integer."""
    path = f"/vehicles/{vin}/domains/charging/batteryStatus/currentSOC_pct"
    soc_pct = run_weconnect_cli("get", path)
    try:
        soc_pct_int = int(float(soc_pct))  # Convert to float first to handle decimals, then to int
        return jsonify({"currentSOC_pct": soc_pct_int})
    except (ValueError, TypeError):
        return jsonify({"error": "Unable to fetch state of charge as an integer"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')