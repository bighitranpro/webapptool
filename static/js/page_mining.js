/**
 * ID Page Mining V1 Functions
 * Mine Facebook page IDs from user UIDs with filtering
 */

// Global state
const miningState = {
    isRunning: false,
    isPaused: false,
    startTime: null,
    timerInterval: null,
    uids: [],
    pages: [],
    stats: {
        total_uids: 0,
        processed_uids: 0,
        total_pages: 0,
        pages_with_ads: 0,
        verified_pages: 0,
        emails_collected: 0
    },
    filters: {
        has_ads: false,
        country: '',
        verified: false
    }
};

/**
 * Load UIDs from file
 */
function miningLoadFile() {
    document.getElementById('miningFileInput').click();
}

/**
 * Handle file upload
 */
function miningHandleFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        document.getElementById('miningUidInput').value = content;
        const lines = content.split('\n').filter(l => l.trim());
        showNotification(`Đã tải ${lines.length} UIDs từ file`, 'success');
    };
    reader.readAsText(file);
}

/**
 * Clear input
 */
function miningClearInput() {
    if (confirm('Xóa toàn bộ UID đã nhập?')) {
        document.getElementById('miningUidInput').value = '';
        showNotification('Đã xóa danh sách UID', 'info');
    }
}

/**
 * Parse UIDs from input
 */
function miningParseUIDs() {
    const input = document.getElementById('miningUidInput').value;
    const lines = input.split('\n');
    const uids = [];
    
    for (const line of lines) {
        const trimmed = line.trim();
        // Validate UID format (15-17 digits)
        if (trimmed && /^\d{15,17}$/.test(trimmed)) {
            uids.push(trimmed);
        }
    }
    
    return uids;
}

/**
 * Add log entry
 */
function miningAddLog(message, type = 'info') {
    const logDisplay = document.getElementById('miningLog');
    const time = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
    
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
function miningUpdateStats() {
    const stats = miningState.stats;
    
    // Processing stats
    document.getElementById('miningProcessed').textContent = stats.processed_uids;
    document.getElementById('miningPagesFound').textContent = stats.total_pages;
    
    // Calculate speed
    if (miningState.startTime) {
        const elapsed = (Date.now() - miningState.startTime) / 1000;
        const speed = elapsed > 0 ? Math.round(stats.processed_uids / elapsed) : 0;
        document.getElementById('miningSpeed').textContent = `${speed}/s`;
    }
    
    // Update progress bar
    const progress = stats.total_uids > 0 ? (stats.processed_uids / stats.total_uids * 100) : 0;
    const progressBar = document.getElementById('miningProgress');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
    
    // Results stats
    document.getElementById('miningTotalPages').textContent = stats.total_pages;
    document.getElementById('miningPagesWithAds').textContent = stats.pages_with_ads;
    document.getElementById('miningVerifiedPages').textContent = stats.verified_pages;
    document.getElementById('miningEmailsCollected').textContent = stats.emails_collected;
}

/**
 * Add page to results table
 */
function miningAddPageToTable(page) {
    const tbody = document.getElementById('miningTableBody');
    const row = document.createElement('tr');
    
    row.innerHTML = `
        <td>${page.page_id}</td>
        <td class="page-name" title="${page.page_name}">${page.page_name}</td>
        <td>${page.has_ads ? '<span class="badge-yes">Yes</span>' : '<span class="badge-no">No</span>'}</td>
        <td>${page.country || '-'}</td>
        <td>${page.verified ? '<i class="fas fa-check-circle" style="color: #3498db;"></i>' : '-'}</td>
        <td>${page.likes || 0}</td>
    `;
    
    tbody.appendChild(row);
}

/**
 * Start timer
 */
function miningStartTimer() {
    miningState.startTime = Date.now();
    
    miningState.timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - miningState.startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('miningRunningTime').textContent = timeStr;
    }, 1000);
}

/**
 * Stop timer
 */
function miningStopTimer() {
    if (miningState.timerInterval) {
        clearInterval(miningState.timerInterval);
        miningState.timerInterval = null;
    }
}

/**
 * Run page mining
 */
