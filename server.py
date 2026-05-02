from flask import Flask
import threading
import subprocess
import time

app = Flask(__name__)

def run_oci_script():
    while True:
        try:
            subprocess.run(["python", "main.py"])
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)

thread = threading.Thread(target=run_oci_script)
thread.daemon = True
thread.start()

@app.route("/")
def home():
    return "OCI retry script is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
