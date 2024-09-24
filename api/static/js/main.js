document.addEventListener('DOMContentLoaded', () => {
    const modelSelect = document.getElementById('modelSelect');
    const promptInput = document.getElementById('promptInput');
    const generateBtn = document.getElementById('generateBtn');
    const imageGrid = document.getElementById('imageGrid');
    const loading = document.getElementById('loading');
    const imageModal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const closeModal = document.getElementById('closeModal');

    // Fetch and populate models
    fetch('/api/models')
        .then(response => response.json())
        .then(models => {
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        });

    generateBtn.addEventListener('click', () => {
        const model = modelSelect.value;
        const prompt = promptInput.value;

        if (!model || !prompt) {
            alert('Please select a model and enter a prompt.');
            return;
        }

        loading.classList.remove('hidden');
        generateBtn.disabled = true;

        fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model, prompt }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.image) {
                    const card = document.createElement('div');
                    card.className = 'image-card bg-gray-800 rounded-lg overflow-hidden neon-box-shadow';
                    
                    const img = document.createElement('img');
                    img.src = `data:image/png;base64,${data.image}`;
                    img.alt = 'Generated Image';
                    img.className = 'w-full h-64 object-cover cursor-pointer';
                    
                    img.addEventListener('click', () => {
                        modalImage.src = img.src;
                        imageModal.classList.remove('hidden');
                    });

                    card.appendChild(img);
                    imageGrid.prepend(card);
                } else {
                    alert('Failed to generate image. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            })
            .finally(() => {
                loading.classList.add('hidden');
                generateBtn.disabled = false;
            });
    });

    closeModal.addEventListener('click', () => {
        imageModal.classList.add('hidden');
    });

    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) {
            imageModal.classList.add('hidden');
        }
    });
});