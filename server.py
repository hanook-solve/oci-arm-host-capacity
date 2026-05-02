from flask import Flask
import threading
import os
import time

app = Flask(__name__)

def try_create_instance():
    print("OCI retry thread started...", flush=True)
    
    required = [
        "OCI_USER_ID", "OCI_TENANCY_ID", "OCI_REGION",
        "OCI_KEY_FINGERPRINT", "OCI_PRIVATE_KEY_CONTENT",
        "OCI_SUBNET_ID", "OCI_IMAGE_ID", "OCI_SSH_PUBLIC_KEY"
    ]
    
    for var in required:
        value = os.environ.get(var)
        if not value:
            print(f"MISSING ENV VAR: {var}", flush=True)
        else:
            print(f"OK: {var} is set", flush=True)
    
    print("Starting OCI retry loop...", flush=True)
    
    while True:
        print("Making OCI attempt now...", flush=True)
        try:
            import oci
            config = {
                "user": os.environ.get("OCI_USER_ID"),
                "tenancy": os.environ.get("OCI_TENANCY_ID"),
                "region": os.environ.get("OCI_REGION"),
                "fingerprint": os.environ.get("OCI_KEY_FINGERPRINT"),
                "key_content": os.environ.get("OCI_PRIVATE_KEY_CONTENT"),
                "timeout": 30
            }
            print("Config built, connecting to OCI...", flush=True)
            compute = oci.core.ComputeClient(config)
            
            details = oci.core.models.LaunchInstanceDetails(
                compartment_id=os.environ.get("OCI_TENANCY_ID"),
                shape=os.environ.get("OCI_SHAPE"),
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                    ocpus=float(os.environ.get("OCI_OCPUS")),
                    memory_in_gbs=float(os.environ.get("OCI_MEMORY_IN_GBS"))
                ),
                subnet_id=os.environ.get("OCI_SUBNET_ID"),
                image_id=os.environ.get("OCI_IMAGE_ID"),
                metadata={
                    "ssh_authorized_keys": os.environ.get("OCI_SSH_PUBLIC_KEY")
                },
                display_name="free-arm-instance"
            )
            
            response = compute.launch_instance(details)
            print(f"SUCCESS! Instance created: {response.data.id}", flush=True)
            break
            
        except Exception as e:
            print(f"Attempt failed: {str(e)}", flush=True)
            print("Retrying in 5 minutes...", flush=True)
            time.sleep(300)

thread = threading.Thread(target=try_create_instance)
thread.daemon = True
thread.start()

@app.route("/")
def home():
    return "OCI retry script is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
