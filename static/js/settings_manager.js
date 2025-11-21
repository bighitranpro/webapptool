/**
 * Settings Manager
 * Handles all settings modal functionality
 */

class SettingsManager {
    constructor() {
        this.currentTab = 'profile';
        this.init();
    }

    init() {
        this.loadProfileData();
        this.loadPreferencesData();
        this.loadAPIKeyData();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Profile save button
        const profileSaveBtn = document.querySelector('#profileTab .btn-primary');
        if (profileSaveBtn) {
            profileSaveBtn.addEventListener('click', () => this.saveProfile());
        }

        // Preferences save button
        const prefsSaveBtn = document.querySelector('#preferencesTab .btn-primary');
        if (prefsSaveBtn) {
            prefsSaveBtn.addEventListener('click', () => this.savePreferences());
        }

        // Security - Change password button
        const passwordBtn = document.querySelector('#securityTab .btn-primary');
        if (passwordBtn) {
            passwordBtn.addEventListener('click', () => this.changePassword());
        }

        // API - Regenerate key button
        const regenBtn = document.querySelector('#apiTab .btn-secondary');
        if (regenBtn) {
            regenBtn.addEventListener('click', () => this.regenerateAPIKey());
        }

        // API - Copy key button
        const copyBtn = document.querySelector('#apiTab .copy-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyAPIKey());
        }

        // API - Toggle visibility button
        const toggleBtn = document.querySelector('#apiTab .toggle-visibility-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleAPIKeyVisibility());
        }
    }

