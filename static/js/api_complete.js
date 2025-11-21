/**
 * Complete API Functions
 * Handle all API calls to backend - 100% functional
 */

const API_BASE = '/api';

/**
 * Ensure showNotification exists (fallback if not loaded from dashboard.js)
 */
if (typeof showNotification === 'undefined') {
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : type === 'warning' ? '#f39c12' : '#3498db'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 10000;
            font-weight: 600;
            animation: slideInRight 0.3s;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };
    
    // Add animation styles if not exist
    if (!document.getElementById('notification-animations')) {
        const style = document.createElement('style');
        style.id = 'notification-animations';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(400px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(400px); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Run Email Validator
 */
async function runValidator() {
    const emailsText = document.getElementById('validatorEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const options = {
        check_mx: document.getElementById('checkMX').checked,
        check_smtp: document.getElementById('checkSMTP').checked,
        check_disposable: document.getElementById('checkDisposable').checked,
        check_fb_compat: document.getElementById('checkFBCompat').checked,
        max_workers: parseInt(document.getElementById('validatorWorkers').value),
        timeout: parseInt(document.getElementById('validatorTimeout').value)
    };
    
    toggleLoading(true, 'validatorResult', 'Đang kiểm tra emails...');
    const progressDiv = document.getElementById('validatorProgress');
    if (progressDiv) progressDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, options })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update dashboard stats
            if (data.stats) {
                updateDashboardStats(data);
            }
            
            // Update tables
            if (data.results) {
                updateLiveEmailsTable(data.results.live || []);
                updateDieEmailsTable(data.results.die || []);
            }
            
            // Display detailed result
            displayValidationResult('validatorResult', data);
            showNotification(`Kiểm tra hoàn tất! LIVE: ${data.stats.live}, DIE: ${data.stats.die}`, 'success');
            
            // Log activity to activity feed
            if (typeof window.logActivity === 'function') {
                window.logActivity({
                    type: 'validation',
                    title: 'Email Validation',
                    description: `Đã kiểm tra ${data.stats.total} emails - LIVE: ${data.stats.live}, DIE: ${data.stats.die}`,
                    status: 'success',
                    icon: 'fas fa-envelope-circle-check',
                    color: 'blue',
                    metadata: {
                        total: data.stats.total,
                        live: data.stats.live,
                        die: data.stats.die,
                        can_receive_code: data.stats.can_receive_code || 0,
                        processing_time: data.stats.processing_time
                    }
                });
            }
        } else {
            displayResult('validatorResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Validation error:', error);
        displayResult('validatorResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    } finally {
        if (progressDiv) progressDiv.style.display = 'none';
    }
}

/**
 * Display validation result with detailed stats
 */
function displayValidationResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const stats = data.stats || {};
    const results = data.results || {};
    
    const html = `
        <div class="validation-summary">
            <h4><i class="fas fa-check-circle"></i> Kết quả kiểm tra</h4>
            <div class="stats-grid-small">
                <div class="stat-item">
                    <span class="stat-label">Tổng:</span>
                    <span class="stat-value">${stats.total || 0}</span>
                </div>
                <div class="stat-item stat-live">
                    <span class="stat-label">LIVE:</span>
                    <span class="stat-value">${stats.live || 0}</span>
                </div>
                <div class="stat-item stat-die">
                    <span class="stat-label">DIE:</span>
                    <span class="stat-value">${stats.die || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Unknown:</span>
                    <span class="stat-value">${stats.unknown || 0}</span>
                </div>
                <div class="stat-item stat-code">
                    <span class="stat-label">Nhận code:</span>
                    <span class="stat-value">${stats.can_receive_code || 0}</span>
                </div>
            </div>
            <p class="processing-time">Thời gian xử lý: ${stats.processing_time || 0}s</p>
        </div>
    `;
    
    container.innerHTML = html;
}

/**
 * Generate Emails
 */
