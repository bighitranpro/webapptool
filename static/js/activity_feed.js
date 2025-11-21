/**
 * Activity Feed Manager
 * Handles dynamic activity loading and real-time updates
 */

class ActivityFeedManager {
    constructor() {
        this.activities = [];
        this.autoRefresh = true;
        this.refreshInterval = 30000; // 30 seconds
        this.init();
    }

    init() {
        this.loadActivities();
        this.loadStats();
        this.setupEventListeners();
        
        if (this.autoRefresh) {
            this.startAutoRefresh();
        }
    }

    setupEventListeners() {
        // View all button
        const viewAllBtn = document.querySelector('.view-all-btn');
        if (viewAllBtn) {
            viewAllBtn.addEventListener('click', () => this.showAllActivities());
        }

        // Refresh on stats card click
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('click', () => {
                this.loadStats();
                this.animateStatCard(card);
            });
        });
    }

    async loadActivities() {
        try {
            const response = await fetch('/api/activities/recent?limit=5');
            const data = await response.json();
            
            if (data.success && data.activities) {
                this.activities = data.activities;
                this.renderActivities();
            }
        } catch (error) {
            console.error('Failed to load activities:', error);
        }
    }

    renderActivities() {
        const activityList = document.querySelector('.activity-list');
        if (!activityList) return;

        if (this.activities.length === 0) {
            activityList.innerHTML = this.renderEmptyState();
            return;
        }

        activityList.innerHTML = '';
        
        this.activities.forEach((activity, index) => {
            const activityElement = this.createActivityElement(activity, index);
            activityList.appendChild(activityElement);
        });
    }

    createActivityElement(activity, index) {
        const div = document.createElement('div');
        div.className = 'activity-item';
        div.style.animation = `fadeInUp 0.5s ease-out ${index * 0.1}s backwards`;
        
        const colorClass = this.getColorClass(activity.color);
        const statusClass = this.getStatusClass(activity.status);
        const timeAgo = this.formatTimeAgo(activity.time);
        
        div.innerHTML = `
            <div class="activity-icon ${colorClass}">
                <i class="fas ${activity.icon}"></i>
            </div>
            <div class="activity-details">
                <div class="activity-title">${this.escapeHtml(activity.title)}</div>
                <div class="activity-time">${this.escapeHtml(activity.description)} • ${timeAgo}</div>
            </div>
            <span class="activity-status ${statusClass}">${this.getStatusText(activity.status)}</span>
        `;
        
        return div;
    }

    getColorClass(color) {
        const colorMap = {
            'blue': 'blue',
            'green': 'green',
            'purple': 'purple',
            'orange': 'orange',
            'red': 'red',
            'teal': 'teal'
        };
        return colorMap[color] || 'blue';
    }

    getStatusClass(status) {
        const statusMap = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };
        return statusMap[status] || 'success';
    }

    getStatusText(status) {
        const textMap = {
            'success': 'Thành công',
            'error': 'Lỗi',
            'warning': 'Cảnh báo',
            'info': 'Thông tin'
        };
        return textMap[status] || 'Thành công';
    }

    formatTimeAgo(timestamp) {
        if (!timestamp || timestamp === 'Vài phút trước') return 'Vài phút trước';
        
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'Vừa xong';
            if (diffMins < 60) return `${diffMins} phút trước`;
            if (diffHours < 24) return `${diffHours} giờ trước`;
            if (diffDays < 7) return `${diffDays} ngày trước`;
            return date.toLocaleDateString('vi-VN');
        } catch (e) {
            return 'Vài phút trước';
        }
    }

    renderEmptyState() {
        return `
            <div class="activity-empty-state">
                <i class="fas fa-inbox" style="font-size: 48px; color: var(--text-muted); opacity: 0.5;"></i>
                <p style="margin-top: 16px; color: var(--text-muted);">Chưa có hoạt động nào</p>
                <p style="font-size: 14px; color: var(--text-muted); opacity: 0.7;">
                    Bắt đầu sử dụng các công cụ để xem lịch sử hoạt động
                </p>
            </div>
        `;
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats/summary');
            const data = await response.json();
            
            if (data.success && data.stats) {
                this.updateStatsDisplay(data.stats);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        // Update live emails
        const liveValue = document.getElementById('liveEmails');
        if (liveValue) {
            this.animateNumber(liveValue, parseInt(liveValue.textContent) || 0, stats.live_emails);
        }

        // Update die emails
        const dieValue = document.getElementById('dieEmails');
        if (dieValue) {
            this.animateNumber(dieValue, parseInt(dieValue.textContent) || 0, stats.die_emails);
        }

        // Update total
        const totalValue = document.getElementById('totalEmails');
        if (totalValue) {
            this.animateNumber(totalValue, parseInt(totalValue.textContent) || 0, stats.total_validated);
        }

        // Update can receive code
        const codeValue = document.getElementById('canReceiveCode');
        if (codeValue) {
            this.animateNumber(codeValue, parseInt(codeValue.textContent) || 0, stats.can_receive_code);
        }

        // Update progress bars
        this.updateProgressBars(stats);
    }

    animateNumber(element, from, to, duration = 1000) {
        const start = Date.now();
        const diff = to - from;
        
        const animate = () => {
            const now = Date.now();
            const progress = Math.min((now - start) / duration, 1);
            const easeOutQuad = progress * (2 - progress);
            const current = Math.floor(from + (diff * easeOutQuad));
            
            element.textContent = current.toLocaleString('vi-VN');
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    updateProgressBars(stats) {
        const total = stats.total_validated || 1;
        
        // Live progress
        const liveProgress = document.getElementById('liveProgress');
        if (liveProgress) {
            const livePercent = Math.round((stats.live_emails / total) * 100);
            liveProgress.style.width = livePercent + '%';
        }

        // Die progress
        const dieProgress = document.getElementById('dieProgress');
        if (dieProgress) {
            const diePercent = Math.round((stats.die_emails / total) * 100);
            dieProgress.style.width = diePercent + '%';
        }

        // Total progress
        const totalProgress = document.getElementById('totalProgress');
        if (totalProgress) {
            totalProgress.style.width = '100%';
        }

        // Code progress
        const codeProgress = document.getElementById('codeProgress');
        if (codeProgress) {
            const codePercent = Math.round((stats.can_receive_code / total) * 100);
            codeProgress.style.width = codePercent + '%';
        }
    }

    animateStatCard(card) {
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 150);
    }

    async logActivity(activityData) {
        try {
            const response = await fetch('/api/activities/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(activityData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Reload activities
                await this.loadActivities();
            }
        } catch (error) {
            console.error('Failed to log activity:', error);
        }
    }

    showAllActivities() {
        // Implement modal or redirect to activities page
        window.location.href = '/activities';
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.loadActivities();
            this.loadStats();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Add CSS for empty state
const style = document.createElement('style');
style.textContent = `
    .activity-empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        text-align: center;
    }
    
    .activity-item {
        opacity: 0;
        transform: translateY(20px);
    }
    
    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stat-card {
        cursor: pointer;
        transition: transform 0.15s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.activityFeed = new ActivityFeedManager();
});

// Export for use in other modules
window.logActivity = function(data) {
    if (window.activityFeed) {
        window.activityFeed.logActivity(data);
    }
};
