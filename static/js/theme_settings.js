/**
 * Theme Settings Manager
 * Handles theme customization, saving, and loading
 */

class ThemeSettingsManager {
    constructor() {
        this.presets = {
            professional: {
                primary_color: '#ffd700',
                secondary_color: '#00d9ff',
                accent_color: '#ff6b35',
                background_color: '#0a0e27',
                text_color: '#ffffff'
            },
            creative: {
                primary_color: '#ff006e',
                secondary_color: '#8338ec',
                accent_color: '#3a86ff',
                background_color: '#1a1a2e',
                text_color: '#ffffff'
            },
            minimal: {
                primary_color: '#000000',
                secondary_color: '#ffffff',
                accent_color: '#6c757d',
                background_color: '#f8f9fa',
                text_color: '#212529'
            },
            bold: {
                primary_color: '#ff0000',
                secondary_color: '#00ff00',
                accent_color: '#0000ff',
                background_color: '#000000',
                text_color: '#ffffff'
            },
            elegant: {
                primary_color: '#a78bfa',
                secondary_color: '#60a5fa',
                accent_color: '#34d399',
                background_color: '#1e1b4b',
                text_color: '#f3f4f6'
            }
        };
        
        this.currentTheme = {};
        this.init();
    }

    init() {
        this.loadThemeSettings();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Settings tab switching
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });

        // Theme mode selector
        document.querySelectorAll('.theme-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.theme-mode-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });

        // Preset themes
        document.querySelectorAll('.preset-theme').forEach(preset => {
            preset.addEventListener('click', (e) => {
                const presetName = e.currentTarget.getAttribute('data-preset');
                this.applyPreset(presetName);
            });
        });

        // Color pickers
        const colorInputs = ['primaryColor', 'secondaryColor', 'accentColor'];
        colorInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', (e) => {
                    const value = e.target.value;
                    const valueSpan = e.target.parentElement.querySelector('.color-value');
                    if (valueSpan) {
                        valueSpan.textContent = value;
                    }
                    this.applyColorChange(id, value);
                });
            }
        });

        // Sliders with real-time preview
        const sliders = [
            { id: 'fontSize', valueId: 'fontSizeValue', suffix: 'px', cssVar: '--font-size-base' },
            { id: 'sidebarWidth', valueId: 'sidebarWidthValue', suffix: 'px', cssVar: '--sidebar-width' },
            { id: 'borderRadius', valueId: 'borderRadiusValue', suffix: 'px', cssVar: '--border-radius' },
            { id: 'animationSpeed', valueId: 'animationSpeedValue', suffix: 's', cssVar: '--animation-speed' }
        ];

        sliders.forEach(slider => {
            const input = document.getElementById(slider.id);
            if (input) {
                input.addEventListener('input', (e) => {
                    const value = e.target.value;
                    const valueSpan = document.getElementById(slider.valueId);
                    if (valueSpan) {
                        valueSpan.textContent = value + slider.suffix;
                    }
                    if (slider.cssVar) {
                        document.documentElement.style.setProperty(slider.cssVar, value + slider.suffix);
                    }
                });
            }
        });

        // Font family selector
        const fontFamily = document.getElementById('fontFamily');
        if (fontFamily) {
            fontFamily.addEventListener('change', (e) => {
                document.documentElement.style.setProperty('--font-primary', e.target.value);
            });
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`.settings-tab[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.settings-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        const contentMap = {
            'profile': 'profileTab',
            'theme': 'themeTab',
            'preferences': 'preferencesTab',
            'api': 'apiTab',
            'security': 'securityTab'
        };
        
        const contentId = contentMap[tabName];
        if (contentId) {
            document.getElementById(contentId).classList.add('active');
        }
    }

    applyPreset(presetName) {
        const preset = this.presets[presetName];
        if (!preset) return;

        // Update UI
        document.querySelectorAll('.preset-theme').forEach(p => p.classList.remove('active'));
        document.querySelector(`[data-preset="${presetName}"]`).classList.add('active');

        // Apply colors
        if (document.getElementById('primaryColor')) {
            document.getElementById('primaryColor').value = preset.primary_color;
            document.querySelector('#primaryColor').parentElement.querySelector('.color-value').textContent = preset.primary_color;
        }
        if (document.getElementById('secondaryColor')) {
            document.getElementById('secondaryColor').value = preset.secondary_color;
            document.querySelector('#secondaryColor').parentElement.querySelector('.color-value').textContent = preset.secondary_color;
        }
        if (document.getElementById('accentColor')) {
            document.getElementById('accentColor').value = preset.accent_color;
            document.querySelector('#accentColor').parentElement.querySelector('.color-value').textContent = preset.accent_color;
        }

        // Apply to CSS variables
        document.documentElement.style.setProperty('--primary-color', preset.primary_color);
        document.documentElement.style.setProperty('--secondary-color', preset.secondary_color);
        document.documentElement.style.setProperty('--accent-color', preset.accent_color);
    }

    applyColorChange(inputId, value) {
        const colorMap = {
            'primaryColor': '--primary-color',
            'secondaryColor': '--secondary-color',
            'accentColor': '--accent-color'
        };

        const cssVar = colorMap[inputId];
        if (cssVar) {
            document.documentElement.style.setProperty(cssVar, value);
        }
    }

    async loadThemeSettings() {
        try {
            const response = await fetch('/api/admin/theme/settings');
            const data = await response.json();
            
            if (data.success && data.theme) {
                this.currentTheme = data.theme;
                this.applyTheme(data.theme);
            }
        } catch (error) {
            console.error('Failed to load theme settings:', error);
        }
    }

    applyTheme(theme) {
        // Apply CSS variables
        if (theme.primary_color) {
            document.documentElement.style.setProperty('--primary-color', theme.primary_color);
            if (document.getElementById('primaryColor')) {
                document.getElementById('primaryColor').value = theme.primary_color;
                document.querySelector('#primaryColor').parentElement.querySelector('.color-value').textContent = theme.primary_color;
            }
        }
        
        if (theme.secondary_color) {
            document.documentElement.style.setProperty('--secondary-color', theme.secondary_color);
            if (document.getElementById('secondaryColor')) {
                document.getElementById('secondaryColor').value = theme.secondary_color;
                document.querySelector('#secondaryColor').parentElement.querySelector('.color-value').textContent = theme.secondary_color;
            }
        }
        
        if (theme.accent_color) {
            document.documentElement.style.setProperty('--accent-color', theme.accent_color);
            if (document.getElementById('accentColor')) {
                document.getElementById('accentColor').value = theme.accent_color;
                document.querySelector('#accentColor').parentElement.querySelector('.color-value').textContent = theme.accent_color;
            }
        }

        if (theme.font_family && document.getElementById('fontFamily')) {
            document.getElementById('fontFamily').value = theme.font_family;
            document.documentElement.style.setProperty('--font-primary', theme.font_family);
        }

        if (theme.font_size_base) {
            const size = parseInt(theme.font_size_base);
            if (document.getElementById('fontSize')) {
                document.getElementById('fontSize').value = size;
                document.getElementById('fontSizeValue').textContent = size + 'px';
            }
            document.documentElement.style.setProperty('--font-size-base', theme.font_size_base);
        }

        if (theme.sidebar_width) {
            const width = parseInt(theme.sidebar_width);
            if (document.getElementById('sidebarWidth')) {
                document.getElementById('sidebarWidth').value = width;
                document.getElementById('sidebarWidthValue').textContent = width + 'px';
            }
            document.documentElement.style.setProperty('--sidebar-width', theme.sidebar_width);
        }

        if (theme.border_radius) {
            const radius = parseInt(theme.border_radius);
            if (document.getElementById('borderRadius')) {
                document.getElementById('borderRadius').value = radius;
                document.getElementById('borderRadiusValue').textContent = radius + 'px';
            }
            document.documentElement.style.setProperty('--border-radius', theme.border_radius);
        }

        if (theme.animation_speed) {
            const speed = parseFloat(theme.animation_speed);
            if (document.getElementById('animationSpeed')) {
                document.getElementById('animationSpeed').value = speed;
                document.getElementById('animationSpeedValue').textContent = speed + 's';
            }
            document.documentElement.style.setProperty('--animation-speed', theme.animation_speed);
        }
    }

    getThemeFromUI() {
        return {
            theme_mode: document.querySelector('.theme-mode-btn.active')?.getAttribute('data-mode') || 'dark',
            primary_color: document.getElementById('primaryColor')?.value || '#ffd700',
            secondary_color: document.getElementById('secondaryColor')?.value || '#00d9ff',
            accent_color: document.getElementById('accentColor')?.value || '#ff6b35',
            background_color: '#0a0e27',
            text_color: '#ffffff',
            font_family: document.getElementById('fontFamily')?.value || 'Inter',
            font_size_base: document.getElementById('fontSize')?.value + 'px' || '16px',
            sidebar_width: document.getElementById('sidebarWidth')?.value + 'px' || '280px',
            border_radius: document.getElementById('borderRadius')?.value + 'px' || '12px',
            animation_speed: document.getElementById('animationSpeed')?.value + 's' || '0.3s'
        };
    }
}

// Global functions for button actions
async function saveThemeSettings() {
    const manager = window.themeManager;
    const theme = manager.getThemeFromUI();

    try {
        const response = await fetch('/api/admin/theme/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ theme })
        });

        const data = await response.json();
        
        if (data.success) {
            showNotification('Đã lưu cài đặt giao diện thành công!', 'success');
        } else {
            showNotification('Lỗi khi lưu cài đặt: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Save theme error:', error);
        showNotification('Lỗi kết nối khi lưu cài đặt', 'error');
    }
}

async function resetThemeSettings() {
    if (!confirm('Bạn có chắc muốn đặt lại giao diện về mặc định?')) {
        return;
    }

    try {
        const response = await fetch('/api/admin/theme/reset', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.success) {
            window.themeManager.applyTheme(data.theme);
            showNotification('Đã đặt lại giao diện về mặc định!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Lỗi khi đặt lại: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Reset theme error:', error);
        showNotification('Lỗi kết nối khi đặt lại giao diện', 'error');
    }
}

function exportTheme() {
    const manager = window.themeManager;
    const theme = manager.getThemeFromUI();
    
    const dataStr = JSON.stringify(theme, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `bighi-theme-${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    showNotification('Đã xuất giao diện thành công!', 'success');
}

function showNotification(message, type = 'info') {
    // Simple notification implementation
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeSettingsManager();
});
