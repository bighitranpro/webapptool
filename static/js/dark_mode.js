/**
 * Dark Mode Manager
 * Bi Tool v2.1 - Theme switching with persistence
 */

class ThemeManager {
    constructor() {
        this.STORAGE_KEY = 'bi-tool-theme';
        this.THEMES = {
            LIGHT: 'light',
            DARK: 'dark',
            AUTO: 'auto'
        };
        
        this.currentTheme = this.THEMES.AUTO;
        this.systemPrefersDark = false;
        
        this.init();
    }
    
    init() {
        // Check system preference
        this.checkSystemPreference();
        
        // Load saved theme
        this.loadTheme();
        
        // Apply theme
        this.applyTheme();
        
        // Setup listeners
        this.setupListeners();
        
        // Create toggle button if needed
        this.createToggleButton();
        
        console.log('✅ Theme Manager initialized');
    }
    
    checkSystemPreference() {
        if (window.matchMedia) {
            this.systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
    }
    
    loadTheme() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            if (saved && Object.values(this.THEMES).includes(saved)) {
                this.currentTheme = saved;
            }
        } catch (e) {
            console.warn('Could not load theme preference:', e);
        }
    }
    
    saveTheme(theme) {
        try {
            localStorage.setItem(this.STORAGE_KEY, theme);
            this.currentTheme = theme;
        } catch (e) {
            console.warn('Could not save theme preference:', e);
        }
    }
    
    getEffectiveTheme() {
        if (this.currentTheme === this.THEMES.AUTO) {
            return this.systemPrefersDark ? this.THEMES.DARK : this.THEMES.LIGHT;
        }
        return this.currentTheme;
    }
    
    applyTheme(theme) {
        if (theme) {
            this.saveTheme(theme);
        }
        
        const effectiveTheme = this.getEffectiveTheme();
        
        // Apply to document
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update body class for compatibility
        if (effectiveTheme === this.THEMES.DARK) {
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        } else {
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        }
        
        // Update toggle button
        this.updateToggleButton();
        
        // Dispatch event
        this.dispatchThemeChangeEvent(effectiveTheme);
        
        // Update Chart.js if available
        this.updateCharts();
    }
    
    toggleTheme() {
        const effectiveTheme = this.getEffectiveTheme();
        const newTheme = effectiveTheme === this.THEMES.DARK 
            ? this.THEMES.LIGHT 
            : this.THEMES.DARK;
        
        this.applyTheme(newTheme);
        
        // Show toast notification
        if (typeof toast !== 'undefined') {
            const message = newTheme === this.THEMES.DARK 
                ? 'Đã chuyển sang chế độ tối' 
                : 'Đã chuyển sang chế độ sáng';
            
            toast.info('Đổi giao diện', message, { duration: 2000 });
        }
    }
    
    setTheme(theme) {
        if (!Object.values(this.THEMES).includes(theme)) {
            console.warn('Invalid theme:', theme);
            return;
        }
        
        this.applyTheme(theme);
    }
    
    setupListeners() {
        // Listen for system preference changes
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            // Modern browsers
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', (e) => {
                    this.systemPrefersDark = e.matches;
                    if (this.currentTheme === this.THEMES.AUTO) {
                        this.applyTheme();
                    }
                });
            }
            // Older browsers
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener((e) => {
                    this.systemPrefersDark = e.matches;
                    if (this.currentTheme === this.THEMES.AUTO) {
                        this.applyTheme();
                    }
                });
            }
        }
        
        // Listen for storage changes (sync across tabs)
        window.addEventListener('storage', (e) => {
            if (e.key === this.STORAGE_KEY) {
                this.currentTheme = e.newValue || this.THEMES.AUTO;
                this.applyTheme();
            }
        });
    }
    
    createToggleButton() {
        // Check if toggle already exists
        if (document.querySelector('.theme-toggle')) {
            return;
        }
        
        // Find suitable container (sidebar header, navbar, etc.)
        const containers = [
            document.querySelector('.sidebar-header'),
            document.querySelector('.navbar'),
            document.querySelector('header')
        ];
        
        const container = containers.find(c => c !== null);
        
        if (!container) {
            console.warn('Could not find container for theme toggle button');
            return;
        }
        
        // Create toggle button
        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('aria-label', 'Toggle Dark Mode');
        button.setAttribute('title', 'Chuyển đổi chế độ tối/sáng');
        button.innerHTML = `
            <i class="fas fa-sun theme-icon-light"></i>
            <i class="fas fa-moon theme-icon-dark"></i>
        `;
        
        button.addEventListener('click', () => this.toggleTheme());
        
        // Add to container
        container.appendChild(button);
    }
    
    updateToggleButton() {
        const button = document.querySelector('.theme-toggle');
        if (!button) return;
        
        const effectiveTheme = this.getEffectiveTheme();
        
        if (effectiveTheme === this.THEMES.DARK) {
            button.setAttribute('title', 'Chuyển sang chế độ sáng');
        } else {
            button.setAttribute('title', 'Chuyển sang chế độ tối');
        }
    }
    
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: {
                theme: theme,
                isDark: theme === this.THEMES.DARK
            }
        });
        
        window.dispatchEvent(event);
    }
    
    updateCharts() {
        // Update Chart.js colors if available
        if (typeof Chart !== 'undefined') {
            const isDark = this.getEffectiveTheme() === this.THEMES.DARK;
            
            // Set default colors
            Chart.defaults.color = isDark ? '#9ca3af' : '#666666';
            Chart.defaults.borderColor = isDark ? '#374151' : '#dee2e6';
            
            // Update existing charts
            if (Chart.instances) {
                Object.values(Chart.instances).forEach(chart => {
                    if (chart.options) {
                        // Update chart colors
                        if (chart.options.scales) {
                            Object.values(chart.options.scales).forEach(scale => {
                                if (scale.ticks) {
                                    scale.ticks.color = isDark ? '#9ca3af' : '#666666';
                                }
                                if (scale.grid) {
                                    scale.grid.color = isDark ? '#374151' : '#e0e0e0';
                                }
                            });
                        }
                        
                        chart.update();
                    }
                });
            }
        }
    }
    
    // API Methods
    isDarkMode() {
        return this.getEffectiveTheme() === this.THEMES.DARK;
    }
    
    isLightMode() {
        return this.getEffectiveTheme() === this.THEMES.LIGHT;
    }
    
    isAutoMode() {
        return this.currentTheme === this.THEMES.AUTO;
    }
    
    getTheme() {
        return this.currentTheme;
    }
    
    getEffectiveThemeName() {
        return this.getEffectiveTheme();
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Global convenience functions
window.toggleDarkMode = () => themeManager.toggleTheme();
window.setTheme = (theme) => themeManager.setTheme(theme);
window.getTheme = () => themeManager.getTheme();
window.isDarkMode = () => themeManager.isDarkMode();

// Expose theme manager
window.themeManager = themeManager;

// Example usage in console:
// toggleDarkMode()          - Toggle between light and dark
// setTheme('dark')          - Set dark mode
// setTheme('light')         - Set light mode
// setTheme('auto')          - Use system preference
// isDarkMode()              - Check if dark mode is active
// getTheme()                - Get current theme setting

/**
 * Theme Change Event Listener Example:
 * 
 * window.addEventListener('themechange', (e) => {
 *     console.log('Theme changed to:', e.detail.theme);
 *     console.log('Is dark mode:', e.detail.isDark);
 * });
 */
