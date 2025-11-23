/**
 * Toast Notification System
 * Bi Tool v2.1 - Professional toast notifications
 */

class ToastManager {
    constructor(options = {}) {
        this.options = {
            position: options.position || 'top-right',
            duration: options.duration || 5000,
            maxToasts: options.maxToasts || 5,
            showProgress: options.showProgress !== false,
            pauseOnHover: options.pauseOnHover !== false,
            ...options
        };
        
        this.toasts = [];
        this.container = null;
        this.init();
    }
    
    init() {
        // Create toast container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = `toast-container toast-${this.options.position}`;
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }
    
    /**
     * Show a toast notification
     * @param {Object} options - Toast options
     * @param {String} options.type - Toast type: success, error, warning, info, loading
     * @param {String} options.title - Toast title
     * @param {String} options.message - Toast message
     * @param {Number} options.duration - Toast duration in ms (0 = no auto-close)
     * @param {Boolean} options.closable - Show close button
     * @param {Function} options.onClick - Click handler
     * @param {Function} options.onClose - Close handler
     */
    show(options) {
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const toastOptions = {
            type: 'info',
            title: '',
            message: '',
            duration: this.options.duration,
            closable: true,
            showProgress: this.options.showProgress,
            pauseOnHover: this.options.pauseOnHover,
            ...options
        };
        
        // Remove oldest toast if max limit reached
        if (this.toasts.length >= this.options.maxToasts) {
            this.remove(this.toasts[0].id);
        }
        
        // Create toast element
        const toast = this.createToastElement(toastId, toastOptions);
        
        // Add to container
        this.container.appendChild(toast);
        
        // Store toast reference
        const toastData = {
            id: toastId,
            element: toast,
            options: toastOptions,
            startTime: Date.now(),
            pausedTime: 0,
            isPaused: false
        };
        this.toasts.push(toastData);
        
        // Setup auto-close timer
        if (toastOptions.duration > 0) {
            this.setupAutoClose(toastData);
        }
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        return toastId;
    }
    
