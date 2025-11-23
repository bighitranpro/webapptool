"""
Email Tool Modules
Modular architecture for email processing
"""

__version__ = "3.1.0"
__author__ = "AI Assistant"

# Import all modules
from .email_validator import EmailValidator
from .email_validator_pro import EmailValidatorPro  # Professional validator
from .email_generator import EmailGenerator
from .email_generator_advanced import EmailGeneratorAdvanced  # Advanced generator with Vietnamese support
from .realistic_email_generator import RealisticEmailGenerator  # Realistic email patterns
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
from .email_checker_integrated import EmailCheckerIntegrated  # Integrated Email Checker
from .email_template_system import EmailTemplateSystem  # NEW: Template system
from .realtime_progress_tracker import RealtimeProgressTracker, get_global_tracker  # NEW: Progress tracking
from .progress_integration import ProgressIntegration, get_progress_integration  # NEW: Progress integration
from .smtp_validator import SMTPValidator, get_smtp_validator  # NEW: SMTP validation

__all__ = [
    'EmailValidator',
    'EmailValidatorPro',
    'EmailGenerator',
    'EmailGeneratorAdvanced',  # NEW
    'RealisticEmailGenerator',
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
    'PageMining',
    'EmailCheckerIntegrated',
    'EmailTemplateSystem',  # NEW
    'RealtimeProgressTracker',  # NEW
    'get_global_tracker',  # NEW
    'ProgressIntegration',  # NEW
    'get_progress_integration',  # NEW
    'SMTPValidator',  # NEW
    'get_smtp_validator'  # NEW
]
