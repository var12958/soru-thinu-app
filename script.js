const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');

const resultsSection = document.getElementById('results-section');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const resetBtn = document.getElementById('reset-btn');

const foodPreview = document.getElementById('food-preview');
const foodNameInput = document.getElementById('food-name');

// Firebase / Auth UI elements
const signInBtn = document.getElementById('sign-in-btn');
const signOutBtn = document.getElementById('sign-out-btn');
const userEmailSpan = document.getElementById('user-email');
const historyList = document.getElementById('history-list');
const historySection = document.getElementById('history-section');

// Keep reference to the last uploaded file so we can upload to Storage
window.currentFile = null;

// Nutrition Elements
const caloriesVal = document.getElementById('calories-val');
const proteinVal = document.getElementById('protein-val');
const carbsVal = document.getElementById('carbs-val');
const fatsVal = document.getElementById('fats-val');
const microBody = document.getElementById('micronutrients-body');

// --- Dashboard & User Elements ---
const dashboardElements = [
    document.getElementById('dashboard-left'),
    document.getElementById('dashboard-center-tracker'),
    document.getElementById('dashboard-right')
];

const onboardingModal = document.getElementById('onboarding-modal');
const onboardingForm = document.getElementById('onboarding-form');
const editProfileBtn = document.getElementById('edit-profile-btn');
const calorieProgress = document.getElementById('calorie-progress');
const caloriesLeftEl = document.getElementById('calories-left');
const dailyGoalEl = document.getElementById('daily-goal');
const dailyEatenEl = document.getElementById('daily-eaten');

let userProfile = null;
let dailyStats = {
    date: new Date().toDateString(),
    eaten: 0,
    items: []
};

// Event Listeners

document.addEventListener('DOMContentLoaded', initApp);

onboardingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    saveUserProfile();
});

editProfileBtn.addEventListener('click', () => {
    onboardingModal.classList.remove('hidden');
});

uploadBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent bubbling to dropZone click
    fileInput.click();
});

function initApp() {
    loadUserProfile();
    loadDailyStats();
    updateDashboardUI();
}

function loadUserProfile() {
    const savedProfile = localStorage.getItem('foodsnap_user');
    if (savedProfile) {
        userProfile = JSON.parse(savedProfile);
        dashboardElements.forEach(el => el.classList.remove('hidden'));
        
        // Pre-fill form
        document.getElementById('user-height').value = userProfile.height;
        document.getElementById('user-weight').value = userProfile.weight;
        document.getElementById('user-age').value = userProfile.age;
        document.getElementById('user-gender').value = userProfile.gender;
        document.getElementById('user-goal').value = userProfile.goal;
    } else {
        // Show modal if new user
        onboardingModal.classList.remove('hidden');
    }
}

function saveUserProfile() {
    const height = parseInt(document.getElementById('user-height').value);
    const weight = parseInt(document.getElementById('user-weight').value);
    const age = parseInt(document.getElementById('user-age').value);
    const gender = document.getElementById('user-gender').value;
    const goal = document.getElementById('user-goal').value;

    if (!height || !weight || !age) {
        alert("Please fill in all fields");
        return;
    }

    // Calculate BMR (Mifflin-St Jeor Equation)
    let bmr;
    if (gender === 'male') {
        bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
        bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }

    // Calculate TDEE (Sedentary default 1.2 for simplicity, can be expanded)
    let tdee = bmr * 1.2;

    // Adjust for Goal
    let targetCalories = Math.round(tdee);
    if (goal === 'lose') {
        targetCalories -= 500; // Deficit
    } else if (goal === 'bulk') {
        targetCalories += 500; // Surplus
    }

    userProfile = { height, weight, age, gender, goal, targetCalories };
    localStorage.setItem('foodsnap_user', JSON.stringify(userProfile));
    
    onboardingModal.classList.add('hidden');
    dashboardElements.forEach(el => el.classList.remove('hidden'));
    updateDashboardUI();
}

function loadDailyStats() {
    const savedStats = localStorage.getItem('foodsnap_daily_stats');
    const today = new Date().toDateString();

    if (savedStats) {
        const parsed = JSON.parse(savedStats);
        if (parsed.date === today) {
            dailyStats = parsed;
            if (!dailyStats.items) dailyStats.items = []; // Ensure items array exists for old data
        } else {
            // New day, reset stats
            dailyStats = { date: today, eaten: 0, items: [] };
            saveDailyStats();
        }
    } else {
        dailyStats = { date: today, eaten: 0, items: [] };
        saveDailyStats();
    }
}

function saveDailyStats() {
    localStorage.setItem('foodsnap_daily_stats', JSON.stringify(dailyStats));
    updateDashboardUI();
}

function updateDashboardUI() {
    if (!userProfile) return;

    const target = userProfile.targetCalories;
    const eaten = dailyStats.eaten;
    const left = target - eaten;

    dailyGoalEl.innerText = target;
    dailyEatenEl.innerText = eaten;
    caloriesLeftEl.innerText = left; // Allow negative if over

    // Update Progress Circle
    // Calculate percentage of GOAL eaten
    let percentage = (eaten / target) * 100;
    if (percentage > 100) percentage = 100; // Cap visual at 100% (or handle overflow differently)
    
    // Conic gradient: Start color X deg, End color Y deg
    // 360 deg * percentage
    const degrees = (percentage / 100) * 360;
    calorieProgress.style.background = `conic-gradient(var(--secondary) ${degrees}deg, #eee ${degrees}deg)`;
    
    renderFoodLog();
}

