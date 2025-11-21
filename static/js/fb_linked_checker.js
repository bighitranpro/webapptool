/**
 * FB Email Linked Checker Functions
 * Complete implementation for Facebook email link verification
 */

// Global state for FB Checker
const fbCheckerState = {
    isRunning: false,
    isPaused: false,
    startTime: null,
    timerInterval: null,
    emails: [],
    results: {
        linked: [],
        hidden_linked: [],
        not_linked: [],
        error: []
    },
    stats: {
        total: 0,
        processed: 0,
        linked: 0,
        hidden_linked: 0,
        not_linked: 0,
        error: 0,
        code6: 0,
        code8: 0
    }
};

/**
 * Load emails from file
 */
function fbLoadFromFile() {
    document.getElementById('fbFileInput').click();
}

/**
 * Handle file upload
 */
function fbHandleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        document.getElementById('fbEmailInput').value = content;
        showNotification(`Đã tải ${content.split('\n').filter(l => l.trim()).length} emails từ file`, 'success');
    };
    reader.readAsText(file);
}

/**
 * Clear input
 */
function fbClearInput() {
    if (confirm('Xóa toàn bộ email đã nhập?')) {
        document.getElementById('fbEmailInput').value = '';
        showNotification('Đã xóa danh sách email', 'info');
    }
}

/**
 * Parse emails from input
 */
function fbParseEmails() {
    const input = document.getElementById('fbEmailInput').value;
    const lines = input.split('\n');
    const emails = [];
    
    for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed && trimmed.includes('@')) {
            emails.push(trimmed);
        }
    }
    
    return emails;
}

/**
 * Parse proxy list
 */
function fbParseProxies() {
    const input = document.getElementById('fbProxyList').value;
    if (!input.trim()) return [];
    
    const lines = input.split('\n');
    const proxies = [];
    
    for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed) {
            proxies.push(trimmed);
        }
    }
    
    return proxies;
}

/**
 * Add log entry
 */
