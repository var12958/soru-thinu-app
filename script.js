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

    // If user is signed in, upload the image and save prediction to Firestore
    if (firebase && firebase.auth && firebase.auth().currentUser) {
        uploadImageAndSavePrediction(window.currentFile, randomFood.name, randomFood.calories);
    }
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

