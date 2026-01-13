import os
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

# 🔒 Disable broken gRPC auth plugin on Windows
os.environ["GRPC_PYTHON_DISABLE_RUNTIME_PROVIDED_SERVICES"] = "1"

KEY_PATH = r"C:\Users\KRISH\Desktop\battery_service_streamlit\serviceAccountKey.json"

cred = credentials.Certificate(KEY_PATH)

# Initialize Firebase ONLY ONCE
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# 🔑 FORCE Firestore to use the SAME credentials
db = firestore.Client(
    project=cred.project_id,
    credentials=cred.get_credential()
)