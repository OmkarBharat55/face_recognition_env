from flask import Flask, request, jsonify, render_template
from firebase_admin import credentials, initialize_app, storage, firestore
import os
from uuid import uuid4
from mtcnn import MTCNN
from PIL import Image
import numpy as np
import face_recognition
import pickle

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("firebase-credentials.json")
initialize_app(cred, {'storageBucket': 'carbhari-abf7c.appspot.com'})
bucket = storage.bucket()
db = firestore.client()

# MTCNN Face Detector
detector = MTCNN()

@app.route('/')
def index():
    return render_template('index.html')

def detect_faces(image_path):
    image = Image.open(image_path)
    image_np = np.array(image)
    faces = detector.detect_faces(image_np)
    return len(faces), faces

def extract_face_features(image_path):
    # Load the image and detect faces
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    return face_encodings

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file:
        filename = f"{uuid4()}{os.path.splitext(file.filename)[1]}"
        local_path = os.path.join('temp', filename)
        file.save(local_path)

        # Detect faces and extract features
        face_count, faces = detect_faces(local_path)
        face_encodings = extract_face_features(local_path)

        # If faces are detected, store the first face encoding in the database
        if face_encodings:
            face_encoding = face_encodings[0]
            # Store the image URL and face encoding (as a list)
            blob = bucket.blob(filename)
            blob.upload_from_filename(local_path)
            blob.make_public()

            db.collection('images').add({
                'url': blob.public_url,
                'face_count': face_count,
                'face_encoding': pickle.dumps(face_encoding),  # Store the face encoding
            })

        os.remove(local_path)

        return jsonify({'url': blob.public_url, 'face_count': face_count}), 200
    return jsonify({'error': 'Upload failed'}), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        images = [{'url': doc.to_dict()['url'], 'face_count': doc.to_dict()['face_count']} 
                  for doc in db.collection('images').stream()]
        return jsonify({'images': images}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file:
        filename = f"{uuid4()}{os.path.splitext(file.filename)[1]}"
        local_path = os.path.join('temp', filename)
        file.save(local_path)

        # Extract features of the uploaded image
        uploaded_face_encodings = extract_face_features(local_path)

        if not uploaded_face_encodings:
            os.remove(local_path)
            return jsonify({'error': 'No face detected in the uploaded image'}), 400

        uploaded_face_encoding = uploaded_face_encodings[0]

        # Retrieve images from Firebase and compare face encodings
        images = db.collection('images').stream()
        results = []
        for doc in images:
            image_data = doc.to_dict()

            # Check if 'face_encoding' exists in the document
            if 'face_encoding' not in image_data:
                continue  # Skip this document if no face encoding is found

            try:
                stored_face_encoding = pickle.loads(image_data['face_encoding'])

                # Compare the face encodings using cosine similarity or Euclidean distance
                distance = np.linalg.norm(uploaded_face_encoding - stored_face_encoding)
                print(f"Distance: {distance}")  # Log the distance for debugging
                if distance < 0.6:  # You can adjust this threshold based on your needs
                    results.append({'url': image_data['url'], 'distance': distance})
            except Exception as e:
                print(f"Error processing face encoding: {e}")
                continue  # Skip if there's an error with face encoding

        results.sort(key=lambda x: x['distance'])

        os.remove(local_path)

        return jsonify({'results': results}), 200

if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(debug=True)
