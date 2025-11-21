/**
 * BI GHI TOOL MMO - Admin Panel JavaScript
 * Complete admin management system
 */

// Admin Dashboard Class
class AdminDashboard {
    constructor() {
        this.currentPage = 'overview';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadOverviewData();
        this.initCharts();
        this.setupEventListeners();
    }

    setupNavigation() {
        document.querySelectorAll('.nav-item[data-page]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.loadPage(page);
            });
        });
    }

    loadPage(pageName) {
        // Hide all pages
        document.querySelectorAll('.admin-page').forEach(page => {
            page.classList.remove('active');
        });

        // Show selected page
        const targetPage = document.getElementById(`page-${pageName}`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');

        // Update page title
        const titles = {
            overview: 'Tổng quan',
            analytics: 'Analytics',
            users: 'Quản lý Users',
            vip: 'Quản lý VIP',
            permissions: 'Permissions',
            settings: 'Cài đặt',
            logs: 'Activity Logs',
            payments: 'Payments'
        };
        document.getElementById('pageTitle').textContent = titles[pageName] || 'Admin';

        this.currentPage = pageName;
        this.loadPageData(pageName);
    }

    async loadPageData(pageName) {
        switch(pageName) {
            case 'users':
                await this.loadUsers();
                break;
            case 'vip':
                await this.loadVIPData();
                break;
            case 'logs':
                await this.loadLogs();
                break;
        }
    }

    async loadOverviewData() {
        try {
            const response = await fetch('/api/admin/overview');
            const data = await response.json();

            // Update stats
            document.getElementById('totalUsers').textContent = data.total_users || 0;
            document.getElementById('activeUsers').textContent = data.active_users || 0;
            document.getElementById('vipUsers').textContent = data.vip_users || 0;
            document.getElementById('totalRevenue').textContent = this.formatCurrency(data.total_revenue || 0);
            document.getElementById('totalOps').textContent = data.total_operations || 0;
            document.getElementById('todayOps').textContent = data.today_operations || 0;

            // Load recent activities
            this.loadRecentActivities(data.recent_activities || []);

        } catch (error) {
            console.error('Failed to load overview data:', error);
        }
    }

    loadRecentActivities(activities) {
        const container = document.getElementById('recentActivities');
        if (!container) return;

        const html = activities.slice(0, 5).map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${this.getActivityColor(activity.action)}">
                    <i class="${this.getActivityIcon(activity.action)}"></i>
                </div>
                <div class="activity-details">
                    <div class="activity-title">${activity.action}</div>
                    <div class="activity-time">${activity.details} • ${this.timeAgo(activity.timestamp)}</div>
                </div>
                <span class="activity-status success">Success</span>
            </div>
        `).join('');

        container.innerHTML = html || '<p class="text-center">No recent activities</p>';
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/admin/users');
            const users = await response.json();

            const tbody = document.getElementById('usersTableBody');
            if (!tbody) return;

            const html = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td><strong>${user.username}</strong></td>
                    <td>${user.email || '-'}</td>
                    <td><span class="vip-badge-table ${this.getVIPClass(user.vip_level)}">${this.getVIPName(user.vip_level)}</span></td>
                    <td>${user.role}</td>
                    <td><span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                        <i class="fas fa-circle"></i> ${user.is_active ? 'Active' : 'Inactive'}
                    </span></td>
                    <td>${this.formatDate(user.created_at)}</td>
                    <td>
                        <div class="action-btns">
                            <button class="btn-action view" onclick="viewUser(${user.id})" title="View">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-action edit" onclick="editUser(${user.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn-action delete" onclick="deleteUser(${user.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');

            tbody.innerHTML = html || '<tr><td colspan="8" class="text-center">No users found</td></tr>';

        } catch (error) {
            console.error('Failed to load users:', error);
        }
    }

    async loadVIPData() {
        try {
            const response = await fetch('/api/admin/vip-stats');
            const data = await response.json();

            document.getElementById('freeUsers').textContent = data.free_users || 0;
            document.getElementById('basicUsers').textContent = data.basic_users || 0;
            document.getElementById('proUsers').textContent = data.pro_users || 0;
            document.getElementById('enterpriseUsers').textContent = data.enterprise_users || 0;

            // Load subscriptions
            const tbody = document.getElementById('subscriptionsTableBody');
            if (!tbody) return;

            const html = (data.subscriptions || []).map(sub => `
                <tr>
                    <td><strong>${sub.username}</strong></td>
                    <td><span class="vip-badge-table ${this.getVIPClass(sub.vip_level)}">${this.getVIPName(sub.vip_level)}</span></td>
                    <td>${this.formatDate(sub.started_at)}</td>
                    <td>${this.formatDate(sub.expires_at)}</td>
                    <td>${this.formatCurrency(sub.price)}</td>
                    <td><span class="status-badge ${sub.is_active ? 'active' : 'inactive'}">
                        ${sub.is_active ? 'Active' : 'Expired'}
                    </span></td>
                    <td>
                        <button class="btn-action view" onclick="viewSubscription(${sub.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `).join('');

            tbody.innerHTML = html || '<tr><td colspan="7" class="text-center">No subscriptions found</td></tr>';

        } catch (error) {
            console.error('Failed to load VIP data:', error);
        }
    }

    async loadLogs() {
        try {
            const response = await fetch('/api/admin/logs');
            const logs = await response.json();

            const tbody = document.getElementById('logsTableBody');
            if (!tbody) return;

            const html = logs.slice(0, 50).map(log => `
                <tr>
                    <td>${this.formatDateTime(log.timestamp)}</td>
                    <td><strong>${log.username || 'System'}</strong></td>
                    <td><span class="vip-badge-table ${this.getActionColor(log.action)}">${log.action}</span></td>
                    <td>${log.details || '-'}</td>
                    <td>${log.ip_address || '-'}</td>
                </tr>
            `).join('');

            tbody.innerHTML = html || '<tr><td colspan="5" class="text-center">No logs found</td></tr>';

        } catch (error) {
            console.error('Failed to load logs:', error);
        }
    }

    initCharts() {
        // User Growth Chart
        const userCtx = document.getElementById('userGrowthChart');
        if (userCtx) {
            this.charts.userGrowth = new Chart(userCtx, {
                type: 'line',
                data: {
                    labels: this.getLast30Days(),
                    datasets: [{
                        label: 'New Users',
                        data: this.generateMockData(30, 0, 20),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#b0b3c1' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: '#2d3348' },
                            ticks: { color: '#b0b3c1' }
                        },
                        x: {
                            grid: { color: '#2d3348' },
                            ticks: { color: '#b0b3c1' }
                        }
                    }
                }
            });
        }

        // VIP Distribution Chart
        const vipCtx = document.getElementById('vipDistributionChart');
        if (vipCtx) {
            this.charts.vipDistribution = new Chart(vipCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Free', 'Basic', 'Pro', 'Enterprise'],
                    datasets: [{
                        data: [65, 20, 12, 3],
                        backgroundColor: ['#95a5a6', '#3498db', '#f39c12', '#9b59b6']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#b0b3c1' }
                        }
                    }
                }
            });
        }
    }

    setupEventListeners() {
        // Refresh button
        window.refreshData = () => {
            this.loadPageData(this.currentPage);
            showNotification('Data refreshed', 'success');
        };
    }

    // Utility Functions
    getVIPClass(level) {
        const classes = ['free', 'basic', 'pro', 'enterprise'];
        return classes[level] || 'free';
    }

    getVIPName(level) {
        const names = ['Free', 'Basic', 'Pro', 'Enterprise'];
        return names[level] || 'Free';
    }

    getActivityColor(action) {
        if (action.includes('login')) return 'blue';
        if (action.includes('vip')) return 'purple';
        if (action.includes('delete')) return 'red';
        return 'green';
    }

    getActivityIcon(action) {
        if (action.includes('login')) return 'fas fa-sign-in-alt';
        if (action.includes('vip')) return 'fas fa-crown';
        if (action.includes('delete')) return 'fas fa-trash';
        return 'fas fa-check';
    }

    getActionColor(action) {
        if (action === 'login') return 'basic';
        if (action === 'vip_upgrade') return 'pro';
        if (action === 'user_created') return 'enterprise';
        return 'free';
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
    }

    formatDate(dateStr) {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleDateString('vi-VN');
    }

    formatDateTime(dateStr) {
        if (!dateStr) return '-';
        return new Date(dateStr).toLocaleString('vi-VN');
    }

    timeAgo(dateStr) {
        const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
        if (seconds < 60) return `${seconds} seconds ago`;
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes} minutes ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours} hours ago`;
        const days = Math.floor(hours / 24);
        return `${days} days ago`;
    }

    getLast30Days() {
        const days = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            days.push(date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' }));
        }
        return days;
    }

    generateMockData(count, min, max) {
        return Array.from({ length: count }, () => Math.floor(Math.random() * (max - min + 1)) + min);
    }
}

// Global Functions
function showAddUserModal() {
    document.getElementById('addUserModal').classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

async function submitAddUser() {
    const form = document.getElementById('addUserForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch('/api/admin/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showNotification('User created successfully', 'success');
            closeModal('addUserModal');
            window.adminDashboard.loadUsers();
        } else {
            showNotification('Failed to create user', 'error');
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

function viewUser(userId) {
    console.log('View user:', userId);
}

function editUser(userId) {
    console.log('Edit user:', userId);
}

function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/api/admin/users/${userId}`, { method: 'DELETE' })
            .then(() => {
                showNotification('User deleted', 'success');
                window.adminDashboard.loadUsers();
            });
    }
}

function searchUsers() {
    const search = document.getElementById('userSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#usersTableBody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(search) ? '' : 'none';
    });
}

function filterUsers() {
    const roleFilter = document.getElementById('userRoleFilter').value;
    const vipFilter = document.getElementById('userVipFilter').value;
    // Implement filtering logic
}

function saveSettings() {
    showNotification('Settings saved', 'success');
}

function exportLogs() {
    showNotification('Exporting logs...', 'info');
}

function showNotification(message, type = 'info') {
    if (window.dashboardInstance) {
        window.dashboardInstance.showNotification(message, type);
    }
}

// Toggle user menu
function toggleUserMenu() {
    const userMenu = document.querySelector('.user-menu');
    userMenu?.classList.toggle('active');
}

// Initialize Admin Dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
    console.log('✨ Admin Dashboard initialized');
});
