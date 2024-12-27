document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('imageUpload');
    formData.append('image', fileInput.files[0]);

    const response = await fetch('/upload-image', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if (data.success) {
        document.getElementById('imageResult').innerHTML = `<img src="${data.imageUrl}" alt="Uploaded Image">`;
        fetchSimilarImages(data.imageUrl);
    }
});

async function fetchSimilarImages(imageUrl) {
    const response = await fetch(`/find-similar?imageUrl=${imageUrl}`);
    const data = await response.json();
    
    const similarImagesContainer = document.getElementById('similarImages');
    similarImagesContainer.innerHTML = '';
    data.similarImages.forEach(image => {
        similarImagesContainer.innerHTML += `<img src="${image}" alt="Similar Image">`;
    });
}
