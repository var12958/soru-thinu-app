class PizzaLogin {
    constructor() {
        this.isLoginMode = true;
        this.users = JSON.parse(localStorage.getItem('users') || '{}');
        this.initElements();
        this.bindEvents();
        this.setupEyeTracking();
    }

    initElements() {
        this.form = document.getElementById('authForm');
        this.email = document.getElementById('email');
        this.password = document.getElementById('password');
        this.submitBtn = document.getElementById('submitBtn');
        this.toggleMode = document.getElementById('toggleMode');
        this.mouth = document.getElementById('mouth');
        this.leftPupil = document.querySelector('.left-eye .pupil');
        this.rightPupil = document.querySelector('.right-eye .pupil');
        this.pizza = document.querySelector('.pizza');
    }

    bindEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.toggleMode.addEventListener('click', () => this.toggleAuthMode());
        this.email.addEventListener('input', () => this.trackTyping());
        this.password.addEventListener('input', () => this.trackTyping());
        this.email.addEventListener('focus', () => this.setNeutralExpression());
        this.password.addEventListener('focus', () => this.setNeutralExpression());
    }

    setupEyeTracking() {
        document.addEventListener('mousemove', (e) => this.moveEyes(e));
        this.email.addEventListener('input', () => this.moveEyesToInput(this.email));
        this.password.addEventListener('input', () => this.moveEyesToInput(this.password));
    }

    moveEyes(event) {
        const pizzaRect = this.pizza.getBoundingClientRect();
        const pizzaCenterX = pizzaRect.left + pizzaRect.width / 2;
        const pizzaCenterY = pizzaRect.top + pizzaRect.height / 2;
        
        const deltaX = event.clientX - pizzaCenterX;
        const deltaY = event.clientY - pizzaCenterY;
        
        const angle = Math.atan2(deltaY, deltaX);
        const distance = Math.min(4, Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 50);
        
        const pupilX = Math.cos(angle) * distance;
        const pupilY = Math.sin(angle) * distance;
        
        this.leftPupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
        this.rightPupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
    }

    moveEyesToInput(input) {
        const inputRect = input.getBoundingClientRect();
        const inputCenterX = inputRect.left + inputRect.width / 2;
        const inputCenterY = inputRect.top + inputRect.height / 2;
        
        const pizzaRect = this.pizza.getBoundingClientRect();
        const pizzaCenterX = pizzaRect.left + pizzaRect.width / 2;
        const pizzaCenterY = pizzaRect.top + pizzaRect.height / 2;
        
        const deltaX = inputCenterX - pizzaCenterX;
        const deltaY = inputCenterY - pizzaCenterY;
        
        const angle = Math.atan2(deltaY, deltaX);
        const pupilX = Math.cos(angle) * 3;
        const pupilY = Math.sin(angle) * 3;
        
        this.leftPupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
        this.rightPupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
    }

    trackTyping() {
        const emailValue = this.email.value;
        const passwordValue = this.password.value;
        
        if (emailValue.length > 0 || passwordValue.length > 0) {
            this.setNeutralExpression();
        }
    }

    setHappyExpression() {
        this.mouth.className = 'mouth happy';
        this.pizza.style.transform = 'scale(1.1)';
        setTimeout(() => {
            this.pizza.style.transform = 'scale(1)';
        }, 300);
    }

    setSadExpression() {
        this.mouth.className = 'mouth sad';
        this.pizza.classList.add('shake');
        setTimeout(() => {
            this.pizza.classList.remove('shake');
        }, 500);
    }

    setNeutralExpression() {
        this.mouth.className = 'mouth';
    }

    toggleAuthMode() {
        this.isLoginMode = !this.isLoginMode;
        if (this.isLoginMode) {
            this.submitBtn.textContent = 'Login';
            this.toggleMode.textContent = 'Sign up';
            document.querySelector('.toggle-text').innerHTML = 
                'Don\'t have an account? <span id="toggleMode">Sign up</span>';
        } else {
            this.submitBtn.textContent = 'Sign Up';
            this.toggleMode.textContent = 'Login';
            document.querySelector('.toggle-text').innerHTML = 
                'Already have an account? <span id="toggleMode">Login</span>';
        }
        
        // Rebind the toggle event
        document.getElementById('toggleMode').addEventListener('click', () => this.toggleAuthMode());
        this.setNeutralExpression();
    }

    handleSubmit(e) {
        e.preventDefault();
        
        const email = this.email.value.trim();
        const password = this.password.value.trim();
        
        if (!email || !password) {
            this.setSadExpression();
            return;
        }

        if (this.isLoginMode) {
            this.handleLogin(email, password);
        } else {
            this.handleSignup(email, password);
        }
    }

    handleLogin(email, password) {
        if (this.users[email] && this.users[email] === password) {
            this.setHappyExpression();
            setTimeout(() => {
                alert('Login successful! Welcome to FoodSnap!');
                // Redirect to main app or dashboard
                window.location.href = 'index.html';
            }, 1000);
        } else {
            this.setSadExpression();
            setTimeout(() => {
                alert('Invalid credentials. Please try again.');
            }, 500);
        }
    }

    handleSignup(email, password) {
        if (this.users[email]) {
            this.setSadExpression();
            setTimeout(() => {
                alert('Email already exists. Please login instead.');
                this.toggleAuthMode();
            }, 500);
        } else {
            this.users[email] = password;
            localStorage.setItem('users', JSON.stringify(this.users));
            this.setHappyExpression();
            setTimeout(() => {
                alert('Account created successfully! You can now login.');
                this.toggleAuthMode();
                this.form.reset();
            }, 1000);
        }
    }
}

// Initialize the login system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PizzaLogin();
});