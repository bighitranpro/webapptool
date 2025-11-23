/**
 * Tool Handlers - Functions for all tool modals
 * Handles Email Validator, Generator, Extractor, FB Linked, 2FA, Mining
 */

// ============================================
// EMAIL VALIDATOR TOOL
// ============================================

function runEmailValidator() {
    const emailsText = document.getElementById('validatorEmails').value.trim();
    const checkMX = document.getElementById('checkMX').checked;
    const checkSMTP = document.getElementById('checkSMTP').checked;
    const checkDisposable = document.getElementById('checkDisposable').checked;
    const checkFBCompat = document.getElementById('checkFBCompat').checked;
    
    if (!emailsText) {
        showNotification('Vui lòng nhập danh sách email', 'error');
        return;
    }
    
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Không tìm thấy email hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'validatorResults', `Đang kiểm tra ${emails.length} emails...`);
    
    fetch('/api/validate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            emails: emails,
            options: {
                check_mx: checkMX,
                check_smtp: checkSMTP,
                check_disposable: checkDisposable,
                check_fb_compat: checkFBCompat,
                max_workers: 10,
                timeout: 5,
                use_cache: true
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayValidatorResults(data);
        } else {
            displayResult('validatorResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Validator Error:', error);
        displayResult('validatorResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayValidatorResults(data) {
    const container = document.getElementById('validatorResults');
    const stats = data.stats || {};
    const results = data.results || {live: [], die: [], unknown: []};
    
    const liveCount = results.live.length;
    const dieCount = results.die.length;
    const unknownCount = results.unknown.length;
    const liveRate = stats.total > 0 ? ((liveCount / stats.total) * 100).toFixed(2) : 0;
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-chart-pie"></i> Tổng quan kết quả</h3>
            <div class="stats-row">
                <div class="stat-item stat-total">
                    <div class="stat-value">${stats.total || 0}</div>
                    <div class="stat-label">Tổng số</div>
                </div>
                <div class="stat-item stat-live">
                    <div class="stat-value">${liveCount}</div>
                    <div class="stat-label">LIVE</div>
                </div>
                <div class="stat-item stat-die">
                    <div class="stat-value">${dieCount}</div>
                    <div class="stat-label">DIE</div>
                </div>
                <div class="stat-item stat-unknown">
                    <div class="stat-value">${unknownCount}</div>
                    <div class="stat-label">UNKNOWN</div>
                </div>
                <div class="stat-item stat-rate">
                    <div class="stat-value">${liveRate}%</div>
                    <div class="stat-label">Tỷ lệ LIVE</div>
                </div>
            </div>
        </div>
        
        <div class="results-tabs">
            <button class="tab-btn active" onclick="showValidatorTab('live')">
                <i class="fas fa-check-circle"></i> LIVE (${liveCount})
            </button>
            <button class="tab-btn" onclick="showValidatorTab('die')">
                <i class="fas fa-times-circle"></i> DIE (${dieCount})
            </button>
            <button class="tab-btn" onclick="showValidatorTab('unknown')">
                <i class="fas fa-question-circle"></i> UNKNOWN (${unknownCount})
            </button>
        </div>
        
        <div class="tab-content">
            <div id="validatorTab-live" class="tab-pane active">
                <textarea readonly rows="10">${results.live.map(r => r.email).join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('validatorTab-live')">
                    <i class="fas fa-copy"></i> Copy LIVE
                </button>
                <button class="btn btn-sm btn-success" onclick="downloadTabContent('validatorTab-live', 'live_emails.txt')">
                    <i class="fas fa-download"></i> Tải xuống
                </button>
            </div>
            <div id="validatorTab-die" class="tab-pane">
                <textarea readonly rows="10">${results.die.map(r => r.email).join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('validatorTab-die')">
                    <i class="fas fa-copy"></i> Copy DIE
                </button>
                <button class="btn btn-sm btn-success" onclick="downloadTabContent('validatorTab-die', 'die_emails.txt')">
                    <i class="fas fa-download"></i> Tải xuống
                </button>
            </div>
            <div id="validatorTab-unknown" class="tab-pane">
                <textarea readonly rows="10">${results.unknown.map(r => r.email).join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('validatorTab-unknown')">
                    <i class="fas fa-copy"></i> Copy UNKNOWN
                </button>
                <button class="btn btn-sm btn-success" onclick="downloadTabContent('validatorTab-unknown', 'unknown_emails.txt')">
                    <i class="fas fa-download"></i> Tải xuống
                </button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function showValidatorTab(tabName) {
    // Remove active from all tabs
    document.querySelectorAll('#validatorResults .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('#validatorResults .tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Add active to selected tab
    event.target.classList.add('active');
    document.getElementById('validatorTab-' + tabName).classList.add('active');
}

function clearValidatorResults() {
    document.getElementById('validatorEmails').value = '';
    document.getElementById('validatorResults').innerHTML = '';
}

// ============================================
// EMAIL GENERATOR TOOL
// ============================================

function runEmailGenerator() {
    const count = parseInt(document.getElementById('genCount').value);
    const domain = document.getElementById('genDomain').value;
    const addNumbers = document.getElementById('genNumbers').checked;
    const addDots = document.getElementById('genDots').checked;
    const addUnderscores = document.getElementById('genUnderscores').checked;
    const unique = document.getElementById('genUnique').checked;
    
    if (count < 1 || count > 10000) {
        showNotification('Số lượng phải từ 1 đến 10,000', 'error');
        return;
    }
    
    let domains = [];
    if (domain === 'custom') {
        const customDomainsText = document.getElementById('customDomains').value.trim();
        if (!customDomainsText) {
            showNotification('Vui lòng nhập danh sách domain tùy chỉnh', 'error');
            return;
        }
        domains = customDomainsText.split('\n').map(d => d.trim()).filter(d => d);
    } else {
        domains = [domain];
    }
    
    toggleLoading(true, 'generatorResults', `Đang tạo ${count} emails...`);
    
    fetch('/api/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email_type: 'random',
            text: '',
            total: count,
            domains: domains,
            char_type: 'lowercase',
            number_type: addNumbers ? 'suffix' : 'none'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayGeneratorResults(data);
        } else {
            displayResult('generatorResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Generator Error:', error);
        displayResult('generatorResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayGeneratorResults(data) {
    const container = document.getElementById('generatorResults');
    const emails = data.emails || [];
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-check-circle"></i> Đã tạo thành công</h3>
            <p>Tổng số: <strong>${emails.length}</strong> emails</p>
        </div>
        <div class="result-list">
            <textarea readonly rows="15">${emails.join('\n')}</textarea>
        </div>
        <div class="result-actions">
            <button class="btn btn-primary" onclick="copyGeneratorResults()">
                <i class="fas fa-copy"></i> Copy tất cả
            </button>
            <button class="btn btn-success" onclick="downloadGeneratorResults()">
                <i class="fas fa-download"></i> Tải xuống
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

function copyGeneratorResults() {
    const textarea = document.querySelector('#generatorResults textarea');
    if (textarea) {
        textarea.select();
        document.execCommand('copy');
        showNotification('Đã copy tất cả emails', 'success');
    }
}

function downloadGeneratorResults() {
    const textarea = document.querySelector('#generatorResults textarea');
    if (textarea) {
        const blob = new Blob([textarea.value], {type: 'text/plain'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated_emails.txt';
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã tải xuống', 'success');
    }
}

function clearGeneratorResults() {
    document.getElementById('generatorResults').innerHTML = '';
}

// Show/hide custom domain field
document.addEventListener('DOMContentLoaded', function() {
    const domainSelect = document.getElementById('genDomain');
    if (domainSelect) {
        domainSelect.addEventListener('change', function() {
            const customGroup = document.getElementById('customDomainGroup');
            if (this.value === 'custom') {
                customGroup.style.display = 'block';
            } else {
                customGroup.style.display = 'none';
            }
        });
    }
});

// ============================================
// EMAIL EXTRACTOR TOOL
// ============================================

function runEmailExtractor() {
    const input = document.getElementById('extractorInput').value.trim();
    const unique = document.getElementById('extractUnique').checked;
    const sort = document.getElementById('extractSort').checked;
    
    if (!input) {
        showNotification('Vui lòng nhập văn bản', 'error');
        return;
    }
    
    toggleLoading(true, 'extractorResults', 'Đang trích xuất emails...');
    
    fetch('/api/extract', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: input,
            options: {
                unique: unique,
                sort_by_domain: sort
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayExtractorResults(data);
        } else {
            displayResult('extractorResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Extractor Error:', error);
        displayResult('extractorResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayExtractorResults(data) {
    const container = document.getElementById('extractorResults');
    const emails = data.emails || [];
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-check-circle"></i> Trích xuất thành công</h3>
            <p>Tìm thấy: <strong>${emails.length}</strong> emails</p>
        </div>
        <div class="result-list">
            <textarea readonly rows="15">${emails.join('\n')}</textarea>
        </div>
        <div class="result-actions">
            <button class="btn btn-primary" onclick="copyExtractorResults()">
                <i class="fas fa-copy"></i> Copy tất cả
            </button>
            <button class="btn btn-success" onclick="downloadExtractorResults()">
                <i class="fas fa-download"></i> Tải xuống
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

function copyExtractorResults() {
    const textarea = document.querySelector('#extractorResults textarea');
    if (textarea) {
        textarea.select();
        document.execCommand('copy');
        showNotification('Đã copy tất cả emails', 'success');
    }
}

function downloadExtractorResults() {
    const textarea = document.querySelector('#extractorResults textarea');
    if (textarea) {
        const blob = new Blob([textarea.value], {type: 'text/plain'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'extracted_emails.txt';
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã tải xuống', 'success');
    }
}

function clearExtractorResults() {
    document.getElementById('extractorInput').value = '';
    document.getElementById('extractorResults').innerHTML = '';
}

// ============================================
// FACEBOOK LINKED CHECKER TOOL
// ============================================

function runFBLinkedChecker() {
    const emailsText = document.getElementById('fbLinkedEmails').value.trim();
    
    if (!emailsText) {
        showNotification('Vui lòng nhập danh sách email', 'error');
        return;
    }
    
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Không tìm thấy email hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'fbLinkedResults', `Đang kiểm tra ${emails.length} emails...`);
    
    fetch('/api/fb-check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            emails: emails
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayFBLinkedResults(data);
        } else {
            displayResult('fbLinkedResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('FB Linked Error:', error);
        displayResult('fbLinkedResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayFBLinkedResults(data) {
    const container = document.getElementById('fbLinkedResults');
    const results = data.results || [];
    
    const linkedEmails = results.filter(r => r.is_linked).map(r => r.email);
    const notLinkedEmails = results.filter(r => !r.is_linked).map(r => r.email);
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-chart-pie"></i> Kết quả kiểm tra Facebook</h3>
            <div class="stats-row">
                <div class="stat-item stat-total">
                    <div class="stat-value">${results.length}</div>
                    <div class="stat-label">Tổng số</div>
                </div>
                <div class="stat-item stat-live">
                    <div class="stat-value">${linkedEmails.length}</div>
                    <div class="stat-label">Có liên kết</div>
                </div>
                <div class="stat-item stat-die">
                    <div class="stat-value">${notLinkedEmails.length}</div>
                    <div class="stat-label">Không liên kết</div>
                </div>
            </div>
        </div>
        
        <div class="results-tabs">
            <button class="tab-btn active" onclick="showFBTab('linked')">
                <i class="fas fa-check-circle"></i> Có liên kết (${linkedEmails.length})
            </button>
            <button class="tab-btn" onclick="showFBTab('not-linked')">
                <i class="fas fa-times-circle"></i> Không liên kết (${notLinkedEmails.length})
            </button>
        </div>
        
        <div class="tab-content">
            <div id="fbTab-linked" class="tab-pane active">
                <textarea readonly rows="10">${linkedEmails.join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('fbTab-linked')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
            <div id="fbTab-not-linked" class="tab-pane">
                <textarea readonly rows="10">${notLinkedEmails.join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('fbTab-not-linked')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function showFBTab(tabName) {
    document.querySelectorAll('#fbLinkedResults .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('#fbLinkedResults .tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    event.target.classList.add('active');
    document.getElementById('fbTab-' + tabName).classList.add('active');
}

function clearFBLinkedResults() {
    document.getElementById('fbLinkedEmails').value = '';
    document.getElementById('fbLinkedResults').innerHTML = '';
}

// ============================================
// CHECK 2FA TOOL
// ============================================

function runCheck2FA() {
    const inputText = document.getElementById('check2faInput').value.trim();
    
    if (!inputText) {
        showNotification('Vui lòng nhập danh sách email|password', 'error');
        return;
    }
    
    const accounts = inputText.split('\n').map(line => line.trim()).filter(line => line);
    
    if (accounts.length === 0) {
        showNotification('Không tìm thấy tài khoản hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'check2faResults', `Đang kiểm tra ${accounts.length} tài khoản...`);
    
    fetch('/api/check-2fa', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            accounts: accounts
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayCheck2FAResults(data);
        } else {
            displayResult('check2faResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('2FA Check Error:', error);
        displayResult('check2faResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayCheck2FAResults(data) {
    const container = document.getElementById('check2faResults');
    const results = data.results || [];
    
    const has2FA = results.filter(r => r.has_2fa);
    const no2FA = results.filter(r => !r.has_2fa);
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-chart-pie"></i> Kết quả kiểm tra 2FA</h3>
            <div class="stats-row">
                <div class="stat-item stat-total">
                    <div class="stat-value">${results.length}</div>
                    <div class="stat-label">Tổng số</div>
                </div>
                <div class="stat-item stat-die">
                    <div class="stat-value">${has2FA.length}</div>
                    <div class="stat-label">Có 2FA</div>
                </div>
                <div class="stat-item stat-live">
                    <div class="stat-value">${no2FA.length}</div>
                    <div class="stat-label">Không 2FA</div>
                </div>
            </div>
        </div>
        
        <div class="results-tabs">
            <button class="tab-btn active" onclick="showTFATab('no2fa')">
                <i class="fas fa-check-circle"></i> Không 2FA (${no2FA.length})
            </button>
            <button class="tab-btn" onclick="showTFATab('has2fa')">
                <i class="fas fa-times-circle"></i> Có 2FA (${has2FA.length})
            </button>
        </div>
        
        <div class="tab-content">
            <div id="tfaTab-no2fa" class="tab-pane active">
                <textarea readonly rows="10">${no2FA.map(r => r.account).join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('tfaTab-no2fa')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
            <div id="tfaTab-has2fa" class="tab-pane">
                <textarea readonly rows="10">${has2FA.map(r => r.account).join('\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('tfaTab-has2fa')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function showTFATab(tabName) {
    document.querySelectorAll('#check2faResults .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('#check2faResults .tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    event.target.classList.add('active');
    document.getElementById('tfaTab-' + tabName).classList.add('active');
}

function clearCheck2FAResults() {
    document.getElementById('check2faInput').value = '';
    document.getElementById('check2faResults').innerHTML = '';
}

// ============================================
// PAGE MINING TOOL
// ============================================

function runPageMining() {
    const urlsText = document.getElementById('miningUrls').value.trim();
    
    if (!urlsText) {
        showNotification('Vui lòng nhập danh sách URL hoặc UID', 'error');
        return;
    }
    
    const uids = urlsText.split('\n').map(line => line.trim()).filter(line => line);
    
    if (uids.length === 0) {
        showNotification('Không tìm thấy UID hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'miningResults', `Đang khai thác ${uids.length} pages...`);
    
    fetch('/api/page-mining', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            uids: uids,
            options: {
                max_workers: 10
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayMiningResults(data);
        } else {
            displayResult('miningResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Mining Error:', error);
        displayResult('miningResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayMiningResults(data) {
    const container = document.getElementById('miningResults');
    const results = data.results || [];
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-check-circle"></i> Kết quả Mining</h3>
            <p>Tổng số: <strong>${results.length}</strong> pages</p>
        </div>
        <div class="results-table">
            <table>
                <thead>
                    <tr>
                        <th>Page ID</th>
                        <th>Tên</th>
                        <th>Followers</th>
                        <th>Category</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
                    ${results.map(r => `
                        <tr>
                            <td>${r.page_id || 'N/A'}</td>
                            <td>${r.name || 'N/A'}</td>
                            <td>${r.followers || 'N/A'}</td>
                            <td>${r.category || 'N/A'}</td>
                            <td><a href="${r.url}" target="_blank">Xem</a></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        <div class="result-actions">
            <button class="btn btn-success" onclick="downloadMiningResults()">
                <i class="fas fa-download"></i> Tải xuống JSON
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

function downloadMiningResults() {
    const table = document.querySelector('#miningResults table');
    if (table) {
        const results = [];
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            results.push({
                page_id: cells[0].textContent,
                name: cells[1].textContent,
                followers: cells[2].textContent,
                category: cells[3].textContent,
                url: cells[4].querySelector('a').href
            });
        });
        
        const blob = new Blob([JSON.stringify(results, null, 2)], {type: 'application/json'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mining_results.json';
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã tải xuống', 'success');
    }
}

function clearMiningResults() {
    document.getElementById('miningUrls').value = '';
    document.getElementById('miningResults').innerHTML = '';
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function copyTabContent(tabId) {
    const tab = document.getElementById(tabId);
    const textarea = tab.querySelector('textarea');
    if (textarea) {
        textarea.select();
        document.execCommand('copy');
        showNotification('Đã copy kết quả', 'success');
    }
}

function downloadTabContent(tabId, filename) {
    const tab = document.getElementById(tabId);
    const textarea = tab.querySelector('textarea');
    if (textarea) {
        const blob = new Blob([textarea.value], {type: 'text/plain'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã tải xuống', 'success');
    }
}

function showNotification(message, type = 'info') {
    // Check if notification function exists from dashboard_pro.js
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else {
        // Fallback to alert
        alert(message);
    }
}

// ============================================
// EMAIL FILTER TOOL
// ============================================

function runEmailFilter() {
    const emailsText = document.getElementById('filterEmails').value.trim();
    const domains = document.getElementById('filterDomain').value.trim();
    const pattern = document.getElementById('filterPattern').value.trim();
    const include = document.getElementById('filterInclude').checked;
    const exclude = document.getElementById('filterExclude').checked;
    const caseSensitive = document.getElementById('filterCaseSensitive').checked;
    
    if (!emailsText) {
        showNotification('Vui lòng nhập danh sách email', 'error');
        return;
    }
    
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Không tìm thấy email hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'filterResults', `Đang lọc ${emails.length} emails...`);
    
    fetch('/api/filter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            emails: emails,
            filter_by: {
                domains: domains ? domains.split(',').map(d => d.trim()) : [],
                pattern: pattern || null,
                include: include,
                exclude: exclude,
                case_sensitive: caseSensitive
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayFilterResults(data);
        } else {
            displayResult('filterResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Filter Error:', error);
        displayResult('filterResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayFilterResults(data) {
    const container = document.getElementById('filterResults');
    const filtered = data.filtered || [];
    const removed = data.removed || [];
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-check-circle"></i> Kết quả lọc</h3>
            <div class="stats-row">
                <div class="stat-item stat-total">
                    <div class="stat-value">${data.total_input || 0}</div>
                    <div class="stat-label">Tổng input</div>
                </div>
                <div class="stat-item stat-live">
                    <div class="stat-value">${filtered.length}</div>
                    <div class="stat-label">Đã lọc</div>
                </div>
                <div class="stat-item stat-die">
                    <div class="stat-value">${removed.length}</div>
                    <div class="stat-label">Đã loại bỏ</div>
                </div>
            </div>
        </div>
        
        <div class="results-tabs">
            <button class="tab-btn active" onclick="showFilterTab('filtered')">
                <i class="fas fa-check-circle"></i> Đã lọc (${filtered.length})
            </button>
            <button class="tab-btn" onclick="showFilterTab('removed')">
                <i class="fas fa-times-circle"></i> Đã loại bỏ (${removed.length})
            </button>
        </div>
        
        <div class="tab-content">
            <div id="filterTab-filtered" class="tab-pane active">
                <textarea readonly rows="10">${filtered.join('\\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('filterTab-filtered')">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="btn btn-sm btn-success" onclick="downloadTabContent('filterTab-filtered', 'filtered_emails.txt')">
                    <i class="fas fa-download"></i> Tải xuống
                </button>
            </div>
            <div id="filterTab-removed" class="tab-pane">
                <textarea readonly rows="10">${removed.join('\\n')}</textarea>
                <button class="btn btn-sm btn-primary" onclick="copyTabContent('filterTab-removed')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function showFilterTab(tabName) {
    document.querySelectorAll('#filterResults .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('#filterResults .tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    event.target.classList.add('active');
    document.getElementById('filterTab-' + tabName).classList.add('active');
}

function clearFilterResults() {
    document.getElementById('filterEmails').value = '';
    document.getElementById('filterDomain').value = '';
    document.getElementById('filterPattern').value = '';
    document.getElementById('filterResults').innerHTML = '';
}

// ============================================
// EMAIL ANALYZER TOOL
// ============================================

function runEmailAnalyzer() {
    const emailsText = document.getElementById('analyzerEmails').value.trim();
    const analyzeDomains = document.getElementById('analyzeDomains').checked;
    const analyzePatterns = document.getElementById('analyzePatterns').checked;
    const analyzeQuality = document.getElementById('analyzeQuality').checked;
    
    if (!emailsText) {
        showNotification('Vui lòng nhập danh sách email', 'error');
        return;
    }
    
    const emails = parseEmails(emailsText);
    
    if (emails.length === 0) {
        showNotification('Không tìm thấy email hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'analyzerResults', `Đang phân tích ${emails.length} emails...`);
    
    fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            emails: emails,
            analyze: {
                domains: analyzeDomains,
                patterns: analyzePatterns,
                quality: analyzeQuality
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayAnalyzerResults(data);
        } else {
            displayResult('analyzerResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Analyzer Error:', error);
        displayResult('analyzerResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayAnalyzerResults(data) {
    const container = document.getElementById('analyzerResults');
    const analysis = data.analysis || {};
    const domains = analysis.domains || {};
    
    // Domain distribution
    let domainRows = '';
    Object.entries(domains).slice(0, 10).forEach(([domain, count]) => {
        const percentage = ((count / data.total) * 100).toFixed(1);
        domainRows += `
            <tr>
                <td>${domain}</td>
                <td>${count}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${percentage}%"></div>
                    </div>
                </td>
                <td>${percentage}%</td>
            </tr>
        `;
    });
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-chart-pie"></i> Phân tích Email</h3>
            <div class="stats-row">
                <div class="stat-item stat-total">
                    <div class="stat-value">${data.total || 0}</div>
                    <div class="stat-label">Tổng số</div>
                </div>
                <div class="stat-item stat-info">
                    <div class="stat-value">${Object.keys(domains).length}</div>
                    <div class="stat-label">Domains</div>
                </div>
                <div class="stat-item stat-success">
                    <div class="stat-value">${analysis.quality_score || 0}%</div>
                    <div class="stat-label">Quality Score</div>
                </div>
            </div>
        </div>
        
        <div class="results-table">
            <h4>Top Domains</h4>
            <table>
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>Count</th>
                        <th>Distribution</th>
                        <th>%</th>
                    </tr>
                </thead>
                <tbody>
                    ${domainRows}
                </tbody>
            </table>
        </div>
        
        <div class="result-actions">
            <button class="btn btn-success" onclick="downloadAnalyzerResults()">
                <i class="fas fa-download"></i> Tải báo cáo JSON
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

function downloadAnalyzerResults() {
    const table = document.querySelector('#analyzerResults table');
    if (table) {
        const data = {
            timestamp: new Date().toISOString(),
            analysis: 'Email Analysis Report'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'email_analysis.json';
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã tải xuống', 'success');
    }
}

function clearAnalyzerResults() {
    document.getElementById('analyzerEmails').value = '';
    document.getElementById('analyzerResults').innerHTML = '';
}

// ============================================
// EMAIL DEDUPLICATOR TOOL
// ============================================

function runDeduplicator() {
    const emailsText = document.getElementById('dedupEmails').value.trim();
    const caseInsensitive = document.getElementById('dedupCaseInsensitive').checked;
    const keepFirst = document.getElementById('dedupKeepFirst').checked;
    const sortOutput = document.getElementById('dedupSortOutput').checked;
    
    if (!emailsText) {
        showNotification('Vui lòng nhập danh sách email', 'error');
        return;
    }
    
    const emails = emailsText.split('\\n').map(e => e.trim()).filter(e => e);
    
    if (emails.length === 0) {
        showNotification('Không tìm thấy email hợp lệ', 'error');
        return;
    }
    
    toggleLoading(true, 'dedupResults', `Đang xử lý ${emails.length} emails...`);
    
    fetch('/api/deduplicate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            emails: emails,
            options: {
                case_insensitive: caseInsensitive,
                keep_first: keepFirst,
                sort_output: sortOutput
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayDedupResults(data);
        } else {
            displayResult('dedupResults', {message: data.message || 'Có lỗi xảy ra'}, 'error');
        }
    })
    .catch(error => {
        console.error('Dedup Error:', error);
        displayResult('dedupResults', {message: 'Lỗi kết nối: ' + error.message}, 'error');
    });
}

function displayDedupResults(data) {
    const container = document.getElementById('dedupResults');
    const unique = data.unique || [];
    const duplicates = data.duplicates || [];
    const removed = data.stats?.duplicates_removed || 0;
    
    let html = `
        <div class="results-summary">
            <h3><i class="fas fa-check-circle"></i> Kết quả loại bỏ trùng</h3>
            <div class="stats-row">
                <div class="stat-item stat-total">
                    <div class="stat-value">${data.stats?.total_input || 0}</div>
                    <div class="stat-label">Tổng input</div>
                </div>
                <div class="stat-item stat-live">
                    <div class="stat-value">${unique.length}</div>
                    <div class="stat-label">Unique</div>
                </div>
                <div class="stat-item stat-die">
                    <div class="stat-value">${removed}</div>
                    <div class="stat-label">Đã loại bỏ</div>
                </div>
            </div>
        </div>
        
        <div class="result-list">
            <h4>Email Unique (${unique.length})</h4>
            <textarea readonly rows="15">${unique.join('\\n')}</textarea>
        </div>
        
        <div class="result-actions">
            <button class="btn btn-primary" onclick="copyDedupResults()">
                <i class="fas fa-copy"></i> Copy tất cả
            </button>
            <button class="btn btn-success" onclick="downloadDedupResults()">
                <i class="fas fa-download"></i> Tải xuống
            </button>
        </div>
    `;
    
    container.innerHTML = html;
}

function copyDedupResults() {
    const textarea = document.querySelector('#dedupResults textarea');
    if (textarea) {
        textarea.select();
        document.execCommand('copy');
        showNotification('Đã copy tất cả emails unique', 'success');
    }
}

function downloadDedupResults() {
    const textarea = document.querySelector('#dedupResults textarea');
    if (textarea) {
        const blob = new Blob([textarea.value], {type: 'text/plain'});
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'unique_emails.txt';
        a.click();
        window.URL.revokeObjectURL(url);
        showNotification('Đã tải xuống', 'success');
    }
}

function clearDedupResults() {
    document.getElementById('dedupEmails').value = '';
    document.getElementById('dedupResults').innerHTML = '';
}

console.log('✅ Tool Handlers loaded successfully (including Filter, Analyzer, Deduplicator)');
