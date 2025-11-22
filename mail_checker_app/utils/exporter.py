"""
Exporter - Xuất kết quả ra file CSV
"""
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict


class ResultExporter:
    """Export kết quả check email ra CSV"""
    
    def __init__(self, output_dir='results'):
        self.output_dir = output_dir
        
        # Tạo thư mục nếu chưa có
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def export_to_csv(self, results: List[Dict], filename: str = None) -> str:
        """
        Export results to CSV file
        
        Args:
            results: List of result dictionaries with keys:
                     email, smtp_status, has_facebook, country, score
            filename: Custom filename (optional)
        
        Returns:
            str: Path to saved file
        """
        if not results:
            raise ValueError("No results to export")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'email_check_results_{timestamp}.csv'
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Reorder columns if they exist
        column_order = ['email', 'smtp_status', 'has_facebook', 'country', 'score']
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in column_order]
        
        df = df[existing_columns + other_columns]
        
        # Save to CSV
        df.to_csv(filepath, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
        
        return filepath
    
    def export_detailed_csv(self, results: List[Dict], filename: str = None) -> str:
        """
        Export với thông tin chi tiết hơn
        
        Expected result format:
        {
            'email': str,
            'smtp_status': str,
            'smtp_error': str,
            'has_facebook': bool,
            'fb_confidence': float,
            'country': str,
            'country_confidence': float,
            'score': float,
            'mx_records': list
        }
        """
        if not results:
            raise ValueError("No results to export")
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'detailed_results_{timestamp}.csv'
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data
        export_data = []
        for r in results:
            row = {
                'Email': r.get('email', ''),
                'SMTP Status': r.get('smtp_status', 'UNKNOWN'),
                'SMTP Error': r.get('smtp_error', ''),
                'Has Facebook': 'Yes' if r.get('has_facebook', False) else 'No',
                'FB Confidence': f"{r.get('fb_confidence', 0.0):.2f}",
                'Country': r.get('country', 'Unknown'),
                'Country Confidence': f"{r.get('country_confidence', 0.0):.2f}",
                'Overall Score': f"{r.get('score', 0.0):.2f}",
                'MX Records': ', '.join(r.get('mx_records', [])[:3]) if r.get('mx_records') else ''
            }
            export_data.append(row)
        
        df = pd.DataFrame(export_data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    def get_export_stats(self, results: List[Dict]) -> Dict:
        """
        Tạo thống kê từ kết quả
        
        Returns:
            dict with statistics
        """
        if not results:
            return {}
        
        total = len(results)
        
        smtp_live = sum(1 for r in results if r.get('smtp_status') == 'LIVE')
        smtp_die = sum(1 for r in results if r.get('smtp_status') == 'DIE')
        smtp_unknown = total - smtp_live - smtp_die
        
        has_fb = sum(1 for r in results if r.get('has_facebook', False))
        
        countries = {}
        for r in results:
            country = r.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        avg_score = sum(r.get('score', 0.0) for r in results) / total if total > 0 else 0
        
        return {
            'total': total,
            'smtp_live': smtp_live,
            'smtp_die': smtp_die,
            'smtp_unknown': smtp_unknown,
            'has_facebook': has_fb,
            'no_facebook': total - has_fb,
            'countries': countries,
            'average_score': round(avg_score, 2)
        }
    
    def list_exports(self) -> List[str]:
        """List all exported CSV files"""
        if not os.path.exists(self.output_dir):
            return []
        
        files = [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
        files.sort(reverse=True)  # Newest first
        return files
    
    def delete_export(self, filename: str) -> bool:
        """Delete an exported file"""
        filepath = os.path.join(self.output_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


def export_results(results: List[Dict], filename: str = None, output_dir: str = 'results') -> str:
    """
    Helper function to quickly export results
    
    Returns:
        str: Path to exported file
    """
    exporter = ResultExporter(output_dir=output_dir)
    return exporter.export_to_csv(results, filename)


def export_detailed_results(results: List[Dict], filename: str = None, output_dir: str = 'results') -> str:
    """
    Helper function to export detailed results
    """
    exporter = ResultExporter(output_dir=output_dir)
    return exporter.export_detailed_csv(results, filename)


if __name__ == '__main__':
    # Test
    print("=== Testing Result Exporter ===\n")
    
    # Sample results
    test_results = [
        {
            'email': 'nguyenvananh@gmail.com',
            'smtp_status': 'LIVE',
            'smtp_error': '',
            'has_facebook': True,
            'fb_confidence': 0.85,
            'country': 'Vietnam',
            'country_confidence': 0.95,
            'score': 0.90,
            'mx_records': ['gmail-smtp-in.l.google.com', 'alt1.gmail-smtp-in.l.google.com']
        },
        {
            'email': 'test123@yahoo.com',
            'smtp_status': 'DIE',
            'smtp_error': 'Mailbox not found',
            'has_facebook': False,
            'fb_confidence': 0.10,
            'country': 'Unknown',
            'country_confidence': 0.30,
            'score': 0.15,
            'mx_records': []
        },
        {
            'email': 'john.smith@gmail.com',
            'smtp_status': 'LIVE',
            'smtp_error': '',
            'has_facebook': True,
            'fb_confidence': 0.75,
            'country': 'USA',
            'country_confidence': 0.80,
            'score': 0.82,
            'mx_records': ['gmail-smtp-in.l.google.com']
        }
    ]
    
    exporter = ResultExporter(output_dir='../results')
    
    # Test basic export
    print("Testing basic CSV export...")
    filepath = exporter.export_to_csv(test_results)
    print(f"Exported to: {filepath}")
    
    # Test detailed export
    print("\nTesting detailed CSV export...")
    detailed_path = exporter.export_detailed_csv(test_results)
    print(f"Exported detailed to: {detailed_path}")
    
    # Test stats
    print("\nExport Statistics:")
    stats = exporter.get_export_stats(test_results)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # List exports
    print("\nExported files:")
    files = exporter.list_exports()
    for f in files:
        print(f"  - {f}")
