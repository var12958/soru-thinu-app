const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const resetBtn = document.getElementById('reset-btn');

const foodPreview = document.getElementById('food-preview');
const foodNameInput = document.getElementById('food-name');

// Nutrition Elements
const caloriesVal = document.getElementById('calories-val');
const proteinVal = document.getElementById('protein-val');
const carbsVal = document.getElementById('carbs-val');
const fatsVal = document.getElementById('fats-val');
const microBody = document.getElementById('micronutrients-body');

// Mock Data Database
const mockFoods = [
    {
        name: "Cheesy Burger",
        calories: 850,
        protein: "45g",
        carbs: "60g",
        fats: "55g",
        micros: [
            { name: "Sodium", amount: "1200mg" },
            { name: "Calcium", amount: "15%" },
            { name: "Iron", amount: "20%" }
        ]
    },
    {
        name: "Pepperoni Pizza",
        calories: 320,
        protein: "14g",
        carbs: "35g",
        fats: "12g",
        micros: [
            { name: "Sodium", amount: "650mg" },
            { name: "Likopen", amount: "5mg" }
        ]
    },
    {
        name: "Grilled Chicken",
        calories: 220,
        protein: "28g",
        carbs: "0g",
        fats: "5g",
        micros: [
            { name: "Vitamin B6", amount: "30%" },
            { name: "Niacin", amount: "50%" }
        ]
    }
];

// Event Listeners

uploadBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent bubbling to dropZone click
    fileInput.click();
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', handleFileSelect);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
    dropZone.querySelector('.dashed-border').style.borderColor = 'var(--secondary)';
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    dropZone.querySelector('.dashed-border').style.borderColor = 'var(--tertiary)';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    dropZone.querySelector('.dashed-border').style.borderColor = 'var(--tertiary)';
    
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

resetBtn.addEventListener('click', resetApp);

function handleFileSelect(e) {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    if (!file.type.match('image.*')) {
        alert("Please upload a valid image file (JPG or PNG).");
        return;
    }

    // Show Image Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        foodPreview.src = e.target.result;
        startProcessing();
    };
    reader.readAsDataURL(file);
}

function startProcessing() {
    uploadSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    // Simulate AI Processing
    setTimeout(() => {
        analyzeFood();
    }, 2500); // 2.5 seconds of "dancing"
}

function analyzeFood() {
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Select random mock data
    const randomFood = mockFoods[Math.floor(Math.random() * mockFoods.length)];
    
    // Populate Data
    foodNameInput.value = randomFood.name;
    
    // Animate Numbers (Simple fake count up)
    caloriesVal.textContent = randomFood.calories;
    proteinVal.textContent = randomFood.protein;
    carbsVal.textContent = randomFood.carbs;
    fatsVal.textContent = randomFood.fats;

    // Populate Table
    microBody.innerHTML = '';
    randomFood.micros.forEach(micro => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${micro.name}</td><td>${micro.amount}</td>`;
        microBody.appendChild(row);
    });
}

function resetApp() {
    foodPreview.src = "";
    fileInput.value = "";
    resultsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
}
