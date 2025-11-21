/**
 * Check Email Pass 2FA FB Functions
 */

// Global state
const check2faState = {
    isRunning: false,
    accounts: [],
    results: {
        hit_2fa: [],
        has_page: [],
        not_hit: [],
        error: []
    },
    stats: {
        total: 0,
        hit_2fa: 0,
        has_page: 0,
        not_hit: 0,
        error: 0,
        checked: 0
    }
};

/**
 * Load from file
 */
function check2faLoadFile() {
    document.getElementById('check2faFileInput').click();
}

/**
 * Handle file upload
 */
function check2faHandleFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('check2faInput').value = e.target.result;
        const lines = e.target.result.split('\n').filter(l => l.trim());
        showNotification(`Loaded ${lines.length} accounts from file`, 'success');
    };
    reader.readAsText(file);
}

/**
 * Clear input
 */
function check2faClearInput() {
    if (confirm('Clear all input?')) {
        document.getElementById('check2faInput').value = '';
        showNotification('Input cleared', 'info');
    }
}

/**
 * Parse accounts
 */
function check2faParseAccounts() {
    const input = document.getElementById('check2faInput').value;
    const lines = input.split('\n');
    const accounts = [];
    
    for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed && trimmed.includes(':')) {
            accounts.push(trimmed);
        }
    }
    
    return accounts;
}

/**
 * Update statistics display
 */
function check2faUpdateStats() {
    const stats = check2faState.stats;
    
    document.getElementById('check2faTotalMail').textContent = stats.total;
    document.getElementById('check2faHit2FA').textContent = stats.hit_2fa;
    document.getElementById('check2faHasPage').textContent = stats.has_page;
    document.getElementById('check2faNotHit').textContent = stats.not_hit;
    document.getElementById('check2faError').textContent = stats.error;
    document.getElementById('check2faChecked').textContent = stats.checked;
}

/**
 * Add result to display
 */
function check2faAddResult(result) {
    const display = document.getElementById('check2faResultsDisplay');
    
    // Remove placeholder if exists
    const placeholder = display.querySelector('.result-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    const entry = document.createElement('div');
    entry.className = `result-entry ${result.status.toLowerCase().replace('_', '-')}`;
    
    let text = `${result.email}:${result.password} -> `;
    
    if (result.status === 'HIT_2FA') {
        text += '✅ Has 2FA';
        if (result.has_page) {
            text += ` (${result.page_count} pages)`;
        }
    } else if (result.status === 'HAS_PAGE') {
        text += `📄 Has ${result.page_count} page(s)`;
    } else if (result.status === 'NOT_HIT') {
        text += '❌ Not hit';
        if (result.reason) {
            text += ` (${result.reason})`;
        }
    } else if (result.status === 'ERROR') {
        text += `⚠️ Error: ${result.error || 'Unknown'}`;
    }
    
    entry.textContent = text;
    display.appendChild(entry);
    display.scrollTop = display.scrollHeight;
}

/**
 * Run checking
 */
async function check2faRun() {
    // Parse accounts
    const accounts = check2faParseAccounts();
    
    if (accounts.length === 0) {
        showNotification('Please enter email:password accounts', 'error');
        return;
    }
    
    // Get settings
    const apiType = document.getElementById('check2faApiType').value;
    const proxyType = document.getElementById('check2faProxyType').value;
    const proxyList = document.getElementById('check2faProxyList').value;
    const validatePattern = document.getElementById('check2faValidatePattern').checked;
    const passwordPattern = document.getElementById('check2faPasswordPattern').value;
    const startFrom = parseInt(document.getElementById('check2faStartFrom').value) - 1;
    const threads = parseInt(document.getElementById('check2faThreads').value);
    
    // Update UI
    check2faState.isRunning = true;
    document.getElementById('check2faRunBtn').disabled = true;
    document.getElementById('check2faStopBtn').disabled = false;
    document.getElementById('check2faStatus').textContent = 'ĐANG CHECK..';
    document.getElementById('check2faStatus').classList.add('running');
    
    // Clear previous results
    const display = document.getElementById('check2faResultsDisplay');
    display.innerHTML = '';
    
    // Reset stats
    check2faState.stats = {
        total: accounts.length,
        hit_2fa: 0,
        has_page: 0,
        not_hit: 0,
        error: 0,
        checked: 0
    };
    
    // Count proxies
    const proxies = proxyList.split('\n').filter(l => l.trim());
    document.getElementById('check2faTotalProxy').textContent = proxies.length;
    
    check2faUpdateStats();
    
    // Prepare request
    const requestData = {
        accounts: accounts,
        options: {
            api_type: apiType,
            password_pattern: passwordPattern,
            validate_pattern: validatePattern,
            max_workers: threads,
            start_from: startFrom
        }
    };
    
    try {
        showNotification('Starting 2FA check...', 'info');
        
        const response = await fetch(`${API_BASE}/check-2fa`, {
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
            check2faState.results = data.results;
            check2faState.stats = data.stats;
            
            check2faUpdateStats();
            
            // Display results
            const allResults = [
                ...data.results.hit_2fa,
                ...data.results.has_page,
                ...data.results.not_hit,
                ...data.results.error
            ];
            
            allResults.forEach(result => check2faAddResult(result));
            
            showNotification(`✅ Check complete! Found ${data.stats.hit_2fa} with 2FA`, 'success');
        } else {
            throw new Error(data.message || 'Unknown error');
        }
        
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
        console.error('Check 2FA error:', error);
    } finally {
        check2faStop();
    }
}

/**
 * Stop checking
 */
function check2faStop() {
    check2faState.isRunning = false;
    document.getElementById('check2faRunBtn').disabled = false;
    document.getElementById('check2faStopBtn').disabled = true;
    document.getElementById('check2faStatus').textContent = 'READY';
    document.getElementById('check2faStatus').classList.remove('running');
}

/**
 * Export results
 */
function check2faExport() {
    if (check2faState.stats.checked === 0) {
        showNotification('No results to export', 'info');
        return;
    }
    
    let content = `Check Email Pass 2FA FB Results\n`;
    content += `Generated: ${new Date().toLocaleString()}\n`;
    content += `Total: ${check2faState.stats.total}\n`;
    content += `Hit 2FA: ${check2faState.stats.hit_2fa}\n`;
    content += `Has Page: ${check2faState.stats.has_page}\n`;
    content += `Not Hit: ${check2faState.stats.not_hit}\n`;
    content += `Error: ${check2faState.stats.error}\n\n`;
    
    // Hit 2FA
    content += `=== HIT 2FA (${check2faState.stats.hit_2fa}) ===\n`;
    check2faState.results.hit_2fa.forEach(r => {
        content += `${r.email}:${r.password}`;
        if (r.has_page) content += ` | Pages: ${r.page_count}`;
        content += '\n';
    });
    
    // Has Page
    content += `\n=== HAS PAGE (${check2faState.stats.has_page}) ===\n`;
    check2faState.results.has_page.forEach(r => {
        content += `${r.email}:${r.password} | Pages: ${r.page_count}\n`;
    });
    
    // Not Hit
    content += `\n=== NOT HIT (${check2faState.stats.not_hit}) ===\n`;
    check2faState.results.not_hit.forEach(r => {
        content += `${r.email}:${r.password}\n`;
    });
    
    // Error
    content += `\n=== ERROR (${check2faState.stats.error}) ===\n`;
    check2faState.results.error.forEach(r => {
        content += `${r.email}:${r.password} | Error: ${r.error || 'Unknown'}\n`;
    });
    
    // Create download
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `check_2fa_results_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Results exported', 'success');
}

console.log('Check 2FA functions loaded');
