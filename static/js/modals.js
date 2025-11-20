/**
 * Modal Management
 * Handle opening, closing, and interactions with modals
 */

/**
 * Open modal by ID
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

/**
 * Close modal by ID
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

/**
 * Close modal when clicking outside
 */
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
};

/**
 * Close modal on ESC key
 */
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
        document.body.style.overflow = 'auto';
    }
});

/**
 * Parse emails from textarea
 */
function parseEmails(text) {
    return text.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
}

/**
 * Display result in container
 */
function displayResult(containerId, data, type = 'success') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = '';
    
    if (type === 'error') {
        html = `
            <div class="alert alert-error">
                <i class="fas fa-exclamation-circle"></i>
                <strong>Lỗi:</strong> ${data.message || data}
            </div>
        `;
    } else if (type === 'success') {
        if (data.emails && Array.isArray(data.emails)) {
            html = `
                <div class="result-summary">
                    <h4><i class="fas fa-check-circle"></i> Kết quả</h4>
                    <p>Tổng số: <strong>${data.emails.length}</strong> emails</p>
                </div>
                <div class="result-list">
                    <textarea readonly rows="10">${data.emails.join('\n')}</textarea>
                </div>
                <button onclick="copyResultText('${containerId}')" class="btn btn-primary">
                    <i class="fas fa-copy"></i> Copy kết quả
                </button>
            `;
        } else {
            html = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        }
    }
    
    container.innerHTML = html;
}

/**
 * Copy result text to clipboard
 */
function copyResultText(containerId) {
    const container = document.getElementById(containerId);
    const textarea = container.querySelector('textarea');
    if (textarea) {
        textarea.select();
        document.execCommand('copy');
        showNotification('Đã copy kết quả', 'success');
    }
}

/**
 * Show/hide loading indicator
 */
function toggleLoading(show, containerId, message = 'Đang xử lý...') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (show) {
        container.innerHTML = `
            <div class="loading-indicator">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }
}

// Add spinner CSS
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
    .loading-indicator {
        text-align: center;
        padding: 40px;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto 20px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .alert {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    .alert-error {
        background: #fee;
        border-left: 4px solid #e74c3c;
        color: #c0392b;
    }
    
    .result-summary {
        background: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 4px solid #2ecc71;
    }
    
    .result-list textarea {
        width: 100%;
        font-family: 'Courier New', monospace;
        margin: 15px 0;
    }
`;
document.head.appendChild(spinnerStyle);