async function miningRun() {
    // Parse UIDs
    const uids = miningParseUIDs();
    
    if (uids.length === 0) {
        showNotification('Vui lòng nhập danh sách UID hợp lệ', 'error');
        return;
    }
    
    // Get filters
    const filterAds = document.getElementById('miningFilterAds').checked;
    const filterVerified = document.getElementById('miningFilterVerified').checked;
    const filterCountry = document.getElementById('miningFilterCountry').value;
    
    // Get proxy settings
    const proxyType = document.getElementById('miningProxyType').value;
    const proxyList = document.getElementById('miningProxyList').value;
    const threads = parseInt(document.getElementById('miningThreads').value);
    
    // Update state
    miningState.isRunning = true;
    miningState.isPaused = false;
    miningState.uids = uids;
    miningState.pages = [];
    miningState.stats = {
        total_uids: uids.length,
        processed_uids: 0,
        total_pages: 0,
        pages_with_ads: 0,
        verified_pages: 0,
        emails_collected: 0
    };
    miningState.filters = {
        has_ads: filterAds,
        country: filterCountry,
        verified: filterVerified
    };
    
    // Update UI
    document.getElementById('miningRunBtn').disabled = true;
    document.getElementById('miningStopBtn').disabled = false;
    document.getElementById('miningStatus').textContent = 'ĐANG KHAI THÁC..';
    document.getElementById('miningStatus').classList.add('running');
    
    // Clear previous results
    document.getElementById('miningLog').innerHTML = '';
    document.getElementById('miningTableBody').innerHTML = '';
    
    // Count proxies
    const proxies = proxyList.split('\n').filter(l => l.trim());
    document.getElementById('miningTotalProxy').textContent = proxies.length;
    
    // Start timer
    miningStartTimer();
    miningUpdateStats();
    
    miningAddLog(`Bắt đầu khai thác ${uids.length} UIDs`, 'info');
    miningAddLog(`Filters: Ads=${filterAds}, Verified=${filterVerified}, Country=${filterCountry || 'All'}`, 'info');
    miningAddLog(`Proxy: ${proxyType}, Threads: ${threads}`, 'info');
    
    // Prepare request
    const requestData = {
        uids: uids,
        options: {
            filter_has_ads: filterAds,
            filter_country: filterCountry === 'all' ? '' : filterCountry,
            filter_verified: filterVerified,
            max_workers: threads,
            proxy_config: proxies.length > 0 ? {
                enabled: true,
                type: proxyType,
                proxies: proxies
            } : null
        }
    };
    
    try {
        miningAddLog('Đang gửi request đến server...', 'info');
        
        const response = await fetch(`${API_BASE}/page-mining`, {
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
            miningState.pages = data.pages;
            miningState.stats = {
                total_uids: data.stats.total_uids,
                processed_uids: data.stats.total_uids,
                total_pages: data.stats.total_pages,
                pages_with_ads: data.stats.pages_with_ads,
                verified_pages: data.stats.verified_pages,
                emails_collected: data.stats.emails_collected
            };
            
            miningUpdateStats();
            
            // Display pages in table
            data.pages.forEach(page => miningAddPageToTable(page));
            
            miningAddLog(`✅ Hoàn thành! Tìm thấy ${data.stats.total_pages} pages`, 'success');
            miningAddLog(`Pages có Ads: ${data.stats.pages_with_ads}, Verified: ${data.stats.verified_pages}`, 'info');
            miningAddLog(`Emails thu thập: ${data.stats.emails_collected}`, 'info');
            miningAddLog(`Thời gian: ${data.stats.processing_time}s`, 'info');
            
            showNotification(`✅ Khai thác hoàn tất! Tìm thấy ${data.stats.total_pages} pages`, 'success');
            
            // Log activity to activity feed
            if (typeof window.logActivity === 'function') {
                window.logActivity({
                    type: 'page_mining',
                    title: 'Page Mining Complete',
                    description: `Tìm thấy ${data.stats.total_pages} pages - Emails: ${data.stats.emails_collected}`,
                    status: 'success',
                    icon: 'fas fa-gem',
                    color: 'purple',
                    metadata: {
                        total_pages: data.stats.total_pages,
                        pages_with_ads: data.stats.pages_with_ads,
                        verified_pages: data.stats.verified_pages,
                        emails_collected: data.stats.emails_collected,
                        processing_time: data.stats.processing_time
                    }
                });
            }
        } else {
            throw new Error(data.message || 'Unknown error');
        }
        
    } catch (error) {
        miningAddLog(`❌ Lỗi: ${error.message}`, 'error');
        showNotification(`Lỗi: ${error.message}`, 'error');
    } finally {
        miningStop();
    }
}

/**
 * Stop mining
 */
function miningStop() {
    miningState.isRunning = false;
    miningState.isPaused = false;
    
    miningStopTimer();
    
    document.getElementById('miningRunBtn').disabled = false;
    document.getElementById('miningStopBtn').disabled = true;
    document.getElementById('miningStatus').textContent = 'READY';
    document.getElementById('miningStatus').classList.remove('running');
}

/**
 * Pause mining
 */
function miningPause() {
    if (miningState.isPaused) {
        miningState.isPaused = false;
        document.getElementById('miningPauseBtn').innerHTML = '<i class="fas fa-pause"></i> TẠM DỪNG';
        miningAddLog('Tiếp tục khai thác...', 'info');
    } else {
        miningState.isPaused = true;
        document.getElementById('miningPauseBtn').innerHTML = '<i class="fas fa-play"></i> TIẾP TỤC';
        miningAddLog('Đã tạm dừng', 'warning');
    }
}

/**
 * Export results to TXT
 */
function miningExportTXT() {
    if (miningState.pages.length === 0) {
        showNotification('Chưa có kết quả để export', 'info');
        return;
    }
    
    let content = `ID Page Mining Results\n`;
    content += `Generated: ${new Date().toLocaleString()}\n`;
    content += `Total UIDs: ${miningState.stats.total_uids}\n`;
    content += `Total Pages: ${miningState.stats.total_pages}\n`;
    content += `Pages with Ads: ${miningState.stats.pages_with_ads}\n`;
    content += `Verified Pages: ${miningState.stats.verified_pages}\n`;
    content += `Emails Collected: ${miningState.stats.emails_collected}\n\n`;
    
    content += `=== PAGE LIST ===\n`;
    miningState.pages.forEach((page, index) => {
        content += `${index + 1}. ${page.page_name}\n`;
        content += `   Page ID: ${page.page_id}\n`;
        content += `   URL: ${page.page_url}\n`;
        content += `   Owner UID: ${page.uid_owner}\n`;
        content += `   Has Ads: ${page.has_ads ? 'Yes' : 'No'}\n`;
        content += `   Country: ${page.country || 'N/A'}\n`;
        content += `   Verified: ${page.verified ? 'Yes' : 'No'}\n`;
        content += `   Likes: ${page.likes || 0}\n`;
        if (page.email) {
            content += `   Email: ${page.email}\n`;
        }
        if (page.domain_email) {
            content += `   Domain Email: ${page.domain_email}\n`;
        }
        content += `\n`;
    });
    
    // Create download
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `page_mining_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Đã export TXT', 'success');
}

/**
 * Export results to CSV
 */
function miningExportCSV() {
    if (miningState.pages.length === 0) {
        showNotification('Chưa có kết quả để export', 'info');
        return;
    }
    
    // CSV header
    let csv = 'Page ID,Page Name,URL,Owner UID,Has Ads,Country,Verified,Likes,Email,Domain Email\n';
    
    // CSV rows
    miningState.pages.forEach(page => {
        const row = [
            page.page_id,
            `"${page.page_name.replace(/"/g, '""')}"`, // Escape quotes in name
            page.page_url,
            page.uid_owner,
            page.has_ads ? 'Yes' : 'No',
            page.country || '',
            page.verified ? 'Yes' : 'No',
            page.likes || 0,
            page.email || '',
            page.domain_email || ''
        ];
        csv += row.join(',') + '\n';
    });
    
    // Create download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `page_mining_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Đã export CSV', 'success');
}

