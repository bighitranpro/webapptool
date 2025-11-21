/**
 * BI GHI TOOL MMO - Professional Dashboard
 * Advanced interactive features and animations
 */

// Dashboard Configuration
const DashboardConfig = {
    updateInterval: 5000, // Update stats every 5 seconds
    animationDuration: 1000,
    chartColors: {
        live: '#2ecc71',
        die: '#e74c3c',
        total: '#3498db',
        code: '#9b59b6'
    }
};

// Initialize Dashboard
class Dashboard {
    constructor() {
        this.statsData = {
            live: 0,
            die: 0,
            total: 0,
            canReceiveCode: 0
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoUpdate();
        this.animateProgressBars();
        this.setupSearch();
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
            });
        }

        // Initialize collapsible sections
        this.initializeCollapsibleSections();

        // Mobile menu toggle
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }

        // User menu toggle
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserMenu();
            });
        }

        // Close menu when clicking outside
        document.addEventListener('click', () => {
            this.closeUserMenu();
        });

        // Navigation items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', function(e) {
                // Remove active from all
                document.querySelectorAll('.nav-item').forEach(nav => {
                    nav.classList.remove('active');
                });
                // Add active to clicked
                this.classList.add('active');
            });
        });

        // Search shortcut (Ctrl+K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.search-box input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
    }

    setupSearch() {
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
    }

    initializeCollapsibleSections() {
        // Load saved collapse states from localStorage
        const sections = ['email-tools', 'facebook-tools', 'advanced-tools'];
        
        sections.forEach(sectionId => {
            const isCollapsed = localStorage.getItem(`section-${sectionId}-collapsed`) === 'true';
            const section = document.querySelector(`[data-section="${sectionId}"]`);
            
            if (section && isCollapsed) {
                section.classList.add('collapsed');
            }
        });
    }

    handleSearch(query) {
        query = query.toLowerCase().trim();
        
        if (query.length === 0) {
            // Show all tools
            document.querySelectorAll('.tool-card').forEach(card => {
                card.style.display = 'block';
            });
            return;
        }

        // Filter tools
        document.querySelectorAll('.tool-card').forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const description = card.querySelector('.tool-description').textContent.toLowerCase();
            
            if (title.includes(query) || description.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    toggleUserMenu() {
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.classList.toggle('active');
        }
    }

    closeUserMenu() {
        const userMenu = document.querySelector('.user-menu');
        if (userMenu && userMenu.classList.contains('active')) {
            userMenu.classList.remove('active');
        }
    }

    async loadInitialData() {
        // Load stats from localStorage or API
        const savedStats = localStorage.getItem('dashboardStats');
        if (savedStats) {
            this.statsData = JSON.parse(savedStats);
            this.updateStatsDisplay();
        }

        // Try to fetch fresh data
        await this.fetchStats();
    }

    async fetchStats() {
        try {
            // Fetch real stats from API
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            
            if (data.success) {
                // Update stats data with real values
                this.statsData.live = data.stats.live_emails;
                this.statsData.die = data.stats.die_emails;
                this.statsData.total = data.stats.total_emails;
                this.statsData.canReceiveCode = data.stats.can_receive_code;
                this.statsData.successRate = data.stats.success_rate;
                this.statsData.todayCount = data.stats.today_count;
                this.statsData.weekCount = data.stats.week_count;
                
                // Update recent activity
                if (data.recent_activity && data.recent_activity.length > 0) {
                    this.updateRecentActivity(data.recent_activity);
                }
                
                this.updateStatsDisplay();
                this.saveStats();
                
                console.log('✅ Dashboard stats updated:', data.stats);
            } else {
                console.error('❌ Failed to fetch stats:', data.message);
                // Fallback to saved stats
                const savedStats = localStorage.getItem('dashboardStats');
                if (savedStats) {
                    this.statsData = JSON.parse(savedStats);
                    this.updateStatsDisplay();
                }
            }
        } catch (error) {
            console.error('❌ Network error fetching stats:', error);
            // Fallback to saved stats
            const savedStats = localStorage.getItem('dashboardStats');
            if (savedStats) {
                this.statsData = JSON.parse(savedStats);
                this.updateStatsDisplay();
            }
        }
    }

    updateStatsDisplay() {
        // Update stat values with animation
        this.animateCounter('liveEmails', this.statsData.live);
        this.animateCounter('dieEmails', this.statsData.die);
        this.animateCounter('totalEmails', this.statsData.total);
        this.animateCounter('canReceiveCode', this.statsData.canReceiveCode);

        // Update progress bars
        const total = this.statsData.total || 1;
        const livePercentage = (this.statsData.live / total) * 100;
        const diePercentage = (this.statsData.die / total) * 100;
        const codePercentage = this.statsData.live > 0 ? (this.statsData.canReceiveCode / this.statsData.live) * 100 : 0;
        
        this.updateProgressBar('liveProgress', livePercentage);
        this.updateProgressBar('dieProgress', diePercentage);
        this.updateProgressBar('totalProgress', 100);
        this.updateProgressBar('codeProgress', codePercentage);
        
        // Update stat card footer values with real data
        if (this.statsData.successRate !== undefined) {
            const successRateEl = document.querySelector('.stat-card:nth-child(1) .stat-footer-value');
            if (successRateEl) {
                successRateEl.textContent = this.statsData.successRate.toFixed(1) + '%';
            }
        }
        
        if (this.statsData.successRate !== undefined) {
            const failureRate = (100 - this.statsData.successRate).toFixed(1);
            const failureRateEl = document.querySelector('.stat-card:nth-child(2) .stat-footer-value');
            if (failureRateEl) {
                failureRateEl.textContent = failureRate + '%';
            }
        }
        
        if (this.statsData.weekCount !== undefined) {
            const weekCountEl = document.querySelector('.stat-card:nth-child(3) .stat-footer-value');
            if (weekCountEl) {
                weekCountEl.textContent = this.statsData.weekCount.toLocaleString();
            }
        }
        
        if (this.statsData.canReceiveCode && this.statsData.live) {
            const codeReadyPercent = ((this.statsData.canReceiveCode / this.statsData.live) * 100).toFixed(0);
            const codeReadyEl = document.querySelector('.stat-card:nth-child(4) .stat-footer-value');
            if (codeReadyEl) {
                codeReadyEl.textContent = codeReadyPercent + '%';
            }
        }
    }
    
    updateRecentActivity(activities) {
        // Update recent activity section with real data
        const activityList = document.querySelector('.activity-list');
        if (!activityList || activities.length === 0) return;
        
        // Clear existing mock activities
        activityList.innerHTML = '';
        
        // Add real activities (show up to 5)
        activities.slice(0, 5).forEach((activity, index) => {
            const timeAgo = this.getTimeAgo(activity.timestamp);
            const statusClass = activity.status === 'LIVE' ? 'success' : 'danger';
            const iconClass = activity.status === 'LIVE' ? 'fa-check-circle' : 'fa-times-circle';
            const iconColor = activity.status === 'LIVE' ? 'green' : 'red';
            const codeText = activity.can_receive_code ? ' • Can receive code' : '';
            
            const activityHTML = `
                <div class="activity-item">
                    <div class="activity-icon ${iconColor}">
                        <i class="fas ${iconClass}"></i>
                    </div>
                    <div class="activity-details">
                        <div class="activity-title">Email Validation: ${activity.email}</div>
                        <div class="activity-time">Status: ${activity.status}${codeText} • ${timeAgo}</div>
                    </div>
                    <span class="activity-status ${statusClass}">${activity.status}</span>
                </div>
            `;
            
            activityList.innerHTML += activityHTML;
        });
    }
    
    getTimeAgo(timestamp) {
        // Convert timestamp to time ago format
        const now = new Date();
        const past = new Date(timestamp);
        const diffMs = now - past;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    }

    animateCounter(elementId, targetValue, duration = 1000) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - startValue) / (duration / 16);
        let currentValue = startValue;

        const updateCounter = () => {
            currentValue += increment;
            
            if ((increment > 0 && currentValue >= targetValue) || 
                (increment < 0 && currentValue <= targetValue)) {
                element.textContent = targetValue.toLocaleString();
            } else {
                element.textContent = Math.floor(currentValue).toLocaleString();
                requestAnimationFrame(updateCounter);
            }
        };

        requestAnimationFrame(updateCounter);
    }

    updateProgressBar(elementId, percentage) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Ensure percentage is between 0 and 100
        percentage = Math.min(100, Math.max(0, percentage));
        
        element.style.width = percentage + '%';
    }

    animateProgressBars() {
        // Initial animation on page load
        setTimeout(() => {
            document.querySelectorAll('.stat-progress-bar').forEach(bar => {
                const width = bar.style.width || '0%';
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 100);
            });
        }, 500);
    }

    startAutoUpdate() {
        // Update stats periodically
        setInterval(() => {
            this.fetchStats();
        }, DashboardConfig.updateInterval);
    }

    saveStats() {
        localStorage.setItem('dashboardStats', JSON.stringify(this.statsData));
    }

    // Tool Card Interactions
    openTool(toolName) {
        console.log('Opening tool:', toolName);
        // This will be handled by modals.js
    }

    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Toggle Section Function (Global)
