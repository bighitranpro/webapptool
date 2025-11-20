"""
Email Batch Processor Module
Process large email lists in batches
"""

from typing import List, Dict, Callable
from datetime import datetime
import concurrent.futures
import time


class EmailBatchProcessor:
    """Process emails in batches for large datasets"""
    
    def __init__(self):
        self.batch_sizes = [10, 50, 100, 500, 1000, 5000]
        self.processing_stats = {
            'total_emails': 0,
            'batches_processed': 0,
            'successful': 0,
            'failed': 0,
            'processing_time': 0,
            'avg_batch_time': 0
        }
    
    def create_batches(self, emails: List[str], batch_size: int) -> List[List[str]]:
        """Split emails into batches"""
        batches = []
        for i in range(0, len(emails), batch_size):
            batches.append(emails[i:i + batch_size])
        return batches
    
    def process_batch(self, batch: List[str], 
                     processor_func: Callable,
                     **kwargs) -> Dict:
        """Process a single batch"""
        start_time = time.time()
        
        try:
            result = processor_func(batch, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        
        return {
            'success': success,
            'result': result,
            'error': error,
            'batch_size': len(batch),
            'processing_time': end_time - start_time
        }
    
    def process_sequential(self, emails: List[str], 
                          batch_size: int,
                          processor_func: Callable,
                          **kwargs) -> Dict:
        """Process batches sequentially"""
        batches = self.create_batches(emails, batch_size)
        
        results = []
        total_time = 0
        successful = 0
        failed = 0
        
        for i, batch in enumerate(batches):
            batch_result = self.process_batch(batch, processor_func, **kwargs)
            results.append(batch_result)
            
            total_time += batch_result['processing_time']
            if batch_result['success']:
                successful += 1
            else:
                failed += 1
        
        self.processing_stats = {
            'total_emails': len(emails),
            'batches_processed': len(batches),
            'successful': successful,
            'failed': failed,
            'processing_time': round(total_time, 2),
            'avg_batch_time': round(total_time / len(batches), 2) if batches else 0
        }
        
        return {
            'success': True,
            'batch_results': results,
            'stats': self.processing_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_parallel(self, emails: List[str],
                        batch_size: int,
                        processor_func: Callable,
                        max_workers: int = 5,
                        **kwargs) -> Dict:
        """Process batches in parallel"""
        batches = self.create_batches(emails, batch_size)
        
        start_time = time.time()
        results = []
        successful = 0
        failed = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {
                executor.submit(self.process_batch, batch, processor_func, **kwargs): i
                for i, batch in enumerate(batches)
            }
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_result = future.result()
                results.append(batch_result)
                
                if batch_result['success']:
                    successful += 1
                else:
                    failed += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.processing_stats = {
            'total_emails': len(emails),
            'batches_processed': len(batches),
            'successful': successful,
            'failed': failed,
            'processing_time': round(total_time, 2),
            'avg_batch_time': round(
                sum(r['processing_time'] for r in results) / len(results), 2
            ) if results else 0,
            'parallel_speedup': round(
                sum(r['processing_time'] for r in results) / total_time, 2
            ) if total_time > 0 else 0
        }
        
        return {
            'success': True,
            'batch_results': results,
            'stats': self.processing_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_with_progress(self, emails: List[str],
                            batch_size: int,
                            processor_func: Callable,
                            progress_callback: Callable = None,
                            **kwargs) -> Dict:
        """Process batches with progress tracking"""
        batches = self.create_batches(emails, batch_size)
        total_batches = len(batches)
        
        results = []
        successful = 0
        failed = 0
        total_time = 0
        
        for i, batch in enumerate(batches):
            batch_result = self.process_batch(batch, processor_func, **kwargs)
            results.append(batch_result)
            
            total_time += batch_result['processing_time']
            if batch_result['success']:
                successful += 1
            else:
                failed += 1
            
            # Call progress callback
            if progress_callback:
                progress = {
                    'current_batch': i + 1,
                    'total_batches': total_batches,
                    'progress_percentage': round((i + 1) / total_batches * 100, 2),
                    'successful': successful,
                    'failed': failed,
                    'elapsed_time': round(total_time, 2)
                }
                progress_callback(progress)
        
        self.processing_stats = {
            'total_emails': len(emails),
            'batches_processed': len(batches),
            'successful': successful,
            'failed': failed,
            'processing_time': round(total_time, 2),
            'avg_batch_time': round(total_time / len(batches), 2) if batches else 0
        }
        
        return {
            'success': True,
            'batch_results': results,
            'stats': self.processing_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def estimate_processing_time(self, total_emails: int,
                                batch_size: int,
                                avg_time_per_email: float = 0.1) -> Dict:
        """Estimate processing time for batch operation"""
        num_batches = (total_emails + batch_size - 1) // batch_size
        estimated_time = total_emails * avg_time_per_email
        
        return {
            'total_emails': total_emails,
            'batch_size': batch_size,
            'num_batches': num_batches,
            'estimated_time_seconds': round(estimated_time, 2),
            'estimated_time_minutes': round(estimated_time / 60, 2),
            'avg_time_per_email': avg_time_per_email
        }
    
    def process_with_retry(self, emails: List[str],
                          batch_size: int,
                          processor_func: Callable,
                          max_retries: int = 3,
                          **kwargs) -> Dict:
        """Process batches with retry logic for failures"""
        batches = self.create_batches(emails, batch_size)
        
        results = []
        successful = 0
        failed = 0
        total_time = 0
        
        for batch in batches:
            retry_count = 0
            batch_result = None
            
            while retry_count < max_retries:
                batch_result = self.process_batch(batch, processor_func, **kwargs)
                
                if batch_result['success']:
                    break
                
                retry_count += 1
                time.sleep(0.5 * retry_count)  # Exponential backoff
            
            results.append(batch_result)
            total_time += batch_result['processing_time']
            
            if batch_result['success']:
                successful += 1
            else:
                failed += 1
        
        self.processing_stats = {
            'total_emails': len(emails),
            'batches_processed': len(batches),
            'successful': successful,
            'failed': failed,
            'processing_time': round(total_time, 2),
            'avg_batch_time': round(total_time / len(batches), 2) if batches else 0,
            'max_retries': max_retries
        }
        
        return {
            'success': True,
            'batch_results': results,
            'stats': self.processing_stats,
            'timestamp': datetime.now().isoformat()
        }