function fbAddLog(message, type = 'info') {
    const logDisplay = document.getElementById('fbLogDisplay');
    const time = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-message">${message}</span>
    `;
    
    logDisplay.appendChild(logEntry);
    logDisplay.scrollTop = logDisplay.scrollHeight;
    
    // Keep only last 100 entries
    while (logDisplay.children.length > 100) {
        logDisplay.removeChild(logDisplay.firstChild);
    }
}

/**
 * Update statistics display
 */
function fbUpdateStats() {
    const stats = fbCheckerState.stats;
    
    // Update counts
    document.getElementById('fbTotalEmails').textContent = stats.total;
    document.getElementById('fbDataProcessed').textContent = stats.processed;
    document.getElementById('fbProcessed').textContent = stats.processed;
    document.getElementById('fbRemaining').textContent = stats.total - stats.processed;
    
    // Update results
    document.getElementById('fbLinkedCount').textContent = stats.linked;
    document.getElementById('fbHiddenCount').textContent = stats.hidden_linked;
    document.getElementById('fbNotLinkedCount').textContent = stats.not_linked;
    document.getElementById('fbErrorCount').textContent = stats.error;
    
    // Update code stats
    document.getElementById('fbCode6Count').textContent = stats.code6;
    document.getElementById('fbCode8Count').textContent = stats.code8;
    
    // Update progress bar
    const progress = stats.total > 0 ? (stats.processed / stats.total * 100) : 0;
    document.getElementById('fbProgressBar').style.width = `${progress}%`;
    document.getElementById('fbProgressText').textContent = `${Math.round(progress)}%`;
    
    // Calculate speed
    if (fbCheckerState.startTime) {
        const elapsed = (Date.now() - fbCheckerState.startTime) / 1000;
        const speed = elapsed > 0 ? Math.round(stats.processed / elapsed) : 0;
        document.getElementById('fbSpeed').textContent = `${speed}/s`;
    }
}

/**
 * Start timer
 */
function fbStartTimer() {
    fbCheckerState.startTime = Date.now();
    
    fbCheckerState.timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - fbCheckerState.startTime) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        
        const timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('fbRunningTime').textContent = timeStr;
    }, 1000);
}

/**
 * Stop timer
 */
function fbStopTimer() {
    if (fbCheckerState.timerInterval) {
        clearInterval(fbCheckerState.timerInterval);
        fbCheckerState.timerInterval = null;
    }
}

/**
 * Start checking
 */
async function fbStartChecking() {
    // Parse emails
    const emails = fbParseEmails();
    if (emails.length === 0) {
        showNotification('Vui lòng nhập danh sách email', 'error');
        return;
    }
    
    // Get settings
    const apiType = document.getElementById('fbApiType').value;
    const proxyType = document.getElementById('fbProxyType').value;
    const proxies = fbParseProxies();
    const mailsPerProxy = parseInt(document.getElementById('fbMailsPerProxy').value);
    const proxyUsage = document.getElementById('fbProxyUsage').value;
    const startFrom = parseInt(document.getElementById('fbStartFrom').value) - 1;
    const threads = parseInt(document.getElementById('fbThreads').value);
    
    // Validate
    if (startFrom < 0 || startFrom >= emails.length) {
        showNotification('Số thứ tự bắt đầu không hợp lệ', 'error');
        return;
    }
    
    // Reset state
    fbCheckerState.isRunning = true;
    fbCheckerState.isPaused = false;
    fbCheckerState.emails = emails;
    fbCheckerState.results = {
        linked: [],
        hidden_linked: [],
        not_linked: [],
        error: []
    };
    fbCheckerState.stats = {
        total: emails.length,
        processed: 0,
        linked: 0,
        hidden_linked: 0,
        not_linked: 0,
        error: 0,
        code6: 0,
        code8: 0
    };
    
    // Update UI
    document.getElementById('fbRunBtn').disabled = true;
    document.getElementById('fbPauseBtn').disabled = false;
    document.getElementById('fbTotalProxies').textContent = proxies.length;
    
    // Clear logs
    document.getElementById('fbLogDisplay').innerHTML = '';
    
    // Start timer
    fbStartTimer();
    
    // Add starting log
    fbAddLog(`Bắt đầu kiểm tra ${emails.length} emails với API: ${apiType}`, 'info');
    fbAddLog(`Số luồng: ${threads}, Proxy: ${proxyType}`, 'info');
    
    // Prepare request
    const requestData = {
        emails: emails,
        options: {
            api_type: apiType,
            proxy_config: proxies.length > 0 ? {
                enabled: true,
                type: proxyType,
                proxies: proxies,
                mails_per_proxy: mailsPerProxy,
                usage: proxyUsage
            } : null,
            max_workers: threads,
            start_from: startFrom
        }
    };
    
    try {
        fbAddLog('Đang gửi request đến server...', 'info');
        document.getElementById('fbActiveThreads').textContent = threads;
        
        const response = await fetch(`${API_BASE}/fb-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update results
            fbCheckerState.results = data.results;
            fbCheckerState.stats = {
                total: data.stats.total,
                processed: data.stats.total,
                linked: data.stats.linked,
                hidden_linked: data.stats.hidden_linked,
                not_linked: data.stats.not_linked,
                error: data.stats.error,
                code6: data.stats.code6_count || 0,
                code8: data.stats.code8_count || 0
            };
            
            fbUpdateStats();
            
            fbAddLog(`✅ Hoàn thành! Tìm thấy ${data.stats.linked} LINKED, ${data.stats.hidden_linked} HIDDEN`, 'success');
            fbAddLog(`Thời gian xử lý: ${data.stats.processing_time}s`, 'info');
            
            showNotification('Kiểm tra hoàn tất!', 'success');
            
            // Log activity to activity feed
            if (typeof window.logActivity === 'function') {
                window.logActivity({
                    type: 'facebook_check',
                    title: 'Facebook Link Check',
                    description: `Đã kiểm tra ${data.stats.total} emails - LINKED: ${data.stats.linked}, HIDDEN: ${data.stats.hidden_linked}`,
                    status: 'success',
                    icon: 'fab fa-facebook',
                    color: 'blue',
                    metadata: {
                        total: data.stats.total,
                        linked: data.stats.linked,
                        hidden_linked: data.stats.hidden_linked,
                        not_linked: data.stats.not_linked,
                        error: data.stats.error,
                        code6: data.stats.code6_count || 0,
                        code8: data.stats.code8_count || 0,
                        processing_time: data.stats.processing_time,
                        api_type: apiType
                    }
                });
            }
        } else {
            throw new Error(data.message || 'Unknown error');
        }
        
    } catch (error) {
        fbAddLog(`❌ Lỗi: ${error.message}`, 'error');
        showNotification(`Lỗi: ${error.message}`, 'error');
    } finally {
        fbStopChecking();
    }
}

/**
 * Pause checking
 */