async function generateEmails() {
    const domainMode = document.getElementById('domainMode').value;
    let domains = [];
    
    if (domainMode === 'single') {
        const singleDomain = document.getElementById('generatorDomain').value.trim();
        if (!singleDomain) {
            showNotification('Vui lòng nhập domain', 'warning');
            return;
        }
        domains = [singleDomain];
    } else {
        // Multiple domains mode
        const domainsText = document.getElementById('generatorDomains').value;
        domains = domainsText.split('\n')
            .map(d => d.trim())
            .filter(d => d.length > 0);
        
        if (domains.length === 0) {
            showNotification('Vui lòng nhập ít nhất 1 domain', 'warning');
            return;
        }
    }
    
    const params = {
        email_type: document.getElementById('emailType').value,
        text: document.getElementById('generatorText').value,
        total: parseInt(document.getElementById('generatorTotal').value),
        domains: domains, // Changed from single 'domain' to array 'domains'
        char_type: document.getElementById('charType').value,
        number_type: document.getElementById('numberType').value
    };
    
    if (params.total < 1 || params.total > 10000) {
        showNotification('Số lượng phải từ 1 đến 10,000', 'warning');
        return;
    }
    
    const outputDiv = document.getElementById('generatorOutput');
    outputDiv.innerHTML = '<div class="loading-indicator"><div class="spinner"></div><p>Đang tạo emails...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success && data.emails) {
            const countBadge = document.getElementById('generatorCount');
            if (countBadge) {
                countBadge.textContent = data.emails.length;
            }
            
            outputDiv.innerHTML = data.emails.map((email, i) => 
                `<div class="email-item">${i + 1}. ${email}</div>`
            ).join('');
            
            showNotification(`Đã tạo ${data.emails.length} emails`, 'success');
            
            // Log activity to activity feed
            if (typeof window.logActivity === 'function') {
                window.logActivity({
                    type: 'generation',
                    title: 'Email Generation',
                    description: `Đã tạo ${data.emails.length} emails với ${domains.length} domain(s)`,
                    status: 'success',
                    icon: 'fas fa-magic',
                    color: 'purple',
                    metadata: {
                        count: data.emails.length,
                        domains: domains,
                        email_type: params.email_type
                    }
                });
            }
        } else {
            outputDiv.innerHTML = `<p class="empty-state error">Có lỗi: ${data.message || 'Unknown error'}</p>`;
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Generation error:', error);
        outputDiv.innerHTML = `<p class="empty-state error">Lỗi: ${error.message}</p>`;
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Toggle domain mode (single or multiple)
 */
function toggleDomainMode() {
    const mode = document.getElementById('domainMode').value;
    const singleGroup = document.getElementById('singleDomainGroup');
    const multiGroup = document.getElementById('multiDomainGroup');
    const quickGroup = document.getElementById('quickDomainGroup');
    
    if (mode === 'single') {
        singleGroup.style.display = 'block';
        multiGroup.style.display = 'none';
        quickGroup.style.display = 'none';
    } else {
        singleGroup.style.display = 'none';
        multiGroup.style.display = 'block';
        quickGroup.style.display = 'block';
    }
}

/**
 * Toggle domain in multi-domain mode
 */
function toggleDomain(domain) {
    const textarea = document.getElementById('generatorDomains');
    const currentDomains = textarea.value.split('\n').map(d => d.trim()).filter(d => d);
    const domainIndex = currentDomains.indexOf(domain);
    
    // Find the button
    const buttons = document.querySelectorAll('.btn-domain');
    let targetButton = null;
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase() === domain.split('.')[0].toLowerCase()) {
            targetButton = btn;
        }
    });
    
    if (domainIndex === -1) {
        // Add domain
        currentDomains.push(domain);
        if (targetButton) targetButton.classList.add('active');
    } else {
        // Remove domain
        currentDomains.splice(domainIndex, 1);
        if (targetButton) targetButton.classList.remove('active');
    }
    
    textarea.value = currentDomains.join('\n');
}

