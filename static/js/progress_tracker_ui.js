/**
 * Progress Tracker UI Manager
 * Real-time progress monitoring for batch operations
 */

class ProgressTrackerUI {
    constructor() {
        this.activeTasks = new Map();
        this.updateInterval = null;
        this.refreshRate = 1000; // Update every second
        this.init();
    }

    init() {
        this.startAutoRefresh();
        this.loadActiveTasks();
    }

    startAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            this.refreshActiveTasks();
        }, this.refreshRate);
    }

    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async loadActiveTasks() {
        try {
            const response = await fetch('/api/progress/active');
            const data = await response.json();

            if (data.success) {
                this.updateTasksDisplay(data.tasks);
            }
        } catch (error) {
            console.error('Failed to load active tasks:', error);
        }
    }

    async refreshActiveTasks() {
        // Only refresh if there are active tasks
        if (this.activeTasks.size === 0) {
            return;
        }

        await this.loadActiveTasks();
    }

    async getTaskProgress(taskId) {
        try {
            const response = await fetch(`/api/progress/${taskId}`);
            const data = await response.json();

            if (data.success) {
                return data.task;
            }
            return null;
        } catch (error) {
            console.error(`Failed to get task ${taskId}:`, error);
            return null;
        }
    }

    updateTasksDisplay(tasks) {
        const container = document.getElementById('progressTasksContainer');
        if (!container) return;

        // Clear old tasks map
        this.activeTasks.clear();

        // If no tasks, show empty state
        if (Object.keys(tasks).length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clipboard-check"></i>
                    <p>Không có task nào đang chạy</p>
                </div>
            `;
            return;
        }

        let html = '<div class="progress-tasks-grid">';

        for (const [taskId, task] of Object.entries(tasks)) {
            this.activeTasks.set(taskId, task);
            html += this.renderTaskCard(taskId, task);
        }

        html += '</div>';
        container.innerHTML = html;
    }

    renderTaskCard(taskId, task) {
        const percentage = task.percentage || 0;
        const statusClass = this.getStatusClass(task.status);
        const statusIcon = this.getStatusIcon(task.status);

        return `
            <div class="progress-task-card ${statusClass}" data-task-id="${taskId}">
                <div class="task-card-header">
                    <div class="task-info">
                        <h4>
                            <i class="${statusIcon}"></i>
                            ${task.task_name}
                        </h4>
                        <span class="task-id">#${taskId.substring(0, 8)}</span>
                    </div>
                    <div class="task-actions">
                        ${this.renderTaskActions(taskId, task.status)}
                    </div>
                </div>

                <div class="task-card-body">
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${percentage}%">
                            <span class="progress-text">${percentage.toFixed(1)}%</span>
                        </div>
                    </div>

                    <div class="task-stats">
                        <div class="task-stat">
                            <i class="fas fa-tasks"></i>
                            <span>${task.current} / ${task.total}</span>
                        </div>
                        ${task.speed ? `
                            <div class="task-stat">
                                <i class="fas fa-tachometer-alt"></i>
                                <span>${task.speed.toFixed(1)} items/s</span>
                            </div>
                        ` : ''}
                        ${task.estimated_time_remaining !== null ? `
                            <div class="task-stat">
                                <i class="fas fa-clock"></i>
                                <span>ETA: ${this.formatTime(task.estimated_time_remaining)}</span>
                            </div>
                        ` : ''}
                    </div>

                    ${task.errors && task.errors.length > 0 ? `
                        <div class="task-errors">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>${task.errors.length} errors</span>
                            <button onclick="progressTrackerUI.showTaskErrors('${taskId}')" class="btn-link">
                                View
                            </button>
                        </div>
                    ` : ''}
                </div>

                <div class="task-card-footer">
                    <small class="task-time">Started: ${this.formatDateTime(task.started_at)}</small>
                    <small class="task-time">Updated: ${this.formatDateTime(task.updated_at)}</small>
                </div>
            </div>
        `;
    }

    renderTaskActions(taskId, status) {
        let actions = '';

        if (status === 'running') {
            actions += `
                <button onclick="progressTrackerUI.pauseTask('${taskId}')" class="btn-icon" title="Pause">
                    <i class="fas fa-pause"></i>
                </button>
                <button onclick="progressTrackerUI.cancelTask('${taskId}')" class="btn-icon btn-danger" title="Cancel">
                    <i class="fas fa-times"></i>
                </button>
            `;
        } else if (status === 'paused') {
            actions += `
                <button onclick="progressTrackerUI.resumeTask('${taskId}')" class="btn-icon" title="Resume">
                    <i class="fas fa-play"></i>
                </button>
                <button onclick="progressTrackerUI.cancelTask('${taskId}')" class="btn-icon btn-danger" title="Cancel">
                    <i class="fas fa-times"></i>
                </button>
            `;
        } else if (status === 'completed' || status === 'failed' || status === 'cancelled') {
            actions += `
                <button onclick="progressTrackerUI.deleteTask('${taskId}')" class="btn-icon btn-danger" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }

        return actions;
    }

    getStatusClass(status) {
        const classes = {
            'pending': 'status-pending',
            'running': 'status-running',
            'paused': 'status-paused',
            'completed': 'status-completed',
            'failed': 'status-failed',
            'cancelled': 'status-cancelled'
        };
        return classes[status] || '';
    }

    getStatusIcon(status) {
        const icons = {
            'pending': 'fas fa-clock',
            'running': 'fas fa-spinner fa-spin',
            'paused': 'fas fa-pause-circle',
            'completed': 'fas fa-check-circle',
            'failed': 'fas fa-times-circle',
            'cancelled': 'fas fa-ban'
        };
        return icons[status] || 'fas fa-circle';
    }

    formatTime(seconds) {
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const secs = Math.round(seconds % 60);
            return `${minutes}m ${secs}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }

    formatDateTime(isoString) {
        if (!isoString) return 'N/A';
        
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) {
            return 'Just now';
        } else if (diffMins < 60) {
            return `${diffMins}m ago`;
        } else if (diffMins < 1440) {
            const hours = Math.floor(diffMins / 60);
            return `${hours}h ago`;
        } else {
            return date.toLocaleString('vi-VN', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    async pauseTask(taskId) {
        try {
            const response = await fetch(`/api/progress/${taskId}/pause`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                if (typeof showNotification !== 'undefined') {
                    showNotification('Task đã được pause', 'success');
                }
                await this.loadActiveTasks();
            } else {
                if (typeof showNotification !== 'undefined') {
                    showNotification(data.message || 'Lỗi khi pause task', 'error');
                }
            }
        } catch (error) {
            console.error('Pause task error:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification('Lỗi kết nối', 'error');
            }
        }
    }

    async resumeTask(taskId) {
        try {
            const response = await fetch(`/api/progress/${taskId}/resume`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                if (typeof showNotification !== 'undefined') {
                    showNotification('Task đã được resume', 'success');
                }
                await this.loadActiveTasks();
            } else {
                if (typeof showNotification !== 'undefined') {
                    showNotification(data.message || 'Lỗi khi resume task', 'error');
                }
            }
        } catch (error) {
            console.error('Resume task error:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification('Lỗi kết nối', 'error');
            }
        }
    }

    async cancelTask(taskId) {
        if (!confirm('Bạn có chắc muốn hủy task này?')) {
            return;
        }

        try {
            const response = await fetch(`/api/progress/${taskId}/cancel`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                if (typeof showNotification !== 'undefined') {
                    showNotification('Task đã được hủy', 'success');
                }
                await this.loadActiveTasks();
            } else {
                if (typeof showNotification !== 'undefined') {
                    showNotification(data.message || 'Lỗi khi hủy task', 'error');
                }
            }
        } catch (error) {
            console.error('Cancel task error:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification('Lỗi kết nối', 'error');
            }
        }
    }

    async deleteTask(taskId) {
        if (!confirm('Bạn có chắc muốn xóa task này?')) {
            return;
        }

        try {
            const response = await fetch(`/api/progress/${taskId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                if (typeof showNotification !== 'undefined') {
                    showNotification('Task đã được xóa', 'success');
                }
                await this.loadActiveTasks();
            } else {
                if (typeof showNotification !== 'undefined') {
                    showNotification(data.message || 'Lỗi khi xóa task', 'error');
                }
            }
        } catch (error) {
            console.error('Delete task error:', error);
            if (typeof showNotification !== 'undefined') {
                showNotification('Lỗi kết nối', 'error');
            }
        }
    }

    async showTaskErrors(taskId) {
        const task = await this.getTaskProgress(taskId);
        if (!task || !task.errors || task.errors.length === 0) {
            if (typeof showNotification !== 'undefined') {
                showNotification('Không có lỗi nào', 'info');
            }
            return;
        }

        // Create modal to show errors
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-exclamation-triangle"></i> Task Errors</h3>
                    <span class="modal-close" onclick="this.closest('.modal').remove()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="errors-list">
                        ${task.errors.map((err, i) => `
                            <div class="error-item">
                                <div class="error-number">${i + 1}</div>
                                <div class="error-details">
                                    <div class="error-message">${JSON.stringify(err.error)}</div>
                                    <div class="error-time">${this.formatDateTime(err.timestamp)}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/progress/statistics');
            const data = await response.json();

            if (data.success) {
                this.updateStatisticsDisplay(data.statistics);
            }
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }

    updateStatisticsDisplay(stats) {
        const container = document.getElementById('progressStatsContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <i class="fas fa-tasks"></i>
                    <div class="stat-value">${stats.total_tasks}</div>
                    <div class="stat-label">Total Tasks</div>
                </div>
                <div class="stat-card status-running">
                    <i class="fas fa-spinner"></i>
                    <div class="stat-value">${stats.running}</div>
                    <div class="stat-label">Running</div>
                </div>
                <div class="stat-card status-completed">
                    <i class="fas fa-check-circle"></i>
                    <div class="stat-value">${stats.completed}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card status-failed">
                    <i class="fas fa-times-circle"></i>
                    <div class="stat-value">${stats.failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
            </div>
        `;
    }
}

// Initialize global progress tracker UI
let progressTrackerUI;

document.addEventListener('DOMContentLoaded', () => {
    progressTrackerUI = new ProgressTrackerUI();
});

// Expose for inline onclick handlers
window.progressTrackerUI = progressTrackerUI;
