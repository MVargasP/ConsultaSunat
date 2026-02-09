const API_BASE = window.location.origin + '/api';

// State management
let state = {
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user')),
    company: null
};

// DOM Elements
const loginSection = document.getElementById('login-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const loginBtn = document.getElementById('login-btn');
const loginError = document.getElementById('login-error');
const displayName = document.getElementById('display-name');
const totalSunatEl = document.getElementById('total-sunat');
const logoutBtn = document.getElementById('logout-btn');

// Initialize app
function init() {
    if (state.token) {
        showDashboard();
    } else {
        showLogin();
    }
}

function showLogin() {
    loginSection.style.display = 'flex';
    dashboardSection.style.display = 'none';
}

function showDashboard() {
    loginSection.style.display = 'none';
    dashboardSection.style.display = 'block';
    if (state.user) {
        displayName.textContent = `${state.user.first_name || state.user.username}`;
        fetchCompanyData();
    } else {
        logout();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // UI Loading state
    loginBtn.disabled = true;
    loginBtn.querySelector('span').style.display = 'none';
    loginBtn.querySelector('.loader-inner').style.display = 'block';
    loginError.textContent = '';

    try {
        const response = await fetch(`${API_BASE}/user/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            state.token = data.token.token;
            state.user = data.usuario;
            localStorage.setItem('token', state.token);
            localStorage.setItem('user', JSON.stringify(state.user));
            showDashboard();
        } else {
            loginError.textContent = data.non_field_errors || data.detail || 'Credenciales inválidas';
        }
    } catch (error) {
        console.error('Login error:', error);
        loginError.textContent = 'Error de conexión con el servidor';
    } finally {
        loginBtn.disabled = false;
        loginBtn.querySelector('span').style.display = 'block';
        loginBtn.querySelector('.loader-inner').style.display = 'none';
    }
}

async function fetchCompanyData() {
    if (!state.user || !state.user.company) return;

    try {
        const response = await fetch(`${API_BASE}/company/${state.user.company}/`, {
            headers: {
                'Authorization': `Token ${state.token}`
            }
        });

        if (response.ok) {
            const companyData = await response.json();
            state.company = companyData;
            const limit = companyData.limit_sunat || '';
            const end = companyData.total_sunat || 0;
            animateValue(totalSunatEl, 0, end, 1000, limit);
        } else if (response.status === 401) {
            logout();
        } else {
            totalSunatEl.textContent = '--- / ---';
        }
    } catch (error) {
        console.error('Fetch company error:', error);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    state = { token: null, user: null, company: null };
    showLogin();
}

// Helper: Animate numbers
function animateValue(obj, start, end, duration, limit) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentVal = Math.floor(progress * (end - start) + start);
        obj.innerHTML = limit ? `${currentVal} / ${limit}` : currentVal;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Event Listeners
loginForm.addEventListener('submit', handleLogin);
logoutBtn.addEventListener('click', logout);

// Run init
init();
