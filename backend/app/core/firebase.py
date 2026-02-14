import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import get_settings
import os

settings = get_settings()

def initialize_firebase():
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if os.path.exists(cred_path):
            import json
            try:
                with open(cred_path, 'r') as f:
                    content = json.load(f)
                    if "REPLACE_ME" in str(content.get("private_key", "")):
                        print(f"Warning: Firebase credentials at {cred_path} contain placeholders. Skipping initialization.")
                        return
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Error loading Firebase credentials: {e}")
        else:
            print(f"Warning: Firebase credentials not found at {cred_path}")

def get_firestore_client():
    if not firebase_admin._apps:
         initialize_firebase()
    
    try:
        return firestore.client()
    except ValueError:
        # Fallback or re-init if needed, but usually _apps check handles it
        return None
