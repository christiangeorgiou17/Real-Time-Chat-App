// Global state management
const state = {
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
    currentView: localStorage.getItem('token') ? 'chat' : 'auth'
};

// API base path configuration
const API_BASE = '/api';

// Render engine switcher
function render() {
    const app = document.getElementById('app');
    
    if (state.currentView === 'auth') {
        app.innerHTML = renderAuthView();
    } else {
        app.innerHTML = renderChatView();
    }
}

// HTML Component: Login & Registration Forms
function renderAuthView() {
    return `
        <div class="auth-container">
            <h2>Welcome to Chat</h2>
            <div id="auth-error" class="error-msg hidden"></div>
            
            <form id="auth-form" onsubmit="handleAuth(event)">
                <div class="input-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" required autocomplete="username">
                </div>
                <div class="input-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" required autocomplete="current-password">
                </div>
                <button type="submit" id="submit-btn">Login</button>
            </form>
            
            <p class="toggle-text">
                Don't have an account? <a href="#" onclick="toggleAuthMode(event)">Register instead</a>
            </p>
        </div>
    `;
}

// Toggle logic between Login and Register
let isLoginMode = true;
function toggleAuthMode(e) {
    e.preventDefault();
    isLoginMode = !isLoginMode;
    document.getElementById('submit-btn').innerText = isLoginMode ? 'Login' : 'Register';
    document.querySelector('.toggle-text').innerHTML = isLoginMode 
        ? `Don't have an account? <a href="#" onclick="toggleAuthMode(event)">Register instead</a>`
        : `Already have an account? <a href="#" onclick="toggleAuthMode(event)">Login instead</a>`;
}

// Initial load
document.addEventListener('DOMContentLoaded', render);