/**
 * Copy Page IDs to clipboard
 */
function miningCopyPageIDs() {
    if (miningState.pages.length === 0) {
        showNotification('Chưa có kết quả', 'info');
        return;
    }
    
    const pageIds = miningState.pages.map(p => p.page_id).join('\n');
    
    navigator.clipboard.writeText(pageIds).then(() => {
        showNotification(`Đã copy ${miningState.pages.length} Page IDs`, 'success');
    }).catch(err => {
        showNotification('Lỗi copy: ' + err.message, 'error');
    });
}

/**
 * Copy Emails to clipboard
 */
function miningCopyEmails() {
    const emails = miningState.pages
        .filter(p => p.email)
        .map(p => p.email)
        .join('\n');
    
    if (!emails) {
        showNotification('Không có email nào', 'info');
        return;
    }
    
    navigator.clipboard.writeText(emails).then(() => {
        showNotification(`Đã copy ${miningState.stats.emails_collected} emails`, 'success');
    }).catch(err => {
        showNotification('Lỗi copy: ' + err.message, 'error');
    });
}

/**
 * Copy Domain Emails to clipboard
 */
function miningCopyDomainEmails() {
    const domainEmails = miningState.pages
        .filter(p => p.domain_email)
        .map(p => p.domain_email)
        .join('\n');
    
    if (!domainEmails) {
        showNotification('Không có domain email nào', 'info');
        return;
    }
    
    navigator.clipboard.writeText(domainEmails).then(() => {
        const count = miningState.pages.filter(p => p.domain_email).length;
        showNotification(`Đã copy ${count} domain emails`, 'success');
    }).catch(err => {
        showNotification('Lỗi copy: ' + err.message, 'error');
    });
}

console.log('Page Mining functions loaded');