    async loadProfileData() {
        try {
            const response = await fetch('/api/user/profile');
            const data = await response.json();
            
            if (data.success) {
                const user = data.user;
                
                // Update profile form
                const fullNameInput = document.querySelector('#profileTab input[type="text"]');
                const emailInput = document.querySelector('#profileTab input[type="email"]');
                
                if (fullNameInput && user.full_name) {
                    fullNameInput.value = user.full_name;
                }
                if (emailInput && user.email) {
                    emailInput.value = user.email;
                }
            }
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    }

    async saveProfile() {
        try {
            const fullNameInput = document.querySelector('#profileTab input[type="text"]');
            const emailInput = document.querySelector('#profileTab input[type="email"]');
            
            const data = {
                full_name: fullNameInput?.value || '',
                email: emailInput?.value || ''
            };
            
            const response = await fetch('/api/user/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('✅ Đã lưu thông tin hồ sơ!', 'success');
                // Update UI if needed
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showToast('❌ ' + result.message, 'error');
            }
        } catch (error) {
            this.showToast('❌ Lỗi kết nối', 'error');
            console.error('Save profile error:', error);
        }
    }

    async loadPreferencesData() {
        try {
            const response = await fetch('/api/user/preferences');
            const data = await response.json();
            
            if (data.success) {
                const prefs = data.preferences;
                
                // Update preferences form
                const langSelect = document.querySelector('#preferencesTab select[class="form-control"]');
                if (langSelect && prefs.language) {
                    langSelect.value = prefs.language;
                }
                
                // Update checkboxes
                const checkboxes = document.querySelectorAll('#preferencesTab input[type="checkbox"]');
                if (checkboxes.length >= 3) {
                    checkboxes[0].checked = prefs.notifications_enabled;
                    checkboxes[1].checked = prefs.auto_save_results;
                    checkboxes[2].checked = prefs.sound_effects;
                }
            }
        } catch (error) {
            console.error('Failed to load preferences:', error);
        }
    }

    async savePreferences() {
        try {
            const langSelect = document.querySelector('#preferencesTab select[class="form-control"]');
            const checkboxes = document.querySelectorAll('#preferencesTab input[type="checkbox"]');
            
            const data = {
                language: langSelect?.value || 'vi',
                theme: 'dark',
                notifications_enabled: checkboxes[0]?.checked || false,
                auto_save_results: checkboxes[1]?.checked || false,
                sound_effects: checkboxes[2]?.checked || false
            };
            
            const response = await fetch('/api/user/preferences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('✅ Đã lưu tùy chọn!', 'success');
                
                // Update language if changed
                if (data.language !== 'vi') {
                    setTimeout(() => location.reload(), 1000);
                }
            } else {
                this.showToast('❌ ' + result.message, 'error');
            }
        } catch (error) {
            this.showToast('❌ Lỗi kết nối', 'error');
            console.error('Save preferences error:', error);
        }
    }

    async changePassword() {
        try {
            const inputs = document.querySelectorAll('#securityTab input[type="password"]');
            
            if (inputs.length < 3) {
                this.showToast('❌ Không tìm thấy form đổi mật khẩu', 'error');
                return;
            }
            
            const currentPassword = inputs[0].value;
            const newPassword = inputs[1].value;
            const confirmPassword = inputs[2].value;
            
            // Validation
            if (!currentPassword || !newPassword || !confirmPassword) {
                this.showToast('⚠️ Vui lòng điền đầy đủ thông tin', 'warning');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                this.showToast('⚠️ Mật khẩu xác nhận không khớp', 'warning');
                return;
            }
            
            if (newPassword.length < 6) {
                this.showToast('⚠️ Mật khẩu mới phải có ít nhất 6 ký tự', 'warning');
                return;
            }
            
            const response = await fetch('/api/user/password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('✅ Đã đổi mật khẩu thành công!', 'success');
                // Clear form
                inputs.forEach(input => input.value = '');
            } else {
                this.showToast('❌ ' + result.message, 'error');
            }
        } catch (error) {
            this.showToast('❌ Lỗi kết nối', 'error');
            console.error('Change password error:', error);
        }
    }

    async loadAPIKeyData() {
        try {
            const response = await fetch('/api/user/apikey');
            const data = await response.json();
            
            if (data.success) {
                const keyInput = document.querySelector('#apiTab input[type="password"]');
                if (keyInput) {
                    keyInput.value = data.api_key;
                    keyInput.dataset.apiKey = data.api_key;
                }
            }
        } catch (error) {
            console.error('Failed to load API key:', error);
        }
    }

    async regenerateAPIKey() {
        if (!confirm('Bạn có chắc muốn tạo lại API key? Key cũ sẽ không còn hoạt động.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/user/apikey', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const keyInput = document.querySelector('#apiTab input[type="password"]');
                if (keyInput) {
                    keyInput.value = result.api_key;
                    keyInput.dataset.apiKey = result.api_key;
                }
                this.showToast('✅ Đã tạo API key mới!', 'success');
            } else {
                this.showToast('❌ ' + result.message, 'error');
            }
        } catch (error) {
            this.showToast('❌ Lỗi kết nối', 'error');
            console.error('Regenerate API key error:', error);
        }
    }

    copyAPIKey() {
        const keyInput = document.querySelector('#apiTab input[type="password"]');
        if (!keyInput) return;
        
        const apiKey = keyInput.dataset.apiKey || keyInput.value;
        
        // Copy to clipboard
        navigator.clipboard.writeText(apiKey).then(() => {
            this.showToast('✅ Đã sao chép API key!', 'success');
            
            // Visual feedback
            const copyBtn = document.querySelector('#apiTab .copy-btn');
            if (copyBtn) {
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                }, 2000);
            }
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showToast('❌ Không thể sao chép', 'error');
        });
    }

    toggleAPIKeyVisibility() {
        const keyInput = document.querySelector('#apiTab input[type="password"], #apiTab input[type="text"]');
        const toggleBtn = document.querySelector('#apiTab .toggle-visibility-btn i');
        
        if (!keyInput || !toggleBtn) return;
        
        if (keyInput.type === 'password') {
            keyInput.type = 'text';
            keyInput.value = keyInput.dataset.apiKey || keyInput.value;
            toggleBtn.classList.remove('fa-eye');
            toggleBtn.classList.add('fa-eye-slash');
        } else {
            keyInput.type = 'password';
            toggleBtn.classList.remove('fa-eye-slash');
            toggleBtn.classList.add('fa-eye');
        }
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        // Set icon based on type
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-times-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        
        const icon = icons[type] || icons['info'];
        
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : type === 'warning' ? '#f39c12' : '#3498db'};
            color: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            z-index: 100000;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 500;
            animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            min-width: 250px;
            backdrop-filter: blur(10px);
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

// Add animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
    
    .toast-notification i {
        font-size: 18px;
    }
`;
document.head.appendChild(style);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});
