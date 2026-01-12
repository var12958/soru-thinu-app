// -------- SIGN IN --------
function signIn() {
  const email = prompt("Enter email");
  const password = prompt("Enter password");

  auth.signInWithEmailAndPassword(email, password)
    .then(() => {
      alert("Signed in successfully!");
    })
    .catch(error => {
      alert(error.message);
    });
}

// -------- SIGN OUT --------
function signOutUser() {
  auth.signOut()
    .then(() => {
      alert("Signed out!");
    });
}

// -------- TRACK LOGIN STATE --------
auth.onAuthStateChanged(user => {
  const signInBtn = document.getElementById("sign-in-btn");
  const signOutBtn = document.getElementById("sign-out-btn");
  const userEmail = document.getElementById("user-email");

  if (user) {

    // ---- 7 day login limit ----
    const loginTime = localStorage.getItem("loginTime");

    if (!loginTime) {
      localStorage.setItem("loginTime", Date.now());
    } else {
      const oneWeek = 7 * 24 * 60 * 60 * 1000;
      if (Date.now() - loginTime > oneWeek) {
        auth.signOut();
        localStorage.removeItem("loginTime");
        alert("Session expired. Please log in again.");
        return;
      }
    }

    signInBtn.classList.add("hidden");
    signOutBtn.classList.remove("hidden");
    userEmail.textContent = user.email;
  } else {
    signInBtn.classList.remove("hidden");
    signOutBtn.classList.add("hidden");
    userEmail.textContent = "";
    localStorage.removeItem("loginTime");
  }
});

