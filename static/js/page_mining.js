/**
 * ID Page Mining V2 Enhanced Functions
 * Mine Facebook page IDs from user UIDs with advanced filtering and export
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
        total_pages_found: 0,
        pages_with_ads: 0,
        pages_verified: 0,
        emails_collected: 0,
        phones_collected: 0,
        websites_collected: 0,
        processing_time: 0,
        cache_hits: 0,
        api_calls: 0
    },
    filters: {
        has_ads: false,
        country: '',
        verified: false,
        category: '',
        min_likes: 0,
        has_email: false,
        has_phone: false,
        has_website: false
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
    document.getElementById('miningPagesFound').textContent = stats.total_pages_found;
    
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
    
    // Results stats - Enhanced with new fields
    document.getElementById('miningTotalPages').textContent = stats.total_pages_found;
    document.getElementById('miningPagesWithAds').textContent = stats.pages_with_ads;
    document.getElementById('miningVerifiedPages').textContent = stats.pages_verified;
    document.getElementById('miningEmailsCollected').textContent = stats.emails_collected;
    
    // New stats
    const phonesEl = document.getElementById('miningPhonesCollected');
    if (phonesEl) phonesEl.textContent = stats.phones_collected || 0;
    
    const websitesEl = document.getElementById('miningWebsitesCollected');
    if (websitesEl) websitesEl.textContent = stats.websites_collected || 0;
    
    const cacheEl = document.getElementById('miningCacheHits');
    if (cacheEl) cacheEl.textContent = stats.cache_hits || 0;
}

/**
 * Add page to results table - Enhanced with new columns
 */
function miningAddPageToTable(page) {
    const tbody = document.getElementById('miningTableBody');
    const row = document.createElement('tr');
    
    // Format location
    const location = page.location || page.country || '-';
    
    // Format phone with link
    const phoneHtml = page.phone 
        ? `<a href="tel:${page.phone}" style="color: #3498db;">${page.phone}</a>` 
        : '-';
    
    // Format website with link
    const websiteHtml = page.website 
        ? `<a href="${page.website}" target="_blank" style="color: #3498db;"><i class="fas fa-external-link-alt"></i></a>` 
        : '-';
    
    // Format email
    const emailHtml = page.email 
        ? `<span title="${page.email}">${page.email.substring(0, 20)}${page.email.length > 20 ? '...' : ''}</span>` 
        : '-';
    
    row.innerHTML = `
        <td>${page.page_id}</td>
        <td class="page-name" title="${page.page_name}">${page.page_name}</td>
        <td>${location}</td>
        <td>${page.category || '-'}</td>
        <td>${page.has_ads ? '<span class="badge-yes">Yes</span>' : '<span class="badge-no">No</span>'}</td>
        <td>${page.verified ? '<i class="fas fa-check-circle" style="color: #3498db;"></i>' : '-'}</td>
        <td>${emailHtml}</td>
        <td>${phoneHtml}</td>
        <td>${websiteHtml}</td>
        <td>${page.likes ? page.likes.toLocaleString() : 0}</td>
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
 * Run page mining - Enhanced with new filters
 */
async function miningRun() {
    // Parse UIDs
    const uids = miningParseUIDs();
    
    if (uids.length === 0) {
        showNotification('Vui lòng nhập danh sách UID hợp lệ', 'error');
        return;
    }
    
    // Get all filters (existing and new)
    const filters = {
        has_ads: document.getElementById('miningFilterAds')?.checked || false,
        verified: document.getElementById('miningFilterVerified')?.checked || false,
        country: document.getElementById('miningFilterCountry')?.value || '',
        category: document.getElementById('miningFilterCategory')?.value || '',
        min_likes: parseInt(document.getElementById('miningFilterMinLikes')?.value || 0),
        has_email: document.getElementById('miningFilterHasEmail')?.checked || false,
        has_phone: document.getElementById('miningFilterHasPhone')?.checked || false,
        has_website: document.getElementById('miningFilterHasWebsite')?.checked || false
    };
    
    // Clean up empty filters
    if (filters.country === 'all') filters.country = '';
    if (filters.category === 'all') filters.category = '';
    
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
        total_pages_found: 0,
        pages_with_ads: 0,
        pages_verified: 0,
        emails_collected: 0,
        phones_collected: 0,
        websites_collected: 0,
        processing_time: 0,
        cache_hits: 0,
        api_calls: 0
    };
    miningState.filters = filters;
    
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
    
    // Log active filters
    const activeFilters = [];
    if (filters.has_ads) activeFilters.push('Has Ads');
    if (filters.verified) activeFilters.push('Verified');
    if (filters.country) activeFilters.push(`Country: ${filters.country}`);
    if (filters.category) activeFilters.push(`Category: ${filters.category}`);
    if (filters.min_likes > 0) activeFilters.push(`Min Likes: ${filters.min_likes}`);
    if (filters.has_email) activeFilters.push('Has Email');
    if (filters.has_phone) activeFilters.push('Has Phone');
    if (filters.has_website) activeFilters.push('Has Website');
    
    if (activeFilters.length > 0) {
        miningAddLog(`Filters: ${activeFilters.join(', ')}`, 'info');
    } else {
        miningAddLog('Filters: None (all pages)', 'info');
    }
    
    miningAddLog(`Proxy: ${proxyType}, Threads: ${threads}`, 'info');
    
    // Prepare request with enhanced options
    const requestData = {
        uids: uids,
        options: {
            filters: filters,
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
            // Update results with enhanced stats
            miningState.pages = data.results?.pages || [];
            miningState.stats = {
                total_uids: data.stats.total_uids || uids.length,
                processed_uids: data.stats.total_uids || uids.length,
                total_pages_found: data.stats.total_pages_found || 0,
                pages_with_ads: data.stats.pages_with_ads || 0,
                pages_verified: data.stats.pages_verified || 0,
                emails_collected: data.stats.emails_collected || 0,
                phones_collected: data.stats.phones_collected || 0,
                websites_collected: data.stats.websites_collected || 0,
                processing_time: data.stats.processing_time || 0,
                cache_hits: data.stats.cache_hits || 0,
                api_calls: data.stats.api_calls || 0
            };
            
            miningUpdateStats();
            
            // Display pages in table
            miningState.pages.forEach(page => miningAddPageToTable(page));
            
            miningAddLog(`✅ Hoàn thành! Tìm thấy ${miningState.stats.total_pages_found} pages`, 'success');
            miningAddLog(`Pages có Ads: ${miningState.stats.pages_with_ads}, Verified: ${miningState.stats.pages_verified}`, 'info');
            miningAddLog(`Emails: ${miningState.stats.emails_collected}, Phones: ${miningState.stats.phones_collected}, Websites: ${miningState.stats.websites_collected}`, 'info');
            miningAddLog(`Cache hits: ${miningState.stats.cache_hits}, API calls: ${miningState.stats.api_calls}`, 'info');
            miningAddLog(`Thời gian: ${miningState.stats.processing_time.toFixed(2)}s`, 'info');
            
            showNotification(`✅ Khai thác hoàn tất! Tìm thấy ${miningState.stats.total_pages_found} pages`, 'success');
            
            // Log activity to activity feed
            if (typeof window.logActivity === 'function') {
                window.logActivity({
                    type: 'page_mining',
                    title: 'Khai thác Page hoàn tất',
                    description: `Tìm thấy ${miningState.stats.total_pages_found} pages - Emails: ${miningState.stats.emails_collected}`,
                    status: 'success',
                    icon: 'fa-bullseye',
                    color: 'purple',
                    metadata: {
                        total_pages: miningState.stats.total_pages_found,
                        pages_with_ads: miningState.stats.pages_with_ads,
                        pages_verified: miningState.stats.pages_verified,
                        emails_collected: miningState.stats.emails_collected,
                        phones_collected: miningState.stats.phones_collected,
                        websites_collected: miningState.stats.websites_collected,
                        processing_time: miningState.stats.processing_time
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
 * Export results to TXT - Enhanced
 */
async function miningExportTXT() {
    if (miningState.pages.length === 0) {
        showNotification('Chưa có kết quả để export', 'info');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/page-mining/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pages: miningState.pages,
                format: 'txt'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create download
            const blob = new Blob([data.data], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `page_mining_${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Đã export TXT', 'success');
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        showNotification(`Lỗi export: ${error.message}`, 'error');
    }
}

