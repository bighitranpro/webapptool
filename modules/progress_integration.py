"""
Progress Integration Module
Wraps existing email operations with real-time progress tracking
"""

import time
import threading
from typing import List, Dict, Any, Callable
from .realtime_progress_tracker import get_global_tracker


class ProgressIntegration:
    """
    Integrates progress tracking into email operations
    """
    
    def __init__(self):
        self.tracker = get_global_tracker()
    
    def validate_with_progress(
        self, 
        emails: List[str], 
        validator_func: Callable,
        task_name: str = "Email Validation",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run email validation with progress tracking
        
        Args:
            emails: List of emails to validate
            validator_func: The validation function to call
            task_name: Name of the task
            **kwargs: Additional arguments for validator
        
        Returns:
            dict: Result with task_id for tracking
        """
        # Create progress task
        task_id = self.tracker.create_task(
            task_name=task_name,
            total_items=len(emails),
            metadata={
                'operation': 'validation',
                'email_count': len(emails),
                'options': kwargs
            }
        )
        
        # Start validation in background thread
        def run_validation():
            try:
                self.tracker.start_task(task_id)
                
                # Process emails in batches for progress updates
                batch_size = max(1, len(emails) // 10)  # 10% increments
                results = {
                    'success': True,
                    'stats': {
                        'total': len(emails),
                        'live': 0,
                        'die': 0,
                        'unknown': 0
                    },
                    'results': {
                        'live': [],
                        'die': [],
                        'unknown': []
                    }
                }
                
                for i in range(0, len(emails), batch_size):
                    batch = emails[i:i+batch_size]
                    
                    # Validate batch
                    batch_result = validator_func(batch, **kwargs)
                    
                    # Merge results
                    if batch_result.get('success'):
                        for status in ['live', 'die', 'unknown']:
                            results['results'][status].extend(
                                batch_result['results'].get(status, [])
                            )
                    
                    # Update progress
                    self.tracker.update_progress(
                        task_id=task_id,
                        current=min(i + batch_size, len(emails)),
                        message=f"Validated {min(i + batch_size, len(emails))}/{len(emails)} emails"
                    )
                
                # Calculate final stats
                results['stats'] = {
                    'total': len(emails),
                    'live': len(results['results']['live']),
                    'die': len(results['results']['die']),
                    'unknown': len(results['results']['unknown']),
                    'processing_time': time.time() - self.tracker.tasks[task_id]['started_at']
                }
                
                # Complete task
                self.tracker.complete_task(
                    task_id=task_id,
                    result=results,
                    message=f"Validated {len(emails)} emails - {results['stats']['live']} LIVE"
                )
                
            except Exception as e:
                self.tracker.fail_task(
                    task_id=task_id,
                    error=str(e)
                )
        
        # Start thread
        thread = threading.Thread(target=run_validation, daemon=True)
        thread.start()
        
        return {
            'success': True,
            'task_id': task_id,
            'message': 'Validation started in background',
            'track_url': f'/api/progress/{task_id}'
        }
    
    def extract_with_progress(
        self,
        text: str,
        extractor_func: Callable,
        task_name: str = "Email Extraction",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run email extraction with progress tracking
        
        Args:
            text: Text to extract emails from
            extractor_func: The extraction function to call
            task_name: Name of the task
            **kwargs: Additional arguments for extractor
        
        Returns:
            dict: Result with task_id for tracking
        """
        # Estimate total items based on text length
        estimated_items = max(100, len(text) // 100)
        
        # Create progress task
        task_id = self.tracker.create_task(
            task_name=task_name,
            total_items=estimated_items,
            metadata={
                'operation': 'extraction',
                'text_length': len(text),
                'options': kwargs
            }
        )
        
        # Start extraction in background thread
        def run_extraction():
            try:
                self.tracker.start_task(task_id)
                
                # Simulate progress updates during extraction
                for i in range(0, 100, 10):
                    self.tracker.update_progress(
                        task_id=task_id,
                        current=i,
                        message=f"Extracting emails... {i}%"
                    )
                    time.sleep(0.1)
                
                # Run actual extraction
                result = extractor_func(text, **kwargs)
                
                # Update actual total based on results
                if result.get('success'):
                    extracted_count = len(result.get('emails', []))
                    self.tracker.tasks[task_id]['total'] = 100
                    self.tracker.tasks[task_id]['current'] = 100
                    
                    self.tracker.complete_task(
                        task_id=task_id,
                        result=result,
                        message=f"Extracted {extracted_count} emails"
                    )
                else:
                    self.tracker.fail_task(
                        task_id=task_id,
                        error=result.get('message', 'Extraction failed')
                    )
                
            except Exception as e:
                self.tracker.fail_task(
                    task_id=task_id,
                    error=str(e)
                )
        
        # Start thread
        thread = threading.Thread(target=run_extraction, daemon=True)
        thread.start()
        
        return {
            'success': True,
            'task_id': task_id,
            'message': 'Extraction started in background',
            'track_url': f'/api/progress/{task_id}'
        }
    
    def batch_operation_with_progress(
        self,
        items: List[Any],
        operation_func: Callable,
        task_name: str,
        batch_size: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generic batch operation with progress tracking
        
        Args:
            items: Items to process
            operation_func: Function to call for each batch
            task_name: Name of the task
            batch_size: Size of each batch
            **kwargs: Additional arguments
        
        Returns:
            dict: Result with task_id
        """
        # Create progress task
        task_id = self.tracker.create_task(
            task_name=task_name,
            total_items=len(items),
            metadata={
                'operation': 'batch_processing',
                'item_count': len(items),
                'batch_size': batch_size,
                'options': kwargs
            }
        )
        
        # Start processing in background
        def run_batch():
            try:
                self.tracker.start_task(task_id)
                
                results = []
                
                for i in range(0, len(items), batch_size):
                    batch = items[i:i+batch_size]
                    
                    # Process batch
                    batch_result = operation_func(batch, **kwargs)
                    results.append(batch_result)
                    
                    # Update progress
                    self.tracker.update_progress(
                        task_id=task_id,
                        current=min(i + batch_size, len(items)),
                        message=f"Processed {min(i + batch_size, len(items))}/{len(items)} items"
                    )
                
                # Complete task
                self.tracker.complete_task(
                    task_id=task_id,
                    result={'results': results},
                    message=f"Processed {len(items)} items"
                )
                
            except Exception as e:
                self.tracker.fail_task(
                    task_id=task_id,
                    error=str(e)
                )
        
        # Start thread
        thread = threading.Thread(target=run_batch, daemon=True)
        thread.start()
        
        return {
            'success': True,
            'task_id': task_id,
            'message': f'Processing {len(items)} items in background',
            'track_url': f'/api/progress/{task_id}'
        }


# Global instance
_progress_integration = None

def get_progress_integration():
    """Get global progress integration instance"""
    global _progress_integration
    if _progress_integration is None:
        _progress_integration = ProgressIntegration()
    return _progress_integration
