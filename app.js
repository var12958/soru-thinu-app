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
            // Simulate API call to backend
            const formData = new FormData();
            const fileInput = document.getElementById('fileInput');
            formData.append('file', fileInput.files[0]);
            
            // Mock response for demo - replace with actual API call
            setTimeout(() => {
                this.displayResults({
                    food_type: 'Pizza',
                    confidence: 0.95,
                    nutrition: {
                        calories: 285,
                        protein: 12,
                        carbs: 36,
                        fat: 10
                    }
                });
                this.setHappyExpression();
                this.analyzeBtn.disabled = false;
                this.analyzeBtn.textContent = 'Analyze Food';
            }, 2000);
            
        } catch (error) {
            this.setSadExpression();
            alert('Error analyzing food. Please try again.');
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.textContent = 'Analyze Food';
        }
    }

    displayResults(data) {
        document.getElementById('foodType').innerHTML = `
            <h4>Food Type: ${data.food_type}</h4>
            <p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
        `;
        
        document.getElementById('nutritionInfo').innerHTML = `
            <h4>Nutrition (per 100g):</h4>
            <ul>
                <li>Calories: ${data.nutrition.calories}</li>
                <li>Protein: ${data.nutrition.protein}g</li>
                <li>Carbs: ${data.nutrition.carbs}g</li>
                <li>Fat: ${data.nutrition.fat}g</li>
            </ul>
        `;
        
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