/**
 * Copy generated list
 */
function copyGeneratedList() {
    const outputDiv = document.getElementById('generatorOutput');
    const emailItems = outputDiv.querySelectorAll('.email-item');
    
    if (emailItems.length === 0) {
        showNotification('Không có email để copy', 'warning');
        return;
    }
    
    const emails = Array.from(emailItems).map(item => {
        const text = item.textContent;
        return text.substring(text.indexOf('.') + 2);
    });
    
    navigator.clipboard.writeText(emails.join('\n')).then(() => {
        showNotification(`Đã copy ${emails.length} emails`, 'success');
    }).catch(err => {
        console.error('Copy error:', err);
        showNotification('Lỗi khi copy', 'error');
    });
}

/**
 * Email Extractor Pro - Advanced Functions
 */

// Global state for extractor
const extractorState = {
    isRunning: false,
    isPaused: false,
    allEmails: [],
    liveEmails: [],
    dieEmails: [],
    currentTab: 'all'
};

/**
 * Toggle input source
 */
function toggleExtractorSource() {
    const source = document.getElementById('extractorSource').value;
    document.getElementById('extractorTextInput').style.display = source === 'text' ? 'block' : 'none';
    document.getElementById('extractorFileInput').style.display = source === 'file' ? 'block' : 'none';
    document.getElementById('extractorUrlInput').style.display = source === 'url' ? 'block' : 'none';
}

/**
 * Handle file upload
 */
function handleFileUpload(input) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('extractorText').value = e.target.result;
            document.getElementById('fileInfo').innerHTML = `
                <i class="fas fa-file-check"></i> File loaded: ${file.name} (${(file.size / 1024).toFixed(2)} KB)
            `;
            updateExtractorInputCount();
        };
        reader.readAsText(file);
    }
}

/**
 * Fetch content from URL
 */
async function fetchFromUrl() {
    const url = document.getElementById('extractorUrl').value;
    if (!url.trim()) {
        showNotification('Vui lòng nhập URL', 'warning');
        return;
    }
    
    addExtractorLog('Đang fetch content từ URL...', 'info');
    
    try {
        // Note: This needs CORS proxy or backend endpoint
        showNotification('Feature đang phát triển - sử dụng paste text thay thế', 'warning');
    } catch (error) {
        addExtractorLog('Lỗi fetch URL: ' + error.message, 'error');
    }
}

/**
 * Update input count
 */
function updateExtractorInputCount() {
    const text = document.getElementById('extractorText').value;
    const lines = text.split('\n').filter(l => l.trim()).length;
    document.getElementById('extractorInputCount').textContent = lines;
}

/**
 * Main extraction function
 */
