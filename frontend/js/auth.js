// ── JU 18th Batch Alumni — Auth Helper ──────────────────────
const API_BASE = window.API_BASE || 'http://localhost:8000';

// ── Departments ───────────────────────────────────────────────
const DEPARTMENTS = [
    "Bangla", "English", "History", "Philosophy", "Dramatics",
    "Statistics", "Mathematics", "Physics", "Chemistry", "Economics",
    "Geography", "Government & Politics", "Anthropology", "Geology",
    "Zoology", "Botany", "Pharmacy"
];

// Populate any <select> element with department options
function populateDepartmentSelect(selectId, includeAll = false) {
    var el = document.getElementById(selectId);
    if (!el) return;
    var html = includeAll
        ? '<option value="">All Departments</option>'
        : '<option value="">Select Department</option>';
    DEPARTMENTS.forEach(function(d) {
        html += '<option value="' + d + '">' + d + '</option>';
    });
    el.innerHTML = html;
}

const Auth = {
    getToken()        { return localStorage.getItem('access_token'); },
    getRefreshToken() { return localStorage.getItem('refresh_token'); },
    getUser()         { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; },
    isLoggedIn()      { return !!this.getToken(); },
    isApproved()      { const u = this.getUser(); return u && u.registration_status === 'approved'; },
    isAdmin()         { const u = this.getUser(); return u && (u.role === 'admin' || u.role === 'super_admin'); },

    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;
        try {
            const res = await fetch(`${API_BASE}/api/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            if (res.ok) {
                const data = await res.json();
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                    return true;
                }
            }
        } catch (e) { console.error('Token refresh failed:', e); }
        return false;
    },

    async request(path, options = {}, retry = true) {
        const token = this.getToken();
        const res = await fetch(`${API_BASE}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                ...(options.headers || {})
            }
        });
        if (res.status === 401 && retry) {
            const refreshed = await this.refreshAccessToken();
            if (refreshed) return this.request(path, options, false);
            this.logout();
            return null;
        }
        return res;
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/pages/login.html';
    },

    requireAuth()    { if (!this.isLoggedIn()) { window.location.href = '/pages/login.html'; return false; } return true; },
    requireApproved() {
        if (!this.isLoggedIn()) { window.location.href = '/pages/login.html'; return false; }
        if (!this.isApproved() && !this.isAdmin()) { window.location.href = '/pages/pending.html'; return false; }
        return true;
    },
    requireAdmin()   { if (!this.isAdmin()) { window.location.href = '/index.html'; return false; } return true; },

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
