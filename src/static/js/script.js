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


// Network Request Handler: Authentication
async function handleAuth(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('auth-error');
    
    const endpoint = isLoginMode ? `${API_BASE}/login` : `${API_BASE}/register`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.msg || 'Something went wrong');
        
        if (isLoginMode) {
            // Store token data securely in local storage
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', username);
            state.token = data.access_token;
            state.username = username;
            state.currentView = 'chat';
            render();
        } else {
            alert('Registration successful! Please login.');
            isLoginMode = true;
            render();
        }
    } catch (err) {
        errorEl.textContent = err.message;
        errorEl.classList.remove('hidden');
    }
}


// Network Request Handler: Logout
async function handleLogout() {
    try {
        await fetch(`${API_BASE}/logout`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
    } catch (err) {
        console.error('Logout error on server:', err);
    } finally {
        // Always clear local client storage even if token blocklist network fails
        localStorage.clear();
        state.token = null;
        state.username = null;
        state.currentView = 'auth';
        render();
    }
}






// Initial load
document.addEventListener('DOMContentLoaded', render);