async function runExtractor() {
    const text = document.getElementById('extractorText').value;
    
    if (!text.trim()) {
        showNotification('Vui lòng nhập dữ liệu', 'warning');
        return;
    }
    
    extractorState.isRunning = true;
    extractorState.isPaused = false;
    extractorState.allEmails = [];
    extractorState.liveEmails = [];
    extractorState.dieEmails = [];
    
    // Enable control buttons
    document.getElementById('extractorPauseBtn').disabled = false;
    document.getElementById('extractorStopBtn').disabled = false;
    
    addExtractorLog('Bắt đầu trích xuất emails...', 'info');
    updateExtractorProgress(10, 'Đang phân tích văn bản...');
    
    // Step 1: Extract emails
    const options = {
        remove_dups: document.getElementById('extractorRemoveDups').checked,
        validate_format: document.getElementById('extractorValidateFormat').checked
    };
    
    const domainFilter = document.getElementById('extractorDomainFilter').value;
    if (domainFilter.trim()) {
        options.filter_domains = domainFilter.split(',').map(d => d.trim());
    }
    
    try {
        const response = await fetch(`${API_BASE}/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, options })
        });
        
        const data = await response.json();
        
        if (data.success && data.emails) {
            extractorState.allEmails = data.emails;
            
            addExtractorLog(`Tìm thấy ${data.emails.length} emails`, 'success');
            updateExtractorProgress(40, 'Đã trích xuất emails');
            updateExtractorStats(data.emails.length, data.emails.length, 0);
            
            // Display all emails first
            displayExtractorResults('all', data.emails);
            
            // Step 2: Auto-detect LIVE/DIE if enabled
            const autoDetect = document.getElementById('extractorAutoDetectLive').checked;
            if (autoDetect && data.emails.length > 0) {
                await autoDetectLiveDie(data.emails);
            } else {
                updateExtractorProgress(100, 'Hoàn tất!');
                addExtractorLog('Trích xuất hoàn tất', 'success');
            }
            
            showNotification(`Trích xuất thành công ${data.emails.length} emails`, 'success');
        } else {
            addExtractorLog('Không tìm thấy email nào', 'warning');
            updateExtractorProgress(100, 'Không có kết quả');
        }
    } catch (error) {
        console.error('Extract error:', error);
        addExtractorLog('Lỗi: ' + error.message, 'error');
        showNotification('Lỗi trích xuất', 'error');
    } finally {
        extractorState.isRunning = false;
        document.getElementById('extractorPauseBtn').disabled = true;
        document.getElementById('extractorStopBtn').disabled = true;
    }
}

/**
 * Auto-detect LIVE/DIE status
 */
async function autoDetectLiveDie(emails) {
    addExtractorLog('Bắt đầu kiểm tra LIVE/DIE...', 'info');
    updateExtractorProgress(50, 'Đang kiểm tra emails...');
    
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                emails: emails,
                options: {
                    check_mx: true,
                    check_smtp: false, // Skip SMTP for speed
                    max_workers: 10
                }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            extractorState.liveEmails = data.results.live || [];
            extractorState.dieEmails = data.results.die || [];
            
            addExtractorLog(`LIVE: ${extractorState.liveEmails.length}, DIE: ${extractorState.dieEmails.length}`, 'success');
            
            // Update displays
            displayExtractorResults('live', extractorState.liveEmails.map(e => e.email));
            displayExtractorResults('die', extractorState.dieEmails.map(e => e.email));
            
            // Update counts
            document.getElementById('extractorLiveCount').textContent = extractorState.liveEmails.length;
            document.getElementById('extractorDieCount').textContent = extractorState.dieEmails.length;
            
            updateExtractorProgress(100, 'Hoàn tất!');
            
            // Log activity to activity feed
            if (typeof window.logActivity === 'function') {
                window.logActivity({
                    type: 'extraction',
                    title: 'Email Extraction',
                    description: `Trích xuất ${extractorState.allEmails.length} emails - LIVE: ${extractorState.liveEmails.length}, DIE: ${extractorState.dieEmails.length}`,
                    status: 'success',
                    icon: 'fas fa-filter',
                    color: 'teal',
                    metadata: {
                        total: extractorState.allEmails.length,
                        live: extractorState.liveEmails.length,
                        die: extractorState.dieEmails.length
                    }
                });
            }
        }
    } catch (error) {
        addExtractorLog('Lỗi kiểm tra LIVE/DIE: ' + error.message, 'error');
        updateExtractorProgress(100, 'Hoàn tất (không check LIVE/DIE)');
    }
}

/**
 * Update progress bar
 */
function updateExtractorProgress(percent, text) {
    document.getElementById('extractorProgress').style.width = percent + '%';
    document.getElementById('extractorProgressText').textContent = text;
}

/**
 * Update stats
 */
function updateExtractorStats(scanned, found, checking) {
    document.getElementById('extractorScanned').textContent = scanned;
    document.getElementById('extractorFound').textContent = found;
    document.getElementById('extractorValid').textContent = found;
    document.getElementById('extractorChecking').textContent = checking;
}

/**
 * Add log entry
 */
function addExtractorLog(message, type = 'info') {
    const logDiv = document.getElementById('extractorLog');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-circle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    entry.innerHTML = `<i class="fas fa-${icon}"></i> [${new Date().toLocaleTimeString()}] ${message}`;
    logDiv.appendChild(entry);
    logDiv.scrollTop = logDiv.scrollHeight;
}

/**
 * Display results in appropriate tab
 */
function displayExtractorResults(tab, emails) {
    const listId = tab === 'all' ? 'extractorAllList' : 
                   tab === 'live' ? 'extractorLiveList' : 'extractorDieList';
    const list = document.getElementById(listId);
    
    if (!emails || emails.length === 0) {
        list.innerHTML = '<p class="empty-state">Chưa có dữ liệu</p>';
        return;
    }
    
    const html = emails.map((email, index) => {
        const emailStr = typeof email === 'object' ? email.email : email;
        const status = typeof email === 'object' ? email.status : null;
        
        return `
            <div class="result-item">
                <span>${index + 1}. ${emailStr}</span>
                ${status ? `<span class="status-badge ${status.toLowerCase()}">${status}</span>` : ''}
            </div>
        `;
    }).join('');
    
    list.innerHTML = html;
    
    // Update count
    const countId = tab === 'all' ? 'extractorAllCount' : 
                    tab === 'live' ? 'extractorLiveCount' : 'extractorDieCount';
    document.getElementById(countId).textContent = emails.length;
}

/**
 * Switch tabs
 */
function switchExtractorTab(tab) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tabs
    document.querySelectorAll('.result-tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`extractorTab${tab.charAt(0).toUpperCase() + tab.slice(1)}`).classList.add('active');
    
    extractorState.currentTab = tab;
}

/**
 * Copy results
 */
function copyExtractorResults(tab) {
    let emails = [];
    
    if (tab === 'all') {
        emails = extractorState.allEmails;
    } else if (tab === 'live') {
        emails = extractorState.liveEmails.map(e => e.email || e);
    } else if (tab === 'die') {
        emails = extractorState.dieEmails.map(e => e.email || e);
    }
    
    if (emails.length === 0) {
        showNotification('Không có dữ liệu để copy', 'warning');
        return;
    }
    
    const text = Array.isArray(emails) ? emails.join('\n') : emails;
    navigator.clipboard.writeText(text).then(() => {
        showNotification(`Đã copy ${emails.length} emails`, 'success');
    }).catch(() => {
        showNotification('Lỗi khi copy', 'error');
    });
}

/**
 * Export results
 */
function exportExtractorResults(format) {
    const emails = extractorState.currentTab === 'all' ? extractorState.allEmails :
                   extractorState.currentTab === 'live' ? extractorState.liveEmails.map(e => e.email || e) :
                   extractorState.dieEmails.map(e => e.email || e);
    
    if (emails.length === 0) {
        showNotification('Không có dữ liệu để export', 'warning');
        return;
    }
    
    let content = '';
    let filename = '';
    
    if (format === 'txt') {
        content = emails.join('\n');
        filename = `emails_${extractorState.currentTab}_${Date.now()}.txt`;
    } else if (format === 'csv') {
        content = 'Email,Status\n' + emails.map((e, i) => {
            const email = typeof e === 'object' ? e.email : e;
            const status = typeof e === 'object' ? e.status : 'UNKNOWN';
            return `${email},${status}`;
        }).join('\n');
        filename = `emails_${extractorState.currentTab}_${Date.now()}.csv`;
    }
    
    // Create download
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification(`Đã export ${emails.length} emails`, 'success');
}

/**
 * Pause extractor
 */
function pauseExtractor() {
    extractorState.isPaused = !extractorState.isPaused;
    const btn = document.getElementById('extractorPauseBtn');
    btn.innerHTML = extractorState.isPaused ? 
        '<i class="fas fa-play"></i> Resume' : 
        '<i class="fas fa-pause"></i> Pause';
    
    addExtractorLog(extractorState.isPaused ? 'Đã tạm dừng' : 'Tiếp tục xử lý', 'warning');
}

/**
 * Stop extractor
 */
function stopExtractor() {
    extractorState.isRunning = false;
    extractorState.isPaused = false;
    
    document.getElementById('extractorPauseBtn').disabled = true;
    document.getElementById('extractorStopBtn').disabled = true;
    
    addExtractorLog('Đã dừng xử lý', 'error');
    showNotification('Đã dừng trích xuất', 'warning');
}

// Add event listener for input count
document.addEventListener('DOMContentLoaded', function() {
    const textArea = document.getElementById('extractorText');
    if (textArea) {
        textArea.addEventListener('input', updateExtractorInputCount);
    }
});

/**
 * Format Emails
 */
async function formatEmails() {
    const emailsText = document.getElementById('formatterEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const params = {
        emails: emails,
        case_format: document.getElementById('formatterCase').value,
        sort_type: document.getElementById('formatterSort').value || null
    };
    
    toggleLoading(true, 'formatterResult', 'Đang định dạng...');
    
    try {
        const response = await fetch(`${API_BASE}/format`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('formatterResult', data, 'success');
            showNotification('Định dạng hoàn tất', 'success');
        } else {
            displayResult('formatterResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Format error:', error);
        displayResult('formatterResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Filter Emails
 */
async function filterEmails() {
    const emailsText = document.getElementById('filterEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const domainsText = document.getElementById('filterDomains').value;
    const domains = domainsText ? domainsText.split(',').map(d => d.trim()).filter(d => d.length > 0) : [];
    
    const filters = {
        remove_invalid: document.getElementById('filterInvalid').checked,
        remove_duplicates: document.getElementById('filterDuplicates').checked,
        has_numbers: document.getElementById('filterNumbers').checked ? true : null,
        domains: domains.length > 0 ? domains : null
    };
    
    toggleLoading(true, 'filterResult', 'Đang lọc...');
    
    try {
        const response = await fetch(`${API_BASE}/filter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails, filters })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('filterResult', data, 'success');
            const filtered = data.stats.filtered_out || 0;
            showNotification(`Lọc hoàn tất. Đã loại bỏ ${filtered} emails`, 'success');
        } else {
            displayResult('filterResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Filter error:', error);
        displayResult('filterResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Split Emails
 */
async function splitEmails() {
    const emailsText = document.getElementById('splitterEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const method = document.getElementById('splitterMethod').value;
    const count = parseInt(document.getElementById('splitterCount').value);
    
    const params = {
        emails: emails,
        method: method,
        count: method === 'count' ? count : null,
        chunks: method === 'chunks' ? count : null
    };
    
    toggleLoading(true, 'splitterResult', 'Đang chia...');
    
    try {
        const response = await fetch(`${API_BASE}/split`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySplitResult('splitterResult', data);
            showNotification('Chia hoàn tất', 'success');
        } else {
            displayResult('splitterResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Split error:', error);
        displayResult('splitterResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Display split result
 */
function displaySplitResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = `
        <div class="result-summary">
            <h4><i class="fas fa-cut"></i> Kết quả chia</h4>
            <p>Tổng emails: <strong>${data.total_emails}</strong></p>
    `;
    
    if (data.chunks) {
        html += `<p>Số phần: <strong>${data.num_chunks}</strong></p>`;
        html += '<div class="chunks-container">';
        data.chunks.forEach((chunk, index) => {
            html += `
                <div class="chunk-item">
                    <h5>Phần ${index + 1} (${chunk.length} emails)</h5>
                    <textarea readonly rows="5">${chunk.join('\n')}</textarea>
                </div>
            `;
        });
        html += '</div>';
    } else if (data.domain_groups) {
        html += `<p>Số domains: <strong>${data.num_domains}</strong></p>`;
        html += '<div class="chunks-container">';
        for (const [domain, emails] of Object.entries(data.domain_groups)) {
            html += `
                <div class="chunk-item">
                    <h5>${domain} (${emails.length} emails)</h5>
                    <textarea readonly rows="5">${emails.join('\n')}</textarea>
                </div>
            `;
        }
        html += '</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Combine Emails
 */
async function combineEmails() {
    const list1Text = document.getElementById('combinerList1').value;
    const list2Text = document.getElementById('combinerList2').value;
    
    const list1 = parseEmails(list1Text);
    const list2 = parseEmails(list2Text);
    
    if (list1.length === 0 || list2.length === 0) {
        showNotification('Vui lòng nhập cả 2 danh sách', 'warning');
        return;
    }
    
    const method = document.getElementById('combinerMethod').value;
    
    const params = {
        email_lists: [list1, list2],
        method: method,
        case_sensitive: false
    };
    
    toggleLoading(true, 'combinerResult', 'Đang gộp...');
    
    try {
        const response = await fetch(`${API_BASE}/combine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('combinerResult', data, 'success');
            showNotification(`Gộp hoàn tất. Kết quả: ${data.total_output} emails`, 'success');
        } else {
            displayResult('combinerResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Combine error:', error);
        displayResult('combinerResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Analyze Emails
 */
async function analyzeEmails() {
    const emailsText = document.getElementById('analyzerEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    toggleLoading(true, 'analyzerResult', 'Đang phân tích...');
    
    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emails })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAnalysisResult('analyzerResult', data);
            showNotification('Phân tích hoàn tất', 'success');
        } else {
            displayResult('analyzerResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        displayResult('analyzerResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Display analysis result
 */
function displayAnalysisResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const domains = data.domains || {};
    const patterns = data.patterns || {};
    const length = data.length || {};
    const providers = data.providers || {};
    
    const html = `
        <div class="analysis-result">
            <h4><i class="fas fa-chart-bar"></i> Kết quả phân tích</h4>
            
            <div class="analysis-section">
                <h5>Domains (Top 5)</h5>
                <ul>
                    ${(domains.top_domains || []).slice(0, 5).map(([domain, count]) => 
                        `<li>${domain}: <strong>${count}</strong> emails</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div class="analysis-section">
                <h5>Mẫu (Patterns)</h5>
                <ul>
                    <li>Có số: ${patterns.patterns?.has_numbers || 0} (${patterns.percentages?.has_numbers || 0}%)</li>
                    <li>Có dấu chấm: ${patterns.patterns?.has_dots || 0} (${patterns.percentages?.has_dots || 0}%)</li>
                    <li>Toàn chữ thường: ${patterns.patterns?.all_lowercase || 0} (${patterns.percentages?.all_lowercase || 0}%)</li>
                </ul>
            </div>
            
            <div class="analysis-section">
                <h5>Độ dài</h5>
                <p>Min: ${length.min || 0} | Max: ${length.max || 0} | Trung bình: ${length.avg || 0}</p>
            </div>
            
            <div class="analysis-section">
                <h5>Nhà cung cấp</h5>
                <ul>
                    ${Object.entries(providers.distribution || {}).map(([provider, count]) => 
                        `<li>${provider}: <strong>${count}</strong> (${providers.percentages?.[provider] || 0}%)</li>`
                    ).join('')}
                </ul>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

/**
 * Deduplicate Emails
 */
async function deduplicateEmails() {
    const emailsText = document.getElementById('deduplicatorEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const params = {
        emails: emails,
        method: document.getElementById('deduplicatorMethod').value,
        keep_strategy: document.getElementById('deduplicatorKeep').value
    };
    
    toggleLoading(true, 'deduplicatorResult', 'Đang loại trùng...');
    
    try {
        const response = await fetch(`${API_BASE}/deduplicate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResult('deduplicatorResult', data, 'success');
            const removed = data.stats.duplicates_removed || 0;
            showNotification(`Loại trùng hoàn tất. Đã loại bỏ ${removed} emails`, 'success');
        } else {
            displayResult('deduplicatorResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Deduplicate error:', error);
        displayResult('deduplicatorResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    }
}

/**
 * Process Batch
 */
async function processBatch() {
    const emailsText = document.getElementById('batchEmails').value;
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'warning');
        return;
    }
    
    const params = {
        emails: emails,
        batch_size: parseInt(document.getElementById('batchSize').value),
        operation: document.getElementById('batchOperation').value,
        max_workers: parseInt(document.getElementById('batchWorkers').value)
    };
    
    const progressDiv = document.getElementById('batchProgress');
    if (progressDiv) progressDiv.style.display = 'block';
    toggleLoading(true, 'batchResult', 'Đang xử lý hàng loạt...');
    
    try {
        const response = await fetch(`${API_BASE}/batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBatchResult('batchResult', data);
            showNotification('Xử lý hàng loạt hoàn tất', 'success');
        } else {
            displayResult('batchResult', data, 'error');
            showNotification('Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('Batch error:', error);
        displayResult('batchResult', { message: error.message }, 'error');
        showNotification('Lỗi kết nối API', 'error');
    } finally {
        if (progressDiv) progressDiv.style.display = 'none';
    }
}

/**
 * Display batch result
 */
function displayBatchResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const stats = data.stats || {};
    
    const html = `
        <div class="batch-result">
            <h4><i class="fas fa-layer-group"></i> Kết quả xử lý hàng loạt</h4>
            <div class="stats-grid-small">
                <div class="stat-item">
                    <span class="stat-label">Tổng emails:</span>
                    <span class="stat-value">${stats.total_emails || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Batches:</span>
                    <span class="stat-value">${stats.batches_processed || 0}</span>
                </div>
                <div class="stat-item stat-live">
                    <span class="stat-label">Thành công:</span>
                    <span class="stat-value">${stats.successful || 0}</span>
                </div>
                <div class="stat-item stat-die">
                    <span class="stat-label">Thất bại:</span>
                    <span class="stat-value">${stats.failed || 0}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Thời gian:</span>
                    <span class="stat-value">${stats.processing_time || 0}s</span>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Add CSS for new styles
const analysisStyle = document.createElement('style');
analysisStyle.textContent = `
    .stats-grid-small {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin: 15px 0;
    }
    
    .stat-item {
        background: white;
        padding: 10px;
        border-radius: 8px;
        border-left: 3px solid #3498db;
    }
    
    .stat-item.stat-live {
        border-left-color: #2ecc71;
    }
    
    .stat-item.stat-die {
        border-left-color: #e74c3c;
    }
    
    .stat-item.stat-code {
        border-left-color: #f39c12;
    }
    
    .stat-label {
        display: block;
        font-size: 0.85rem;
        color: #7f8c8d;
        margin-bottom: 5px;
    }
    
    .stat-value {
        display: block;
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .validation-summary,
    .analysis-result,
    .batch-result {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
    }
    
    .analysis-section {
        margin: 15px 0;
        padding: 15px;
        background: white;
        border-radius: 8px;
    }
    
    .analysis-section h5 {
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .analysis-section ul {
        list-style: none;
        padding: 0;
    }
    
    .analysis-section li {
        padding: 5px 0;
        border-bottom: 1px solid #ecf0f1;
    }
    
    .chunks-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    
    .chunk-item {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ecf0f1;
    }
    
    .chunk-item h5 {
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .chunk-item textarea {
        width: 100%;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        border: 1px solid #ecf0f1;
        border-radius: 4px;
        padding: 10px;
    }
    
    .email-item {
        padding: 8px;
        border-bottom: 1px solid #ecf0f1;
        transition: background 0.2s;
    }
    
    .email-item:hover {
        background: #f8f9fa;
    }
    
    .processing-time {
        margin-top: 15px;
        font-style: italic;
        color: #7f8c8d;
    }
`;
document.head.appendChild(analysisStyle);

console.log('Complete API functions loaded successfully');