function addCalories(foodItem) {
    dailyStats.eaten += foodItem.calories;
    if (!dailyStats.items) dailyStats.items = [];
    
    dailyStats.items.push({
        name: foodItem.name,
        calories: foodItem.calories,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    
    saveDailyStats();
}

function renderFoodLog() {
    const logList = document.getElementById('food-log-list');
    if (!logList) return;
    
    if (!dailyStats.items || dailyStats.items.length === 0) {
        logList.innerHTML = '<div class="empty-state">No food logged yet</div>';
        return;
    }
    
    logList.innerHTML = '';
    // Show recent first
    [...dailyStats.items].reverse().forEach(item => {
        const div = document.createElement('div');
        div.className = 'log-item';
        div.innerHTML = `
            <div class="log-info">
                <span class="log-name">${item.name}</span>
                <span class="log-time">${item.time}</span>
            </div>
            <span class="log-cals">+${item.calories}</span>
        `;
        logList.appendChild(div);
    });
}

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

    // Save selected file for later upload
    window.currentFile = file;

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

    // Call your trained model API
    const formData = new FormData();
    formData.append('file', window.currentFile);

    fetch('http://localhost:8081/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.items && data.items.length > 0) {
            const foodItem = data.items[0];
            
            // Populate Data
            foodNameInput.value = foodItem.food;
            caloriesVal.textContent = foodItem.calories;
            proteinVal.textContent = foodItem.protein_g + 'g';
            carbsVal.textContent = foodItem.carbs_g + 'g';
            fatsVal.textContent = foodItem.fat_g + 'g';
            
            // Add to daily tracking
            addCalories({
                name: foodItem.food,
                calories: foodItem.calories
            });
            
            // Clear micronutrients table for now
            microBody.innerHTML = '<tr><td>Serving Size</td><td>' + foodItem.serving_size + '</td></tr>';
            
            // If user is signed in, save prediction
            if (firebase && firebase.auth && firebase.auth().currentUser) {
                uploadImageAndSavePrediction(window.currentFile, foodItem.food, foodItem.calories);
            }
        } else {
            // Handle unknown food or error
            foodNameInput.value = 'Unknown Food';
            caloriesVal.textContent = '0';
            proteinVal.textContent = '0g';
            carbsVal.textContent = '0g';
            fatsVal.textContent = '0g';
            microBody.innerHTML = '<tr><td colspan="2">Food not recognized. Try a clearer image.</td></tr>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Show error message instead of mock data
        foodNameInput.value = 'Error - Backend not available';
        caloriesVal.textContent = '0';
        proteinVal.textContent = '0g';
        carbsVal.textContent = '0g';
        fatsVal.textContent = '0g';
        microBody.innerHTML = '<tr><td colspan="2">Please check if backend server is running on port 8081</td></tr>';
    });
}

function resetApp() {
    foodPreview.src = "";
    fileInput.value = "";
    resultsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
}

// --------- Firebase Auth / Firestore / Storage Helpers ---------

// Sign-in / Sign-out
if (signInBtn) signInBtn.addEventListener('click', () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithPopup(provider).catch(err => console.error(err));
});
if (signOutBtn) signOutBtn.addEventListener('click', () => {
    firebase.auth().signOut().catch(err => console.error(err));
});

// Observe auth state
if (firebase && firebase.auth) {
    firebase.auth().onAuthStateChanged(user => {
        if (user) {
            // show signed-in UI
            if (signInBtn) signInBtn.classList.add('hidden');
            if (signOutBtn) signOutBtn.classList.remove('hidden');
            if (userEmailSpan) userEmailSpan.textContent = user.email || user.uid;
            // Fetch user's history
            fetchHistory();
        } else {
            if (signInBtn) signInBtn.classList.remove('hidden');
            if (signOutBtn) signOutBtn.classList.add('hidden');
            if (userEmailSpan) userEmailSpan.textContent = '';
            if (historySection) historySection.classList.add('hidden');
            if (historyList) historyList.innerHTML = '';
        }
    });
}

function uploadImageAndSavePrediction(file, predictedName, calories) {
    if (!file) return Promise.resolve();
    const user = firebase.auth().currentUser;
    if (!user) return Promise.reject(new Error('Not authenticated'));

    const uid = user.uid;
    const path = `images/${uid}/${Date.now()}_${file.name}`;
    const storageRef = firebase.storage().ref(path);

    return storageRef.put(file)
    .then(snapshot => snapshot.ref.getDownloadURL())
    .then(url => {
        // Save a record in Firestore under users/{uid}/predictions
        return firebase.firestore().collection('users').doc(uid).collection('predictions').add({
            imagePath: path,
            imageUrl: url,
            predictedName,
            calories,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });
    })
    .then(() => fetchHistory())
    .catch(err => console.error('Upload/save error', err));
}

function fetchHistory() {
    const user = firebase.auth().currentUser;
    if (!user) return;
    const uid = user.uid;

    firebase.firestore().collection('users').doc(uid).collection('predictions')
    .orderBy('timestamp', 'desc').limit(50).get()
    .then(qs => {
        if (!historyList) return;
        historyList.innerHTML = '';
        qs.forEach(doc => {
            const data = doc.data();
            const li = document.createElement('li');
            li.className = 'history-item';
            const ts = data.timestamp && data.timestamp.toDate ? data.timestamp.toDate().toLocaleString() : '';
            li.innerHTML = `
                <img src="${data.imageUrl || ''}" alt="thumb" class="history-thumb">
                <div class="history-meta">
                  <div><strong>${data.predictedName || ''}</strong></div>
                  <div>${data.calories || ''} kcal</div>
                  <div class="ts">${ts}</div>
                </div>
            `;
            historyList.appendChild(li);
        });
        if (historySection) historySection.classList.remove('hidden');
    })
    .catch(err => console.error('Failed to fetch history', err));
}
