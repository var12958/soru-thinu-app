// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAqv2TuxEJOGfLVzptL-T1hdBGZEDBmq1Y",
  authDomain: "food-snap-b3ff4.firebaseapp.com",
  projectId: "food-snap-b3ff4",
  storageBucket: "food-snap-b3ff4.appspot.com",
  messagingSenderId: "192398778104",
  appId: "1:192398778104:web:aba07fc75e87714275250d"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Services
const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();