function fbPauseChecking() {
    if (fbCheckerState.isPaused) {
        fbCheckerState.isPaused = false;
        document.getElementById('fbPauseBtn').innerHTML = '<i class="fas fa-pause"></i> TẠM DỪNG';
        fbAddLog('Tiếp tục kiểm tra...', 'info');
    } else {
        fbCheckerState.isPaused = true;
        document.getElementById('fbPauseBtn').innerHTML = '<i class="fas fa-play"></i> TIẾP TỤC';
        fbAddLog('Đã tạm dừng', 'warning');
    }
}

/**
 * Stop checking
 */
function fbStopChecking() {
    fbCheckerState.isRunning = false;
    fbCheckerState.isPaused = false;
    
    fbStopTimer();
    
    document.getElementById('fbRunBtn').disabled = false;
    document.getElementById('fbPauseBtn').disabled = true;
    document.getElementById('fbActiveThreads').textContent = '0';
}

/**
 * View results in modal
 */
function fbViewResults(category) {
    const results = fbCheckerState.results[category];
    
    if (!results || results.length === 0) {
        showNotification(`Không có kết quả ${category}`, 'info');
        return;
    }
    
    // Create result display
    let content = `<h3>Kết quả ${category.toUpperCase()}</h3><ul style="max-height: 400px; overflow-y: auto;">`;
    
    results.forEach((result, index) => {
        content += `<li style="margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
            <strong>${index + 1}. ${result.email}</strong><br>
            <small>API: ${result.api_used} | Status: ${result.status}</small>`;
        
        if (result.code_length) {
            content += `<br><small>Code: ${result.code_length} digits</small>`;
        }
        
        if (result.phone) {
            content += `<br><small>Phone: ${result.phone}</small>`;
        }
        
        if (result.secondary_email) {
            content += `<br><small>Secondary: ${result.secondary_email}</small>`;
        }
        
        content += `</li>`;
    });
    
    content += '</ul>';
    
    // Show in alert (in real app, use a better modal)
    const detailWindow = window.open('', 'Results', 'width=600,height=700');
    detailWindow.document.write(`
        <html>
        <head>
            <title>FB Linked Checker Results</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h3 { color: #667eea; }
                ul { list-style: none; padding: 0; }
                li { margin-bottom: 10px; }
            </style>
        </head>
        <body>${content}</body>
        </html>
    `);
}

/**
 * Copy results to clipboard
 */
function fbCopyResults(category) {
    const results = fbCheckerState.results[category];
    
    if (!results || results.length === 0) {
        showNotification(`Không có kết quả ${category}`, 'info');
        return;
    }
    
    const emailList = results.map(r => r.email).join('\n');
    
    navigator.clipboard.writeText(emailList).then(() => {
        showNotification(`Đã copy ${results.length} emails ${category}`, 'success');
    }).catch(err => {
        showNotification('Lỗi copy: ' + err.message, 'error');
    });
}

/**
 * Export results to file
 */
function fbExportResults() {
    if (fbCheckerState.stats.processed === 0) {
        showNotification('Chưa có kết quả để export', 'info');
        return;
    }
    
    let content = `FB Email Linked Checker Results\n`;
    content += `Generated: ${new Date().toLocaleString()}\n`;
    content += `Total: ${fbCheckerState.stats.total}\n`;
    content += `Processed: ${fbCheckerState.stats.processed}\n\n`;
    
    // Linked
    content += `=== LINKED (${fbCheckerState.stats.linked}) ===\n`;
    fbCheckerState.results.linked.forEach(r => {
        content += `${r.email} | Code: ${r.code_length || 'N/A'}`;
        if (r.phone) content += ` | Phone: ${r.phone}`;
        content += '\n';
    });
    
    content += `\n=== HIDDEN LINKED (${fbCheckerState.stats.hidden_linked}) ===\n`;
    fbCheckerState.results.hidden_linked.forEach(r => {
        content += `${r.email} | Code: ${r.code_length || 'N/A'}\n`;
    });
    
    content += `\n=== NOT LINKED (${fbCheckerState.stats.not_linked}) ===\n`;
    fbCheckerState.results.not_linked.forEach(r => {
        content += `${r.email}\n`;
    });
    
    content += `\n=== ERROR (${fbCheckerState.stats.error}) ===\n`;
    fbCheckerState.results.error.forEach(r => {
        content += `${r.email} | Error: ${r.error || 'Unknown'}\n`;
    });
    
    // Create download
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fb_linked_results_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Đã export kết quả', 'success');
}

console.log('FB Linked Checker functions loaded');
