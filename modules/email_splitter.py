"""
Email Splitter Module
Split email lists into smaller chunks
"""

from typing import List, Dict
from datetime import datetime
import math


class EmailSplitter:
    """Split email lists into manageable chunks"""
    
    def __init__(self):
        self.split_methods = {
            'count': 'Theo số lượng',
            'chunks': 'Theo số phần',
            'domain': 'Theo domain',
            'alphabetical': 'Theo thứ tự A-Z'
        }
    
    def split_by_count(self, emails: List[str], count_per_chunk: int) -> List[List[str]]:
        """Split emails into chunks of specific size"""
        chunks = []
        for i in range(0, len(emails), count_per_chunk):
            chunks.append(emails[i:i + count_per_chunk])
        return chunks
    
    def split_by_chunks(self, emails: List[str], num_chunks: int) -> List[List[str]]:
        """Split emails into specific number of chunks"""
        chunk_size = math.ceil(len(emails) / num_chunks)
        return self.split_by_count(emails, chunk_size)
    
    def split_by_domain(self, emails: List[str]) -> Dict[str, List[str]]:
        """Split emails by domain"""
        domain_groups = {}
        
        for email in emails:
            try:
                local, domain = email.split('@')
                if domain not in domain_groups:
                    domain_groups[domain] = []
                domain_groups[domain].append(email)
            except:
                continue
        
        return domain_groups
    
    def split_alphabetically(self, emails: List[str], 
                           letters_per_group: int = 3) -> Dict[str, List[str]]:
        """Split emails alphabetically"""
        groups = {}
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        
        # Create letter groups
        for i in range(0, len(alphabet), letters_per_group):
            group_letters = alphabet[i:i + letters_per_group]
            group_key = f"{group_letters[0].upper()}-{group_letters[-1].upper()}"
            groups[group_key] = []
        
        groups['Other'] = []
        
        # Distribute emails
        for email in emails:
            first_char = email[0].lower()
            placed = False
            
            for i in range(0, len(alphabet), letters_per_group):
                group_letters = alphabet[i:i + letters_per_group]
                if first_char in group_letters:
                    group_key = f"{group_letters[0].upper()}-{group_letters[-1].upper()}"
                    groups[group_key].append(email)
                    placed = True
                    break
            
            if not placed:
                groups['Other'].append(email)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def split_evenly_weighted(self, emails: List[str], 
                             num_chunks: int,
                             weight_by_length: bool = False) -> List[List[str]]:
        """Split emails evenly, optionally considering length"""
        if not weight_by_length:
            return self.split_by_chunks(emails, num_chunks)
        
        # Sort by length
        sorted_emails = sorted(emails, key=len, reverse=True)
        
        # Initialize chunks
        chunks = [[] for _ in range(num_chunks)]
        chunk_lengths = [0] * num_chunks
        
        # Distribute emails to balance total length
        for email in sorted_emails:
            # Find chunk with smallest total length
            min_idx = chunk_lengths.index(min(chunk_lengths))
            chunks[min_idx].append(email)
            chunk_lengths[min_idx] += len(email)
        
        return chunks
    
    def split_emails(self, emails: List[str], method: str, 
                    count: int = None, chunks: int = None) -> Dict:
        """
        Split emails using specified method
        
        Args:
            emails: List of emails to split
            method: Split method (count, chunks, domain, alphabetical)
            count: Emails per chunk (for count method)
            chunks: Number of chunks (for chunks method)
        
        Returns:
            Dict with split results and statistics
        """
        result = {
            'success': True,
            'method': method,
            'total_emails': len(emails),
            'timestamp': datetime.now().isoformat()
        }
        
        if method == 'count':
            if not count or count <= 0:
                count = 10
            split_result = self.split_by_count(emails, count)
            result['chunks'] = split_result
            result['num_chunks'] = len(split_result)
            result['emails_per_chunk'] = count
            
        elif method == 'chunks':
            if not chunks or chunks <= 0:
                chunks = 5
            split_result = self.split_by_chunks(emails, chunks)
            result['chunks'] = split_result
            result['num_chunks'] = len(split_result)
            result['avg_per_chunk'] = math.ceil(len(emails) / chunks)
            
        elif method == 'domain':
            split_result = self.split_by_domain(emails)
            result['domain_groups'] = split_result
            result['num_domains'] = len(split_result)
            result['domains'] = list(split_result.keys())
            
        elif method == 'alphabetical':
            split_result = self.split_alphabetically(emails)
            result['letter_groups'] = split_result
            result['num_groups'] = len(split_result)
            result['groups'] = list(split_result.keys())
        
        return result
    
    def export_chunks(self, chunks: List[List[str]], 
                     format_type: str = 'text') -> List[str]:
        """Export chunks in various formats"""
        exports = []
        
        for i, chunk in enumerate(chunks):
            if format_type == 'text':
                exports.append('\n'.join(chunk))
            elif format_type == 'numbered':
                numbered = [f"{j+1}. {email}" for j, email in enumerate(chunk)]
                exports.append('\n'.join(numbered))
            elif format_type == 'csv':
                exports.append(','.join(chunk))
        
        return exports
