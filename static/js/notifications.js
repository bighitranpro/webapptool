/**
 * Toast Notification System
 * Beautiful, non-intrusive notifications
 */

// Create notification container
const createNotificationContainer = () => {
    if (document.getElementById('notificationContainer')) return;
    
    const container = document.createElement('div');
    container.id = 'notificationContainer';
    container.className = 'notification-container';
    document.body.appendChild(container);
};

// Show notification
window.showNotification = (message, type = 'info', duration = 3000) => {
    createNotificationContainer();
    
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const icon = icons[type] || icons.info;
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas ${icon}"></i>
        </div>
        <div class="notification-content">
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto remove
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
};

// Progress notification (for long operations)
window.showProgressNotification = (message, progress = 0) => {
    createNotificationContainer();
    
    const container = document.getElementById('notificationContainer');
    let notification = document.getElementById('progressNotification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'progressNotification';
        notification.className = 'notification notification-progress show';
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-spinner fa-spin"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${message}</div>
                <div class="notification-progress">
                    <div class="notification-progress-bar" style="width: ${progress}%"></div>
                </div>
                <div class="notification-progress-text">${progress}%</div>
            </div>
        `;
        container.appendChild(notification);
    } else {
        notification.querySelector('.notification-message').textContent = message;
        notification.querySelector('.notification-progress-bar').style.width = progress + '%';
        notification.querySelector('.notification-progress-text').textContent = progress + '%';
    }
    
    if (progress >= 100) {
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 1000);
    }
};

// Confirm dialog
window.confirmDialog = (message, onConfirm, onCancel) => {
    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    
    const dialog = document.createElement('div');
    dialog.className = 'confirm-dialog';
    dialog.innerHTML = `
        <div class="confirm-header">
            <i class="fas fa-question-circle"></i>
            <h3>Xác nhận</h3>
        </div>
        <div class="confirm-body">
            <p>${message}</p>
        </div>
        <div class="confirm-actions">
            <button class="btn btn-secondary" id="confirmCancel">
                <i class="fas fa-times"></i> Hủy
            </button>
            <button class="btn btn-primary" id="confirmOk">
                <i class="fas fa-check"></i> Xác nhận
            </button>
        </div>
    `;
    
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    
    // Animate in
    setTimeout(() => {
        overlay.classList.add('show');
    }, 10);
    
    // Event handlers
    const remove = () => {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    };
    
    dialog.querySelector('#confirmOk').onclick = () => {
        remove();
        if (onConfirm) onConfirm();
    };
    
    dialog.querySelector('#confirmCancel').onclick = () => {
        remove();
        if (onCancel) onCancel();
    };
    
    overlay.onclick = (e) => {
        if (e.target === overlay) {
            remove();
            if (onCancel) onCancel();
        }
    };
};

// Loading overlay
window.showLoading = (message = 'Đang xử lý...') => {
    let overlay = document.getElementById('loadingOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-message">${message}</div>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.querySelector('.loading-message').textContent = message;
    }
    
    setTimeout(() => overlay.classList.add('show'), 10);
};

window.hideLoading = () => {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }
};

// Add styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10001;
        pointer-events: none;
    }
    
    .notification {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 15px 20px;
        background: var(--card-bg, #12172e);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin-bottom: 10px;
        min-width: 300px;
        max-width: 400px;
        opacity: 0;
        transform: translateX(400px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        pointer-events: all;
        border-left: 4px solid;
    }
    
    .notification.show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .notification-success {
        border-left-color: #2ecc71;
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, transparent 100%);
    }
    
    .notification-error {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, transparent 100%);
    }
    
    .notification-warning {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, rgba(243, 156, 18, 0.1) 0%, transparent 100%);
    }
    
    .notification-info {
        border-left-color: #3498db;
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, transparent 100%);
    }
    
    .notification-icon {
        font-size: 24px;
    }
    
    .notification-success .notification-icon {
        color: #2ecc71;
    }
    
    .notification-error .notification-icon {
        color: #e74c3c;
    }
    
    .notification-warning .notification-icon {
        color: #f39c12;
    }
    
    .notification-info .notification-icon {
        color: #3498db;
    }
    
    .notification-content {
        flex: 1;
    }
    
    .notification-message {
        color: var(--text-primary, #ffffff);
        font-size: 14px;
        font-weight: 500;
    }
    
    .notification-progress {
        height: 4px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 2px;
        margin-top: 8px;
        overflow: hidden;
    }
    
    .notification-progress-bar {
        height: 100%;
        background: var(--gradient-gold);
        transition: width 0.3s ease;
    }
    
    .notification-progress-text {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 4px;
        transition: color 0.2s;
    }
    
    .notification-close:hover {
        color: var(--text-primary);
    }
    
    /* Confirm Dialog */
    .confirm-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        z-index: 10002;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .confirm-overlay.show {
        opacity: 1;
    }
    
    .confirm-dialog {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 0;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
        transform: scale(0.9);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .confirm-overlay.show .confirm-dialog {
        transform: scale(1);
    }
    
    .confirm-header {
        padding: 20px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .confirm-header i {
        font-size: 28px;
        color: var(--accent-gold);
    }
    
    .confirm-header h3 {
        margin: 0;
        color: var(--text-primary);
        font-size: 20px;
    }
    
    .confirm-body {
        padding: 20px;
    }
    
    .confirm-body p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 15px;
        line-height: 1.6;
    }
    
    .confirm-actions {
        padding: 20px;
        border-top: 1px solid var(--border-color);
        display: flex;
        gap: 10px;
        justify-content: flex-end;
    }
    
    /* Loading Overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        z-index: 10003;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .loading-overlay.show {
        opacity: 1;
    }
    
    .loading-content {
        text-align: center;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(243, 156, 18, 0.2);
        border-top-color: var(--accent-gold);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-message {
        color: var(--text-primary);
        font-size: 16px;
        font-weight: 500;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .notification-container {
            left: 10px;
            right: 10px;
            top: 10px;
        }
        
        .notification {
            min-width: auto;
            max-width: none;
        }
        
        .confirm-dialog {
            width: 95%;
        }
    }
`;

document.head.appendChild(notificationStyles);

console.log('✅ Notification System loaded successfully');