function toggleSection(sectionId) {
    const section = document.querySelector(`[data-section="${sectionId}"]`);
    
    if (!section) return;
    
    // Toggle collapsed class
    section.classList.toggle('collapsed');
    
    // Save state to localStorage
    const isCollapsed = section.classList.contains('collapsed');
    localStorage.setItem(`section-${sectionId}-collapsed`, isCollapsed);
    
    // Add haptic feedback on mobile
    if (navigator.vibrate) {
        navigator.vibrate(10);
    }
}

// Logout Function
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            // Clear local storage
            localStorage.clear();
            sessionStorage.clear();
            
            // Show success message
            showNotification('Logged out successfully', 'success');
            
            // Redirect to login
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        } else {
            showNotification('Logout failed', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showNotification('Network error during logout', 'error');
        
        // Force redirect anyway
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }
}

// Global notification function
function showNotification(message, type = 'info') {
    if (window.dashboardInstance) {
        window.dashboardInstance.showNotification(message, type);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardInstance = new Dashboard();
    console.log('✨ BI GHI TOOL MMO Dashboard initialized');
});

// Expose to window for debugging
window.Dashboard = Dashboard;

// Show Full Guide Function
function showFullGuide() {
    // Open modal or redirect to documentation
    window.dashboardInstance.showNotification('Full documentation will be available soon!', 'info');
    // TODO: Implement full guide modal or link to external documentation
    return false;
}

