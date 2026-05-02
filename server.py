from flask import Flask
import threading
import oci
import os
import time

app = Flask(__name__)

def try_create_instance():
    while True:
        try:
            config = {
                "user": os.environ.get("OCI_USER_ID"),
                "tenancy": os.environ.get("OCI_TENANCY_ID"),
                "region": os.environ.get("OCI_REGION"),
                "fingerprint": os.environ.get("OCI_KEY_FINGERPRINT"),
                "key_content": os.environ.get("OCI_PRIVATE_KEY_CONTENT")
            }
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
            print(f"SUCCESS! Instance created: {response.data.id}")
            break
            
        except oci.exceptions.ServiceError as e:
            print(f"Attempt failed: {e.message} - Retrying in 5 minutes...")
            time.sleep(300)
        except Exception as e:
            print(f"Error: {str(e)} - Retrying in 5 minutes...")
            time.sleep(300)

thread = threading.Thread(target=try_create_instance)
thread.daemon = True
thread.start()

@app.route("/")
def home():
    return "OCI retry script is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
