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

