/**
 * Dashboard Management
 * Handle dashboard statistics and updates
 */

// Global state
const dashboardState = {
    stats: {
        total: 0,
        live: 0,
        die: 0,
        canReceiveCode: 0
    },
    liveEmails: [],
    dieEmails: []
};

/**
 * Update dashboard statistics
 */
function updateDashboardStats(data) {
    if (data.stats) {
        dashboardState.stats = {
            total: data.stats.total || 0,
            live: data.stats.live || 0,
            die: data.stats.die || 0,
            canReceiveCode: data.stats.can_receive_code || 0
        };
    }
    
    // Update UI
    document.getElementById('totalEmails').textContent = dashboardState.stats.total;
    document.getElementById('liveEmails').textContent = dashboardState.stats.live;
    document.getElementById('dieEmails').textContent = dashboardState.stats.die;
    document.getElementById('canReceiveCode').textContent = dashboardState.stats.canReceiveCode;
    
    // Calculate percentages
    const total = dashboardState.stats.total;
    if (total > 0) {
        const livePercent = ((dashboardState.stats.live / total) * 100).toFixed(1);
        const diePercent = ((dashboardState.stats.die / total) * 100).toFixed(1);
        const codePercent = ((dashboardState.stats.canReceiveCode / total) * 100).toFixed(1);
        
        document.getElementById('livePercent').textContent = `${livePercent}%`;
        document.getElementById('diePercent').textContent = `${diePercent}%`;
        document.getElementById('codePercent').textContent = `${codePercent}%`;
    }
}

/**
 * Update LIVE emails table
 */
function updateLiveEmailsTable(emails) {
    dashboardState.liveEmails = emails;
    const tbody = document.getElementById('liveEmailsBody');
    const countBadge = document.getElementById('liveCount');
    
    countBadge.textContent = emails.length;
    
    if (emails.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Chưa có dữ liệu</td></tr>';
        return;
    }
    
    tbody.innerHTML = emails.map((item, index) => {
        const email = typeof item === 'string' ? item : item.email;
        const domain = email.split('@')[1] || '';
        const canReceive = item.can_receive_code ? 'Có' : 'Không';
        
        return `
            <tr>
                <td>${index + 1}</td>
                <td>${email}</td>
                <td>${domain}</td>
                <td><span class="badge badge-live">LIVE</span></td>
                <td>${canReceive}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Update DIE emails table
 */
function updateDieEmailsTable(emails) {
    dashboardState.dieEmails = emails;
    const tbody = document.getElementById('dieEmailsBody');
    const countBadge = document.getElementById('dieCount');
    
    countBadge.textContent = emails.length;
    
    if (emails.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Chưa có dữ liệu</td></tr>';
        return;
    }
    
    tbody.innerHTML = emails.map((item, index) => {
        const email = typeof item === 'string' ? item : item.email;
        const domain = email.split('@')[1] || '';
        const reason = item.details ? item.details.join(', ') : 'Invalid';
        
        return `
            <tr>
                <td>${index + 1}</td>
                <td>${email}</td>
                <td>${domain}</td>
                <td>${reason}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Copy email list to clipboard
 */
function copyList(tableId) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    const emails = [];
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 1) {
            emails.push(cells[1].textContent);
        }
    });
    
    if (emails.length === 0) {
        showNotification('Không có email để copy', 'warning');
        return;
    }
    
    const text = emails.join('\n');
    navigator.clipboard.writeText(text).then(() => {
        showNotification(`Đã copy ${emails.length} emails`, 'success');
    }).catch(err => {
        showNotification('Lỗi khi copy', 'error');
        console.error('Copy failed:', err);
    });
}

/**
 * Export email list to file
 */
function exportList(tableId, filename) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    const emails = [];
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length > 1) {
            emails.push(cells[1].textContent);
        }
    });
    
    if (emails.length === 0) {
        showNotification('Không có email để export', 'warning');
        return;
    }
    
    const text = emails.join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification(`Đã export ${emails.length} emails`, 'success');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideInRight 0.3s;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

/**
 * Load dashboard data from database on page load
 */
async function loadDashboardData() {
    try {
        const response = await fetch('/api/db/stats');
        const data = await response.json();
        
        if (data.success && data.stats) {
            // Update dashboard stats
            updateDashboardStats({ stats: data.stats });
            
            // Update LIVE table
            if (data.live_emails && data.live_emails.length > 0) {
                updateLiveEmailsTable(data.live_emails);
            }
            
            // Update DIE table
            if (data.die_emails && data.die_emails.length > 0) {
                updateDieEmailsTable(data.die_emails);
            }
            
            console.log('Dashboard data loaded successfully');
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Silent fail - don't show notification on initial load
    }
}
