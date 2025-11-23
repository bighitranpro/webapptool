/**
 * Admin Backup & Restore Manager
 * Bi Tool v2.1
 */

class BackupManager {
    constructor() {
        this.backups = [];
        this.init();
    }
    
    init() {
        this.loadBackups();
        this.setupEventListeners();
        this.loadDatabaseStats();
    }
    
    setupEventListeners() {
        // Create backup button
        const createBtn = document.getElementById('createBackupBtn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.createBackup());
        }
        
        // Restore backup file input
        const restoreInput = document.getElementById('restoreBackupInput');
        if (restoreInput) {
            restoreInput.addEventListener('change', (e) => this.handleRestoreFile(e));
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refreshBackupsBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadBackups());
        }
    }
    
    async createBackup() {
        const btn = document.getElementById('createBackupBtn');
        if (!btn) return;
        
        // Disable button and show loading
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang tạo backup...';
        
        // Show loading toast
        const loadingToast = toast.loading('Đang tạo backup...', 'Vui lòng đợi');
        
        try {
            const response = await fetch('/admin/api/backup/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            // Close loading toast
            toast.remove(loadingToast);
            
            if (result.success) {
                toast.success('Tạo backup thành công!', 
                    `Backup "${result.backup_info.name}" đã được tạo (${this.formatFileSize(result.backup_info.size)})`);
                
                // Reload backup list
                await this.loadBackups();
            } else {
                toast.error('Lỗi tạo backup', result.error || 'Không thể tạo backup');
            }
            
        } catch (error) {
            toast.remove(loadingToast);
            toast.error('Lỗi kết nối', 'Không thể tạo backup: ' + error.message);
        } finally {
            // Re-enable button
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-database"></i> Tạo Backup Mới';
        }
    }
    
    async loadBackups() {
        try {
            const response = await fetch('/admin/api/backup/list');
            const result = await response.json();
            
            if (result.success) {
                this.backups = result.backups;
                this.renderBackupList();
                this.updateBackupStats();
            } else {
                toast.error('Lỗi tải backup', result.error || 'Không thể tải danh sách backup');
            }
            
        } catch (error) {
            toast.error('Lỗi kết nối', 'Không thể tải danh sách backup: ' + error.message);
        }
    }
    
    renderBackupList() {
        const container = document.getElementById('backupListContainer');
        if (!container) return;
        
        if (this.backups.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-database" style="font-size: 48px; color: #666; margin-bottom: 16px;"></i>
                    <p>Chưa có backup nào</p>
                    <p class="text-muted">Nhấn "Tạo Backup Mới" để tạo backup đầu tiên</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="backup-cards-grid">';
        
        this.backups.forEach(backup => {
            const date = new Date(backup.created_at);
            const fileIcon = backup.file_type === 'zip' ? 'fa-file-zipper' : 'fa-file-code';
            
            html += `
                <div class="backup-card">
                    <div class="backup-card-header">
                        <div class="backup-icon">
                            <i class="fas ${fileIcon}"></i>
                        </div>
                        <div class="backup-info">
                            <h4>${backup.filename}</h4>
                            <span class="backup-date">${this.formatDate(date)}</span>
                        </div>
                    </div>
                    <div class="backup-card-body">
                        <div class="backup-meta">
                            <div class="meta-item">
                                <i class="fas fa-hdd"></i>
                                <span>${this.formatFileSize(backup.file_size)}</span>
                            </div>
                            <div class="meta-item">
                                <i class="fas fa-clock"></i>
                                <span>${this.formatTime(date)}</span>
                            </div>
                        </div>
                    </div>
                    <div class="backup-card-footer">
                        <button class="btn btn-sm btn-primary" onclick="backupManager.downloadBackup('${backup.filename}')">
                            <i class="fas fa-download"></i> Tải về
                        </button>
                        <button class="btn btn-sm btn-success" onclick="backupManager.prepareRestore('${backup.filename}')">
                            <i class="fas fa-undo"></i> Restore
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="backupManager.deleteBackup('${backup.filename}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    updateBackupStats() {
        // Update backup count
        const countEl = document.getElementById('backupCount');
        if (countEl) {
            countEl.textContent = this.backups.length;
        }
        
        // Calculate total size
        const totalSize = this.backups.reduce((sum, backup) => sum + backup.file_size, 0);
        const sizeEl = document.getElementById('backupTotalSize');
        if (sizeEl) {
            sizeEl.textContent = this.formatFileSize(totalSize);
        }
        
        // Latest backup
        if (this.backups.length > 0) {
            const latest = this.backups[0];
            const latestEl = document.getElementById('latestBackup');
            if (latestEl) {
                const date = new Date(latest.created_at);
                latestEl.textContent = this.formatDate(date);
            }
        }
    }
    
    async downloadBackup(filename) {
        try {
            // Show loading toast
            const loadingToast = toast.loading('Đang tải xuống...', 'Đang chuẩn bị file backup');
            
            // Download file
            window.location.href = `/admin/api/backup/download/${encodeURIComponent(filename)}`;
            
            // Close loading toast after a delay
            setTimeout(() => {
                toast.remove(loadingToast);
                toast.success('Tải xuống thành công!', `Backup "${filename}" đã được tải về`);
            }, 1000);
            
        } catch (error) {
            toast.error('Lỗi tải xuống', 'Không thể tải backup: ' + error.message);
        }
    }
    
    prepareRestore(filename) {
        // Show restore confirmation modal
        const modal = document.getElementById('restoreBackupModal');
        if (!modal) {
            this.showRestoreDialog(filename);
            return;
        }
        
        // Set filename
        document.getElementById('restoreBackupName').textContent = filename;
        document.getElementById('restoreBackupFilename').value = filename;
        
        // Show modal
        modal.style.display = 'flex';
    }
    
    showRestoreDialog(filename) {
        const confirmed = confirm(
            `Bạn có chắc muốn restore backup "${filename}"?\n\n` +
            `Cảnh báo: Thao tác này sẽ thay thế dữ liệu hiện tại!\n\n` +
            `Nhấn OK để tiếp tục.`
        );
        
        if (confirmed) {
            const mode = prompt(
                'Chọn chế độ restore:\n\n' +
                '1. replace - Thay thế hoàn toàn (mặc định)\n' +
                '2. merge - Gộp dữ liệu (bỏ qua trùng lặp)\n' +
                '3. append - Thêm tất cả\n\n' +
                'Nhập số (1-3):',
                '1'
            );
            
            const modes = { '1': 'replace', '2': 'merge', '3': 'append' };
            const restoreMode = modes[mode] || 'replace';
            
            this.restoreBackupByFilename(filename, restoreMode);
        }
    }
    
    async restoreBackupByFilename(filename, mode) {
        // Show loading
        const loadingToast = toast.loading('Đang restore...', 'Vui lòng đợi, đừng tắt trang');
        
        try {
            // Create form data
            const formData = new FormData();
            
            // Get the backup file
            const response = await fetch(`/admin/api/backup/download/${encodeURIComponent(filename)}`);
            const blob = await response.blob();
            formData.append('backup_file', blob, filename);
            formData.append('restore_mode', mode);
            
            // Restore
            const restoreResponse = await fetch('/admin/api/backup/restore', {
                method: 'POST',
                body: formData
            });
            
            const result = await restoreResponse.json();
            
            toast.remove(loadingToast);
            
            if (result.success) {
                toast.success('Restore thành công!', 'Database đã được restore');
                
                // Show detailed results
                console.log('Restore info:', result.restore_info);
                
                // Reload page after 2 seconds
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                toast.error('Lỗi restore', result.error || 'Không thể restore backup');
            }
            
        } catch (error) {
            toast.remove(loadingToast);
            toast.error('Lỗi kết nối', 'Không thể restore backup: ' + error.message);
        }
    }
    
    async handleRestoreFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type
        if (!file.name.endsWith('.zip') && !file.name.endsWith('.json')) {
            toast.error('File không hợp lệ', 'Chỉ chấp nhận file .zip hoặc .json');
            event.target.value = '';
            return;
        }
        
        // Get restore mode
        const modeSelect = document.getElementById('restoreModeSelect');
        const mode = modeSelect ? modeSelect.value : 'replace';
        
        // Show confirmation
        const confirmed = confirm(
            `Bạn có chắc muốn restore từ file "${file.name}"?\n\n` +
            `Chế độ: ${mode}\n` +
            `Cảnh báo: Thao tác này có thể thay đổi dữ liệu hiện tại!\n\n` +
            `Nhấn OK để tiếp tục.`
        );
        
        if (!confirmed) {
            event.target.value = '';
            return;
        }
        
        // Show loading
        const loadingToast = toast.loading('Đang restore...', 'Vui lòng đợi, đừng tắt trang');
        
        try {
            // Create form data
            const formData = new FormData();
            formData.append('backup_file', file);
            formData.append('restore_mode', mode);
            
            // Restore
            const response = await fetch('/admin/api/backup/restore', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            toast.remove(loadingToast);
            
            if (result.success) {
                toast.success('Restore thành công!', 'Database đã được restore');
                
                // Reset file input
                event.target.value = '';
                
                // Reload page after 2 seconds
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                toast.error('Lỗi restore', result.error || 'Không thể restore backup');
            }
            
        } catch (error) {
            toast.remove(loadingToast);
            toast.error('Lỗi kết nối', 'Không thể restore backup: ' + error.message);
        }
    }
    
    async deleteBackup(filename) {
        const confirmed = confirm(
            `Bạn có chắc muốn xóa backup "${filename}"?\n\n` +
            `Thao tác này không thể hoàn tác!`
        );
        
        if (!confirmed) return;
        
        try {
            const response = await fetch(`/admin/api/backup/delete/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                toast.success('Đã xóa backup', `Backup "${filename}" đã được xóa`);
                await this.loadBackups();
            } else {
                toast.error('Lỗi xóa backup', result.error || 'Không thể xóa backup');
            }
            
        } catch (error) {
            toast.error('Lỗi kết nối', 'Không thể xóa backup: ' + error.message);
        }
    }
    
    async loadDatabaseStats() {
        try {
            const response = await fetch('/admin/api/database/stats');
            const result = await response.json();
            
            if (result.success) {
                this.renderDatabaseStats(result.stats);
            }
            
        } catch (error) {
            console.error('Error loading database stats:', error);
        }
    }
    
    renderDatabaseStats(stats) {
        // Update database size
        const sizeEl = document.getElementById('databaseSize');
        if (sizeEl) {
            sizeEl.textContent = this.formatFileSize(stats.database_size);
        }
        
        // Update table count
        const tableCountEl = document.getElementById('tableCount');
        if (tableCountEl) {
            tableCountEl.textContent = stats.table_count;
        }
        
        // Update total rows
        const rowCountEl = document.getElementById('totalRows');
        if (rowCountEl) {
            rowCountEl.textContent = stats.total_rows.toLocaleString();
        }
        
        // Render table list
        const tableListEl = document.getElementById('databaseTablesList');
        if (tableListEl && stats.tables) {
            let html = '<div class="table-list">';
            
            for (const [tableName, tableInfo] of Object.entries(stats.tables)) {
                html += `
                    <div class="table-item">
                        <div class="table-name">
                            <i class="fas fa-table"></i>
                            ${tableName}
                        </div>
                        <div class="table-stats">
                            <span>${tableInfo.row_count.toLocaleString()} rows</span>
                            <span>${tableInfo.column_count} columns</span>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            tableListEl.innerHTML = html;
        }
    }
    
    // Utility functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
    
    formatDate(date) {
        const options = { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit'
        };
        return date.toLocaleDateString('vi-VN', options);
    }
    
    formatTime(date) {
        const options = { 
            hour: '2-digit', 
            minute: '2-digit'
        };
        return date.toLocaleTimeString('vi-VN', options);
    }
}

// Initialize backup manager
let backupManager;
document.addEventListener('DOMContentLoaded', function() {
    backupManager = new BackupManager();
});
