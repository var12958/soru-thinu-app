class FoodSnapApp {
    constructor() {
        this.initElements();
        this.bindEvents();
        this.setupEyeTracking();
    }

    initElements() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.browseBtn = document.getElementById('browseBtn');
        this.previewSection = document.getElementById('previewSection');
        this.imagePreview = document.getElementById('imagePreview');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.results = document.getElementById('results');
        this.logoutBtn = document.getElementById('logoutBtn');
        this.pizzaMouth = document.getElementById('pizzaMouth');
        this.leftPupil = document.querySelector('.left-eye .pupil');
        this.rightPupil = document.querySelector('.right-eye .pupil');
        this.pizza = document.querySelector('.pizza');
    }

    bindEvents() {
        this.browseBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.dropZone.addEventListener('click', () => this.fileInput.click());
        this.dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropZone.addEventListener('drop', (e) => this.handleDrop(e));
        this.analyzeBtn.addEventListener('click', () => this.analyzeFood());
        this.clearBtn.addEventListener('click', () => this.clearImage());
        this.logoutBtn.addEventListener('click', () => this.logout());
    }

    setupEyeTracking() {
        document.addEventListener('mousemove', (e) => this.moveEyes(e));
    }

    moveEyes(event) {
        const pizzaRect = this.pizza.getBoundingClientRect();
        const pizzaCenterX = pizzaRect.left + pizzaRect.width / 2;
        const pizzaCenterY = pizzaRect.top + pizzaRect.height / 2;
        
        const deltaX = event.clientX - pizzaCenterX;
        const deltaY = event.clientY - pizzaCenterY;
        
        const angle = Math.atan2(deltaY, deltaX);
        const distance = Math.min(3, Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 100);
        
        const pupilX = Math.cos(angle) * distance;
        const pupilY = Math.sin(angle) * distance;
        
        this.leftPupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
        this.rightPupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
    }

    setHappyExpression() {
        this.pizzaMouth.className = 'mouth happy';
        this.pizza.style.transform = 'scale(1.1)';
        setTimeout(() => {
            this.pizza.style.transform = 'scale(1)';
        }, 300);
    }

    setSadExpression() {
        this.pizzaMouth.className = 'mouth sad';
        this.pizza.classList.add('shake');
        setTimeout(() => {
            this.pizza.classList.remove('shake');
        }, 500);
    }

    setNeutralExpression() {
        this.pizzaMouth.className = 'mouth';
    }

    handleDragOver(e) {
        e.preventDefault();
        this.dropZone.classList.add('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        if (!file.type.startsWith('image/')) {
            this.setSadExpression();
            alert('Please select an image file');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.imagePreview.src = e.target.result;
            this.dropZone.style.display = 'none';
            this.previewSection.style.display = 'block';
            this.setHappyExpression();
        };
        reader.readAsDataURL(file);
    }

    async analyzeFood() {
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Analyzing...';
        
        try {
            const formData = new FormData();
            const fileInput = document.getElementById('fileInput');
            formData.append('file', fileInput.files[0]);
            
            // Call the actual backend API
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.displayResults(data);
            this.setHappyExpression();
            
        } catch (error) {
            console.error('Error analyzing food:', error);
            this.setSadExpression();
            alert('Error analyzing food. Please try again.');
        } finally {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.textContent = 'Analyze Food';
        }
    }

    displayResults(data) {
        if (data.status === 'success' && data.items && data.items.length > 0) {
            const firstItem = data.items[0];
            
            document.getElementById('foodType').innerHTML = `
                <h4>Food Type: ${firstItem.food}</h4>
                <p>Serving Size: ${firstItem.serving_size}</p>
                <p>Source: ${firstItem.source}</p>
            `;
            
            document.getElementById('nutritionInfo').innerHTML = `
                <h4>Nutrition Information:</h4>
                <ul>
                    <li>Calories: ${firstItem.calories}</li>
                    <li>Protein: ${firstItem.protein_g}g</li>
                    <li>Carbs: ${firstItem.carbs_g}g</li>
                    <li>Fat: ${firstItem.fat_g}g</li>
                </ul>
                <p><strong>Total Calories: ${data.total_calories}</strong></p>
            `;
        } else {
            document.getElementById('foodType').innerHTML = `
                <h4>Analysis Failed</h4>
                <p>Could not identify the food item</p>
            `;
            
            document.getElementById('nutritionInfo').innerHTML = `
                <p>Please try with a clearer image</p>
            `;
        }
        
        this.results.style.display = 'block';
    }

    clearImage() {
        this.dropZone.style.display = 'block';
        this.previewSection.style.display = 'none';
        this.results.style.display = 'none';
        this.fileInput.value = '';
        this.setNeutralExpression();
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            window.location.href = 'login.html';
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FoodSnapApp();
});