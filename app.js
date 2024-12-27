// app.js

// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyAYm75FiyeOd3ug8uBsOISdIoXMzZyX3y8",
  authDomain: "carbhari-abf7c.firebaseapp.com",
  projectId: "carbhari-abf7c",
  storageBucket: "carbhari-abf7c.appspot.com",
  messagingSenderId: "592415189844",
  appId: "1:592415189844:web:b78c2fa6eecf07322876c1",
  measurementId: "G-4CV4VV73X6"
};

firebase.initializeApp(firebaseConfig);

const storage = firebase.storage();
const firestore = firebase.firestore();

function uploadImages() {
    const imageInput = document.getElementById('imageInput');
    const files = imageInput.files;

    if (files.length === 0) {
        alert("Please select at least one image to upload.");
        return;
    }

    // Loop through selected files and upload each one
    Array.from(files).forEach(file => {
        const storageRef = storage.ref(`images/${file.name}`);
        const uploadTask = storageRef.put(file);

        uploadTask.on('state_changed', 
            function(snapshot) {
                // Track upload progress
            }, 
            function(error) {
                console.error("Error uploading image:", error);
            }, 
            function() {
                uploadTask.snapshot.ref.getDownloadURL().then(function(downloadURL) {
                    // Save image URL to Firestore
                    firestore.collection('images').add({
                        url: downloadURL,
                        name: file.name,
                        timestamp: firebase.firestore.FieldValue.serverTimestamp()
                    }).then(() => {
                        alert("Image uploaded successfully!");
                        loadImages();  // Reload gallery after upload
                    });
                });
            }
        );
    });
}

function loadImages() {
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = "";  // Clear current gallery

    firestore.collection('images').get().then(snapshot => {
        snapshot.forEach(doc => {
            const imageData = doc.data();
            const imgElement = document.createElement('img');
            imgElement.src = imageData.url;
            imgElement.alt = imageData.name;
            gallery.appendChild(imgElement);
        });
    });
}

// Load images when the page loads
window.onload = loadImages;
