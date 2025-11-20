"""
Email Combiner Module
Combine multiple email lists with various options
"""

from typing import List, Dict
from datetime import datetime


class EmailCombiner:
    """Combine and merge email lists"""
    
    def __init__(self):
        self.combine_methods = {
            'simple': 'Gộp đơn giản',
            'unique': 'Gộp và loại trùng',
            'intersect': 'Giao nhau',
            'difference': 'Khác biệt'
        }
    
    def simple_combine(self, *email_lists: List[str]) -> List[str]:
        """Simply combine all lists"""
        result = []
        for email_list in email_lists:
            result.extend(email_list)
        return result
    
    def unique_combine(self, *email_lists: List[str], 
                      case_sensitive: bool = False) -> List[str]:
        """Combine lists and remove duplicates"""
        all_emails = self.simple_combine(*email_lists)
        
        if case_sensitive:
            return list(set(all_emails))
        else:
            seen = set()
            result = []
            for email in all_emails:
                email_lower = email.lower()
                if email_lower not in seen:
                    seen.add(email_lower)
                    result.append(email)
            return result
    
    def intersect(self, *email_lists: List[str],
                  case_sensitive: bool = False) -> List[str]:
        """Find emails common to all lists"""
        if not email_lists:
            return []
        
        if case_sensitive:
            sets = [set(lst) for lst in email_lists]
        else:
            sets = [set(e.lower() for e in lst) for lst in email_lists]
        
        intersection = sets[0]
        for s in sets[1:]:
            intersection = intersection.intersection(s)
        
        # Return original case from first list
        if case_sensitive:
            return list(intersection)
        else:
            result = []
            first_list_lower = {e.lower(): e for e in email_lists[0]}
            for email_lower in intersection:
                result.append(first_list_lower[email_lower])
            return result
    
    def difference(self, list1: List[str], list2: List[str],
                   case_sensitive: bool = False) -> List[str]:
        """Find emails in list1 but not in list2"""
        if case_sensitive:
            set2 = set(list2)
            return [e for e in list1 if e not in set2]
        else:
            set2 = set(e.lower() for e in list2)
            return [e for e in list1 if e.lower() not in set2]
    
    def symmetric_difference(self, list1: List[str], list2: List[str],
                           case_sensitive: bool = False) -> List[str]:
        """Find emails in either list but not both"""
        if case_sensitive:
            set1 = set(list1)
            set2 = set(list2)
            return list(set1.symmetric_difference(set2))
        else:
            # Get all unique emails
            all_emails = {}
            for email in list1 + list2:
                email_lower = email.lower()
                if email_lower not in all_emails:
                    all_emails[email_lower] = email
            
            # Find those in only one list
            set1_lower = set(e.lower() for e in list1)
            set2_lower = set(e.lower() for e in list2)
            symmetric = set1_lower.symmetric_difference(set2_lower)
            
            return [all_emails[e] for e in symmetric]
    
    def combine_with_priority(self, *email_lists: List[str],
                             priorities: List[int] = None) -> List[str]:
        """Combine lists with priority (keep first occurrence)"""
        if not priorities:
            priorities = list(range(len(email_lists)))
        
        # Sort lists by priority
        sorted_lists = [lst for _, lst in sorted(zip(priorities, email_lists))]
        
        # Combine keeping first occurrence
        seen = set()
        result = []
        
        for email_list in sorted_lists:
            for email in email_list:
                email_lower = email.lower()
                if email_lower not in seen:
                    seen.add(email_lower)
                    result.append(email)
        
        return result
    
    def combine_emails(self, email_lists: List[List[str]], 
                      method: str = 'unique',
                      case_sensitive: bool = False) -> Dict:
        """
        Combine email lists using specified method
        
        Args:
            email_lists: List of email lists to combine
            method: Combine method (simple, unique, intersect, difference)
            case_sensitive: Whether to consider case in comparisons
        
        Returns:
            Dict with combined results and statistics
        """
        if not email_lists:
            return {
                'success': False,
                'error': 'No email lists provided',
                'timestamp': datetime.now().isoformat()
            }
        
        result = {
            'success': True,
            'method': method,
            'input_lists': len(email_lists),
            'input_counts': [len(lst) for lst in email_lists],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if method == 'simple':
                combined = self.simple_combine(*email_lists)
            elif method == 'unique':
                combined = self.unique_combine(*email_lists, 
                                              case_sensitive=case_sensitive)
            elif method == 'intersect':
                combined = self.intersect(*email_lists, 
                                        case_sensitive=case_sensitive)
            elif method == 'difference':
                if len(email_lists) < 2:
                    raise ValueError("Difference requires at least 2 lists")
                combined = self.difference(email_lists[0], email_lists[1],
                                         case_sensitive=case_sensitive)
            else:
                combined = self.unique_combine(*email_lists,
                                              case_sensitive=case_sensitive)
            
            result['emails'] = combined
            result['total_output'] = len(combined)
            result['total_input'] = sum(len(lst) for lst in email_lists)
            
            if method == 'unique':
                result['duplicates_removed'] = (
                    result['total_input'] - result['total_output']
                )
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def get_list_statistics(self, email_lists: List[List[str]]) -> Dict:
        """Get statistics about multiple email lists"""
        stats = {
            'num_lists': len(email_lists),
            'list_sizes': [len(lst) for lst in email_lists],
            'total_emails': sum(len(lst) for lst in email_lists),
            'unique_emails': len(self.unique_combine(*email_lists)),
            'timestamp': datetime.now().isoformat()
        }
        
        # Find overlap statistics
        if len(email_lists) >= 2:
            stats['common_to_all'] = len(self.intersect(*email_lists))
            stats['unique_to_each'] = [
                len(self.difference(email_lists[i], 
                    self.simple_combine(*[email_lists[j] 
                                        for j in range(len(email_lists)) 
                                        if j != i])))
                for i in range(len(email_lists))
            ]
        
        return stats
