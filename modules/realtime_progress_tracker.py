"""
Real-time Progress Tracker Module
Track and broadcast batch processing progress in real-time
"""

import time
import threading
from datetime import datetime
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressData:
    """Progress data structure"""
    task_id: str
    task_name: str
    status: str
    current: int
    total: int
    percentage: float
    processed_items: list
    errors: list
    started_at: str
    updated_at: str
    estimated_time_remaining: Optional[float] = None
    speed: Optional[float] = None  # items per second
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RealtimeProgressTracker:
    """Track batch processing progress with real-time updates"""
    
    def __init__(self):
        self.tasks: Dict[str, ProgressData] = {}
        self.lock = threading.Lock()
        self.callbacks = []  # List of callback functions
    
    def create_task(self, task_id: str, task_name: str, total: int, 
                    metadata: Optional[Dict] = None) -> str:
        """
        Create a new task for tracking
        
        Args:
            task_id: Unique task identifier
            task_name: Human-readable task name
            total: Total number of items to process
            metadata: Additional task metadata
        
        Returns:
            Task ID
        """
        with self.lock:
            progress = ProgressData(
                task_id=task_id,
                task_name=task_name,
                status=TaskStatus.PENDING.value,
                current=0,
                total=total,
                percentage=0.0,
                processed_items=[],
                errors=[],
                started_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.tasks[task_id] = progress
            self._notify_update(task_id)
        
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Mark task as started"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            self.tasks[task_id].status = TaskStatus.RUNNING.value
            self.tasks[task_id].started_at = datetime.now().isoformat()
            self.tasks[task_id].updated_at = datetime.now().isoformat()
            self._notify_update(task_id)
        
        return True
    
    def update_progress(self, task_id: str, current: int, 
                       processed_item: Optional[Dict] = None,
                       error: Optional[Dict] = None) -> bool:
        """
        Update task progress
        
        Args:
            task_id: Task identifier
            current: Current progress count
            processed_item: Newly processed item data
            error: Error information if any
        
        Returns:
            Success status
        """
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.current = current
            task.percentage = round((current / task.total * 100), 2) if task.total > 0 else 0
            task.updated_at = datetime.now().isoformat()
            
            # Calculate speed and ETA
            started = datetime.fromisoformat(task.started_at)
            elapsed = (datetime.now() - started).total_seconds()
            
            if elapsed > 0:
                task.speed = round(current / elapsed, 2)
                
                if task.speed > 0:
                    remaining_items = task.total - current
                    task.estimated_time_remaining = round(remaining_items / task.speed, 2)
            
            # Add processed item
            if processed_item:
                task.processed_items.append({
                    'data': processed_item,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Keep only last 100 items to save memory
                if len(task.processed_items) > 100:
                    task.processed_items = task.processed_items[-100:]
            
            # Add error
            if error:
                task.errors.append({
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })
            
            self._notify_update(task_id)
        
        return True
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Mark task as completed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED.value if success else TaskStatus.FAILED.value
            task.percentage = 100.0
            task.updated_at = datetime.now().isoformat()
            task.estimated_time_remaining = 0
            
            self._notify_update(task_id)
        
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a running task"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.RUNNING.value:
                return False
            
            task.status = TaskStatus.PAUSED.value
            task.updated_at = datetime.now().isoformat()
            self._notify_update(task_id)
        
        return True
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status != TaskStatus.PAUSED.value:
                return False
            
            task.status = TaskStatus.RUNNING.value
            task.updated_at = datetime.now().isoformat()
            self._notify_update(task_id)
        
        return True
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = TaskStatus.CANCELLED.value
            task.updated_at = datetime.now().isoformat()
            self._notify_update(task_id)
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task progress data"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            
            return asdict(task)
    
    def get_all_tasks(self) -> Dict[str, Dict]:
        """Get all tasks"""
        with self.lock:
            return {
                task_id: asdict(task)
                for task_id, task in self.tasks.items()
            }
    
    def get_active_tasks(self) -> Dict[str, Dict]:
        """Get only active (running) tasks"""
        with self.lock:
            return {
                task_id: asdict(task)
                for task_id, task in self.tasks.items()
                if task.status == TaskStatus.RUNNING.value
            }
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task from tracker"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            del self.tasks[task_id]
            self._notify_update(task_id, deleted=True)
        
        return True
    
    def cleanup_old_tasks(self, max_age_seconds: int = 3600) -> int:
        """
        Cleanup completed tasks older than specified age
        
        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour)
        
        Returns:
            Number of tasks cleaned up
        """
        cleaned_count = 0
        current_time = datetime.now()
        
        with self.lock:
            tasks_to_delete = []
            
            for task_id, task in self.tasks.items():
                if task.status in [TaskStatus.COMPLETED.value, 
                                  TaskStatus.FAILED.value, 
                                  TaskStatus.CANCELLED.value]:
                    
                    updated_at = datetime.fromisoformat(task.updated_at)
                    age = (current_time - updated_at).total_seconds()
                    
                    if age > max_age_seconds:
                        tasks_to_delete.append(task_id)
            
            for task_id in tasks_to_delete:
                del self.tasks[task_id]
                cleaned_count += 1
        
        return cleaned_count
    
    def register_callback(self, callback: Callable[[str, Dict], None]):
        """
        Register a callback function for progress updates
        
        Args:
            callback: Function that takes (task_id, progress_data) as arguments
        """
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[str, Dict], None]):
        """Unregister a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_update(self, task_id: str, deleted: bool = False):
        """Notify all registered callbacks of an update"""
        if deleted:
            data = {'deleted': True}
        else:
            task = self.tasks.get(task_id)
            data = asdict(task) if task else None
        
        for callback in self.callbacks:
            try:
                callback(task_id, data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        with self.lock:
            stats = {
                'total_tasks': len(self.tasks),
                'pending': 0,
                'running': 0,
                'paused': 0,
                'completed': 0,
                'failed': 0,
                'cancelled': 0,
                'total_processed': 0,
                'total_errors': 0
            }
            
            for task in self.tasks.values():
                stats[task.status] = stats.get(task.status, 0) + 1
                stats['total_processed'] += task.current
                stats['total_errors'] += len(task.errors)
            
            return stats


# Global tracker instance
_global_tracker = RealtimeProgressTracker()


def get_global_tracker() -> RealtimeProgressTracker:
    """Get the global progress tracker instance"""
    return _global_tracker


# Example usage with decorator
def track_progress(task_name: str, total_items: int):
    """
    Decorator for tracking function progress
    
    Usage:
        @track_progress("Processing emails", 100)
        def process_emails(tracker, task_id, emails):
            for i, email in enumerate(emails):
                # Process email
                result = validate_email(email)
                
                # Update progress
                tracker.update_progress(task_id, i + 1, processed_item=result)
            
            tracker.complete_task(task_id)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import uuid
            
            tracker = get_global_tracker()
            task_id = str(uuid.uuid4())
            
            tracker.create_task(task_id, task_name, total_items)
            tracker.start_task(task_id)
            
            try:
                result = func(tracker, task_id, *args, **kwargs)
                tracker.complete_task(task_id, success=True)
                return result
            except Exception as e:
                tracker.complete_task(task_id, success=False)
                raise
        
        return wrapper
    return decorator


# Example usage
if __name__ == '__main__':
    import uuid
    
    tracker = RealtimeProgressTracker()
    
    # Create a task
    task_id = str(uuid.uuid4())
    tracker.create_task(task_id, "Email Validation", 100)
    
    # Start task
    tracker.start_task(task_id)
    
    # Simulate processing
    for i in range(100):
        time.sleep(0.01)  # Simulate work
        
        tracker.update_progress(
            task_id, 
            i + 1,
            processed_item={'email': f'test{i}@example.com', 'status': 'LIVE'}
        )
        
        # Simulate occasional error
        if i % 20 == 0:
            tracker.update_progress(
                task_id,
                i + 1,
                error={'message': 'Connection timeout', 'email': f'bad{i}@example.com'}
            )
    
    # Complete task
    tracker.complete_task(task_id)
    
    # Get final result
    result = tracker.get_task(task_id)
    print(f"Task completed: {result['percentage']}%")
    print(f"Speed: {result['speed']} items/sec")
    print(f"Errors: {len(result['errors'])}")