// Upgrade VIP Function
function upgradeVIP(plan) {
    // Handle VIP upgrade
    window.dashboardInstance.showNotification(`Upgrading to ${plan.toUpperCase()} plan...`, 'info');
    // TODO: Implement payment/upgrade flow
    // This could redirect to payment page or open upgrade modal
    setTimeout(() => {
        window.dashboardInstance.showNotification('Payment integration coming soon!', 'warning');
    }, 1500);
}

// Notifications Panel Functions
function openNotificationsPanel() {
    const panel = document.getElementById('notificationsPanel');
    if (panel) {
        panel.classList.add('active');
        // Mark badge as read after opening
        setTimeout(() => {
            const badge = document.getElementById('notificationCount');
            if (badge) {
                badge.textContent = '';
                badge.style.display = 'none';
            }
        }, 500);
    }
}

function closeNotificationsPanel() {
    const panel = document.getElementById('notificationsPanel');
    if (panel) {
        panel.classList.remove('active');
    }
}

function markAllAsRead() {
    const unreadItems = document.querySelectorAll('.notification-item.unread');
    unreadItems.forEach(item => {
        item.classList.remove('unread');
        item.classList.add('read');
    });
    window.dashboardInstance.showNotification('All notifications marked as read', 'success');
}

// Settings Modal Functions
function openSettingsModal() {
    openModal('settingsModal');
}

function toggleAPIKeyVisibility() {
    const input = document.querySelector('.api-key-display input');
    const icon = document.querySelector('.toggle-visibility-btn i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

function copyAPIKey() {
    const input = document.querySelector('.api-key-display input');
    input.select();
    document.execCommand('copy');
    window.dashboardInstance.showNotification('API Key copied to clipboard!', 'success');
}

// Settings Tabs Handler
document.addEventListener('DOMContentLoaded', () => {
    const settingsTabs = document.querySelectorAll('.settings-tab');
    const settingsContents = document.querySelectorAll('.settings-tab-content');
    
    settingsTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active from all tabs
            settingsTabs.forEach(t => t.classList.remove('active'));
            settingsContents.forEach(c => c.classList.remove('active'));
            
            // Add active to clicked tab
            tab.classList.add('active');
            const tabName = tab.getAttribute('data-tab');
            const content = document.getElementById(tabName + 'Tab');
            if (content) {
                content.classList.add('active');
            }
        });
    });
});

// Add notification styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: var(--shadow-lg);
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 10000;
        min-width: 300px;
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification i {
        font-size: 20px;
    }

    .notification-success {
        border-left: 4px solid var(--success-green);
    }

    .notification-success i {
        color: var(--success-green);
    }

    .notification-error {
        border-left: 4px solid var(--danger-red);
    }

    .notification-error i {
        color: var(--danger-red);
    }

    .notification-warning {
        border-left: 4px solid var(--warning-orange);
    }

    .notification-warning i {
        color: var(--warning-orange);
    }

    .notification-info {
        border-left: 4px solid var(--info-blue);
    }

    .notification-info i {
        color: var(--info-blue);
    }

    .notification span {
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 500;
    }

    /* Sidebar collapsed state */
    .sidebar.collapsed {
        width: var(--sidebar-collapsed-width);
    }

    .sidebar.collapsed .logo-text,
    .sidebar.collapsed .nav-item span:not(.nav-badge),
    .sidebar.collapsed .nav-section-title,
    .sidebar.collapsed .user-plan div {
        display: none;
    }

    .sidebar.collapsed .nav-badge {
        position: absolute;
        top: 5px;
        right: 5px;
    }

    .sidebar.collapsed ~ .main-content {
        margin-left: var(--sidebar-collapsed-width);
    }

    /* User menu dropdown */
    .user-menu {
        position: relative;
        cursor: pointer;
    }

    .user-menu.active .user-dropdown {
        display: block;
        opacity: 1;
        transform: translateY(0);
    }

    .user-dropdown {
        display: none;
        opacity: 0;
        transform: translateY(-10px);
        position: absolute;
        top: 100%;
        right: 0;
        margin-top: 10px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        min-width: 200px;
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-fast);
        z-index: 1000;
    }

    .dropdown-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 15px;
        color: var(--text-secondary);
        transition: all var(--transition-fast);
        cursor: pointer;
    }

    .dropdown-item:hover {
        background: var(--primary-dark);
        color: var(--accent-gold);
    }

    .dropdown-divider {
        height: 1px;
        background: var(--border-color);
        margin: 5px 0;
    }
`;
document.head.appendChild(notificationStyles);
