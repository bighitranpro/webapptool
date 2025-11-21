/**
 * I18N - Internationalization System
 * Hệ thống đa ngôn ngữ
 */

class I18N {
    constructor() {
        this.currentLang = this.getStoredLanguage() || 'vi'; // Default: Vietnamese
        this.translations = {};
        this.fallbackLang = 'en';
        
        // Load translations
        this.loadTranslations();
        
        // Apply language on init
        this.applyLanguage();
    }
    
    /**
     * Get stored language from localStorage
     */
    getStoredLanguage() {
        return localStorage.getItem('app_language');
    }
    
    /**
     * Store language to localStorage
     */
    storeLanguage(lang) {
        localStorage.setItem('app_language', lang);
    }
    
    /**
     * Load translation files
     */
    loadTranslations() {
        // Translations are loaded from separate files (vi.js, en.js)
        // They should be included before this file
        if (typeof vi !== 'undefined') {
            this.translations.vi = vi;
        }
        if (typeof en !== 'undefined') {
            this.translations.en = en;
        }
    }
    
    /**
     * Change language
     */
    changeLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLang = lang;
            this.storeLanguage(lang);
            this.applyLanguage();
            
            // Trigger custom event
            window.dispatchEvent(new CustomEvent('languageChanged', { 
                detail: { language: lang } 
            }));
            
            return true;
        }
        return false;
    }
    
    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLang;
    }
    
    /**
     * Get translation by key path
     * Example: t('login.title') => 'Đăng Nhập'
     */
    t(keyPath, defaultValue = '') {
        const keys = keyPath.split('.');
        let value = this.translations[this.currentLang];
        
        // Navigate through nested object
        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                // Try fallback language
                value = this.translations[this.fallbackLang];
                for (const fallbackKey of keys) {
                    if (value && typeof value === 'object' && fallbackKey in value) {
                        value = value[fallbackKey];
                    } else {
                        return defaultValue || keyPath;
                    }
                }
                break;
            }
        }
        
        return value || defaultValue || keyPath;
    }
    
    /**
     * Apply language to all elements with data-i18n attribute
     */
    applyLanguage() {
        // Update HTML lang attribute
        document.documentElement.lang = this.currentLang;
        
        // Find all elements with data-i18n
        const elements = document.querySelectorAll('[data-i18n]');
        
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            
            // Update different types of elements
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                // Update placeholder for input/textarea
                if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                } else {
                    element.value = translation;
                }
            } else if (element.tagName === 'IMG') {
                // Update alt for images
                element.alt = translation;
            } else if (element.hasAttribute('title')) {
                // Update title attribute
                element.title = translation;
            } else {
                // Update text content
                element.textContent = translation;
            }
        });
        
        // Update elements with data-i18n-placeholder
        const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
        placeholders.forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });
        
        // Update elements with data-i18n-title
        const titles = document.querySelectorAll('[data-i18n-title]');
        titles.forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });
        
        // Update language selector
        this.updateLanguageSelector();
    }
    
    /**
     * Update language selector UI
     */
    updateLanguageSelector() {
        const selectors = document.querySelectorAll('.language-selector');
        
        selectors.forEach(selector => {
            const currentLangBtn = selector.querySelector('.current-language');
            if (currentLangBtn) {
                // Update flag and text
                const flagMap = {
                    'vi': '🇻🇳',
                    'en': '🇬🇧'
                };
                const nameMap = {
                    'vi': 'Tiếng Việt',
                    'en': 'English'
                };
                
                currentLangBtn.innerHTML = `
                    <span class="flag">${flagMap[this.currentLang]}</span>
                    <span class="lang-name">${nameMap[this.currentLang]}</span>
                    <i class="fas fa-chevron-down"></i>
                `;
            }
            
            // Update active state in dropdown
            const options = selector.querySelectorAll('.lang-option');
            options.forEach(option => {
                const lang = option.getAttribute('data-lang');
                if (lang === this.currentLang) {
                    option.classList.add('active');
                } else {
                    option.classList.remove('active');
                }
            });
        });
    }
    
    /**
     * Initialize language selector
     */
    initLanguageSelector() {
        const selectors = document.querySelectorAll('.language-selector');
        
        selectors.forEach(selector => {
            // Toggle dropdown
            const currentLangBtn = selector.querySelector('.current-language');
            const dropdown = selector.querySelector('.language-dropdown');
            
            if (currentLangBtn && dropdown) {
                currentLangBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    dropdown.classList.toggle('active');
                });
                
                // Close dropdown when clicking outside
                document.addEventListener('click', () => {
                    dropdown.classList.remove('active');
                });
            }
            
            // Handle language selection
            const options = selector.querySelectorAll('.lang-option');
            options.forEach(option => {
                option.addEventListener('click', (e) => {
                    e.preventDefault();
                    const lang = option.getAttribute('data-lang');
                    
                    if (lang && lang !== this.currentLang) {
                        this.changeLanguage(lang);
                        
                        // Show notification
                        this.showLanguageChangedNotification(lang);
                    }
                    
                    // Close dropdown
                    if (dropdown) {
                        dropdown.classList.remove('active');
                    }
                });
            });
        });
    }
    
    /**
     * Show notification when language changes
     */
    showLanguageChangedNotification(lang) {
        const messages = {
            'vi': 'Đã chuyển sang Tiếng Việt',
            'en': 'Changed to English'
        };
        
        const notification = document.createElement('div');
        notification.className = 'language-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${messages[lang] || 'Language changed'}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Remove after 2 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 2000);
    }
    
    /**
     * Format number based on current language
     */
    formatNumber(number) {
        const locale = this.currentLang === 'vi' ? 'vi-VN' : 'en-US';
        return new Intl.NumberFormat(locale).format(number);
    }
    
    /**
     * Format currency based on current language
     */
    formatCurrency(amount, currency = 'VND') {
        const locale = this.currentLang === 'vi' ? 'vi-VN' : 'en-US';
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
    
    /**
     * Format date based on current language
     */
    formatDate(date, options = {}) {
        const locale = this.currentLang === 'vi' ? 'vi-VN' : 'en-US';
        return new Intl.DateTimeFormat(locale, options).format(date);
    }
}

// Create global instance
const i18n = new I18N();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        i18n.initLanguageSelector();
    });
} else {
    i18n.initLanguageSelector();
}

// Make available globally
window.i18n = i18n;
window.t = (key, defaultValue) => i18n.t(key, defaultValue);
