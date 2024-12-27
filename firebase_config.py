import firebase_admin
from firebase_admin import credentials, storage, firestore

# Initialize Firebase Admin SDK only if it hasn't been initialized already
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-credentials.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'carbhari-abf7c.appspot.com',
    })
else:
    print("Firebase app already initialized.")

# Firestore setup
db = firestore.client()
