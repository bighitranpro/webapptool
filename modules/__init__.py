"""
Email Tool Modules
Modular architecture for email processing
"""

__version__ = "3.0.0"
__author__ = "AI Assistant"

# Import all modules
from .email_validator import EmailValidator
from .email_validator_pro import EmailValidatorPro  # NEW: Professional validator
from .email_generator import EmailGenerator
from .email_extractor import EmailExtractor
from .email_formatter import EmailFormatter
from .email_filter import EmailFilter
from .email_splitter import EmailSplitter
from .email_combiner import EmailCombiner
from .email_analyzer import EmailAnalyzer
from .email_deduplicator import EmailDeduplicator
from .email_batch_processor import EmailBatchProcessor
from .fb_linked_checker import FBLinkedChecker
from .email_pass_2fa_checker import EmailPass2FAChecker
from .page_mining import PageMining

__all__ = [
    'EmailValidator',
    'EmailValidatorPro',  # NEW
    'EmailGenerator',
    'EmailExtractor',
    'EmailFormatter',
    'EmailFilter',
    'EmailSplitter',
    'EmailCombiner',
    'EmailAnalyzer',
    'EmailDeduplicator',
    'EmailBatchProcessor',
    'FBLinkedChecker',
    'EmailPass2FAChecker',
    'PageMining'
]
