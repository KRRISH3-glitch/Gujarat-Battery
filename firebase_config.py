# firebaseconfig.py

import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

# 🔒 Disable broken gRPC auth plugin on Windows
os.environ["GRPC_PYTHON_DISABLE_RUNTIME_PROVIDED_SERVICES"] = "1"

# Load Firebase credentials from Streamlit secrets
firebase_secrets = st.secrets["firebase"]

cred_info = {
    "type": firebase_secrets["type"],
    "project_id": firebase_secrets["project_id"],
    "private_key_id": firebase_secrets["private_key_id"],
    "private_key": firebase_secrets["private_key"],
    "client_email": firebase_secrets["client_email"],
    "client_id": firebase_secrets["client_id"],
    "auth_uri": firebase_secrets["auth_uri"],
    "token_uri": firebase_secrets["token_uri"],
    "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_secrets["client_x509_cert_url"],
}

cred = credentials.Certificate(cred_info)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.Client(
    project=cred.project_id,
    credentials=cred.get_credential()
)
