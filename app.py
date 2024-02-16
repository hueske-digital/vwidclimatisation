from flask import Flask
import subprocess
import os
from threading import Thread

app = Flask(__name__)

username = os.getenv('WECONNECT_USERNAME')
password = os.getenv('WECONNECT_PASSWORD')
vin = os.getenv('WECONNECT_VIN')

def run_weconnect_cli(command):
    subprocess.run(["weconnect-cli", "--username", username, "--password", password, "set", f"/vehicles/{vin}/controls/climatisation", command])

@app.route('/climatisation/start', methods=['POST'])
def start_climatisation():
    thread = Thread(target=run_weconnect_cli, args=("start",))
    thread.start()
    return {"status": "starting"}

@app.route('/climatisation/stop', methods=['POST'])
def stop_climatisation():
    thread = Thread(target=run_weconnect_cli, args=("stop",))
    thread.start()
    return {"status": "stopping"}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
