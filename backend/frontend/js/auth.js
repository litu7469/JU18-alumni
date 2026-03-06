// ── JU 18th Batch Alumni — Auth Helper ──────────────────────
const API_BASE = window.API_BASE || 'http://localhost:8000';

const Auth = {
    getToken() { return localStorage.getItem('access_token'); },
    getUser() { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; },
    isLoggedIn() { return !!this.getToken(); },
    isApproved() { const u = this.getUser(); return u && u.registration_status === 'approved'; },
    isAdmin() { const u = this.getUser(); return u && (u.role === 'admin' || u.role === 'super_admin'); },

    async request(path, options = {}) {
        const token = this.getToken();
        const res = await fetch(`${API_BASE}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                ...(options.headers || {})
            }
        });
        if (res.status === 401) { this.logout(); return null; }
        return res;
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/pages/login.html';
    },

    requireAuth() {
        if (!this.isLoggedIn()) { window.location.href = '/pages/login.html'; return false; }
        return true;
    },

    requireApproved() {
        if (!this.isLoggedIn()) { window.location.href = '/pages/login.html'; return false; }
        if (!this.isApproved() && !this.isAdmin()) {
            window.location.href = '/pages/pending.html'; return false;
        }
        return true;
    },

    requireAdmin() {
        if (!this.isAdmin()) { window.location.href = '/index.html'; return false; }
        return true;
    },

    updateNavbar() {
        const user = this.getUser();
        const navAuth = document.getElementById('nav-auth');
        if (!navAuth) return;
        if (user) {
            navAuth.innerHTML = `
                <a href="/pages/dashboard.html" class="nav-btn">👤 ${user.full_name?.split(' ')[0] || 'Profile'}</a>
                ${this.isAdmin() ? '<a href="/admin/dashboard.html" class="nav-btn admin-btn">⚙️ Admin</a>' : ''}
                <a href="#" onclick="Auth.logout()" class="nav-btn logout-btn">Logout</a>
            `;
        } else {
            navAuth.innerHTML = `
                <a href="/pages/register.html" class="nav-btn register-btn">Register</a>
                <a href="/pages/login.html" class="nav-btn login-btn">Login</a>
            `;
        }
    }
};