    createToastElement(toastId, options) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${options.type}`;
        toast.id = toastId;
        
        // Icon
        const icon = this.getIcon(options.type);
        const iconEl = document.createElement('div');
        iconEl.className = 'toast-icon';
        iconEl.innerHTML = icon;
        toast.appendChild(iconEl);
        
        // Content
        const content = document.createElement('div');
        content.className = 'toast-content';
        
        if (options.title) {
            const title = document.createElement('div');
            title.className = 'toast-title';
            title.textContent = options.title;
            content.appendChild(title);
        }
        
        if (options.message) {
            const message = document.createElement('div');
            message.className = 'toast-message';
            message.textContent = options.message;
            content.appendChild(message);
        }
        
        toast.appendChild(content);
        
        // Close button
        if (options.closable) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'toast-close';
            closeBtn.innerHTML = '<i class="fas fa-times"></i>';
            closeBtn.setAttribute('aria-label', 'Close');
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.remove(toastId);
            });
            toast.appendChild(closeBtn);
        }
        
        // Progress bar
        if (options.showProgress && options.duration > 0) {
            const progress = document.createElement('div');
            progress.className = 'toast-progress';
            progress.style.width = '100%';
            toast.appendChild(progress);
        }
        
        // Click handler
        if (options.onClick) {
            toast.style.cursor = 'pointer';
            toast.addEventListener('click', () => {
                options.onClick(toastId);
            });
        }
        
        return toast;
    }
    
    getIcon(type) {
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-times-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>',
            loading: '<i class="fas fa-spinner fa-spin"></i>'
        };
        return icons[type] || icons.info;
    }
    
    setupAutoClose(toastData) {
        const { id, element, options } = toastData;
        
        // Progress bar animation
        if (options.showProgress) {
            const progress = element.querySelector('.toast-progress');
            if (progress) {
                progress.style.transition = `width ${options.duration}ms linear`;
                setTimeout(() => {
                    progress.style.width = '0%';
                }, 10);
            }
        }
        
        // Auto-close timer
        toastData.timer = setTimeout(() => {
            this.remove(id);
        }, options.duration);
        
        // Pause on hover
        if (options.pauseOnHover) {
            element.addEventListener('mouseenter', () => {
                this.pauseToast(toastData);
            });
            
            element.addEventListener('mouseleave', () => {
                this.resumeToast(toastData);
            });
        }
    }
    
    pauseToast(toastData) {
        if (toastData.isPaused) return;
        
        toastData.isPaused = true;
        toastData.pausedTime = Date.now();
        
        // Clear timer
        if (toastData.timer) {
            clearTimeout(toastData.timer);
        }
        
        // Pause progress bar
        const progress = toastData.element.querySelector('.toast-progress');
        if (progress) {
            const computedStyle = window.getComputedStyle(progress);
            progress.style.width = computedStyle.width;
            progress.style.transition = 'none';
        }
    }
    
    resumeToast(toastData) {
        if (!toastData.isPaused) return;
        
        toastData.isPaused = false;
        
        // Calculate remaining time
        const elapsed = toastData.pausedTime - toastData.startTime;
        const remaining = toastData.options.duration - elapsed;
        
        if (remaining <= 0) {
            this.remove(toastData.id);
            return;
        }
        
        // Resume progress bar
        const progress = toastData.element.querySelector('.toast-progress');
        if (progress) {
            progress.style.transition = `width ${remaining}ms linear`;
            progress.style.width = '0%';
        }
        
        // Resume timer
        toastData.timer = setTimeout(() => {
            this.remove(toastData.id);
        }, remaining);
        
        toastData.startTime = Date.now() - elapsed;
    }
    
    remove(toastId) {
        const toastIndex = this.toasts.findIndex(t => t.id === toastId);
        if (toastIndex === -1) return;
        
        const toastData = this.toasts[toastIndex];
        const { element, options } = toastData;
        
        // Clear timer
        if (toastData.timer) {
            clearTimeout(toastData.timer);
        }
        
        // Trigger close animation
        element.classList.add('removing');
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            
            // Call onClose callback
            if (options.onClose) {
                options.onClose(toastId);
            }
        }, 300);
        
        // Remove from array
        this.toasts.splice(toastIndex, 1);
    }
    
    removeAll() {
        this.toasts.forEach(toast => {
            this.remove(toast.id);
        });
    }
    
    // Convenience methods
    success(title, message, options = {}) {
        return this.show({
            type: 'success',
            title,
            message,
            ...options
        });
    }
    
    error(title, message, options = {}) {
        return this.show({
            type: 'error',
            title,
            message,
            duration: options.duration || 7000, // Errors stay longer
            ...options
        });
    }
    
    warning(title, message, options = {}) {
        return this.show({
            type: 'warning',
            title,
            message,
            ...options
        });
    }
    
    info(title, message, options = {}) {
        return this.show({
            type: 'info',
            title,
            message,
            ...options
        });
    }
    
    loading(title, message, options = {}) {
        return this.show({
            type: 'loading',
            title,
            message,
            duration: 0, // Loading toasts don't auto-close
            closable: false,
            showProgress: false,
            ...options
        });
    }
    
    // Update existing toast
    update(toastId, options) {
        const toastData = this.toasts.find(t => t.id === toastId);
        if (!toastData) return;
        
        const { element } = toastData;
        
        // Update type
        if (options.type) {
            element.className = `toast toast-${options.type}`;
            const icon = element.querySelector('.toast-icon');
            if (icon) {
                icon.innerHTML = this.getIcon(options.type);
            }
        }
        
        // Update title
        if (options.title !== undefined) {
            let titleEl = element.querySelector('.toast-title');
            if (!titleEl && options.title) {
                titleEl = document.createElement('div');
                titleEl.className = 'toast-title';
                element.querySelector('.toast-content').prepend(titleEl);
            }
            if (titleEl) {
                titleEl.textContent = options.title;
            }
        }
        
        // Update message
        if (options.message !== undefined) {
            let messageEl = element.querySelector('.toast-message');
            if (!messageEl && options.message) {
                messageEl = document.createElement('div');
                messageEl.className = 'toast-message';
                element.querySelector('.toast-content').appendChild(messageEl);
            }
            if (messageEl) {
                messageEl.textContent = options.message;
            }
        }
        
        // Update duration
        if (options.duration !== undefined) {
            toastData.options.duration = options.duration;
            
            // Clear existing timer
            if (toastData.timer) {
                clearTimeout(toastData.timer);
            }
            
            // Setup new timer if duration > 0
            if (options.duration > 0) {
                toastData.startTime = Date.now();
                this.setupAutoClose(toastData);
            }
        }
    }
}

// Create global toast instance
window.toast = new ToastManager();

// Global convenience functions
window.showToast = {
    success: (title, message, options) => window.toast.success(title, message, options),
    error: (title, message, options) => window.toast.error(title, message, options),
    warning: (title, message, options) => window.toast.warning(title, message, options),
    info: (title, message, options) => window.toast.info(title, message, options),
    loading: (title, message, options) => window.toast.loading(title, message, options)
};