/**
 * Export results to CSV - Enhanced
 */
async function miningExportCSV() {
    if (miningState.pages.length === 0) {
        showNotification('Chưa có kết quả để export', 'info');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/page-mining/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pages: miningState.pages,
                format: 'csv'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create download
            const blob = new Blob([data.data], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `page_mining_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Đã export CSV', 'success');
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        showNotification(`Lỗi export: ${error.message}`, 'error');
    }
}

/**
 * Export results to JSON - New
 */
async function miningExportJSON() {
    if (miningState.pages.length === 0) {
        showNotification('Chưa có kết quả để export', 'info');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/page-mining/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pages: miningState.pages,
                format: 'json'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create download
            const blob = new Blob([data.data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `page_mining_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Đã export JSON', 'success');
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        showNotification(`Lỗi export: ${error.message}`, 'error');
    }
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

/**
 * Copy Phones to clipboard - New
 */
function miningCopyPhones() {
    const phones = miningState.pages
        .filter(p => p.phone)
        .map(p => p.phone)
        .join('\n');
    
    if (!phones) {
        showNotification('Không có số điện thoại nào', 'info');
        return;
    }
    
    navigator.clipboard.writeText(phones).then(() => {
        const count = miningState.pages.filter(p => p.phone).length;
        showNotification(`Đã copy ${count} số điện thoại`, 'success');
    }).catch(err => {
        showNotification('Lỗi copy: ' + err.message, 'error');
    });
}

/**
 * Copy Websites to clipboard - New
 */
function miningCopyWebsites() {
    const websites = miningState.pages
        .filter(p => p.website)
        .map(p => p.website)
        .join('\n');
    
    if (!websites) {
        showNotification('Không có website nào', 'info');
        return;
    }
    
    navigator.clipboard.writeText(websites).then(() => {
        const count = miningState.pages.filter(p => p.website).length;
        showNotification(`Đã copy ${count} websites`, 'success');
    }).catch(err => {
        showNotification('Lỗi copy: ' + err.message, 'error');
    });
}

console.log('Page Mining V2 Enhanced functions loaded');
