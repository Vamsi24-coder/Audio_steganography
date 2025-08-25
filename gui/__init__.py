"""
GUI Package for Audio Steganography Application
"""

# Main entry points for backward compatibility
from .dialogs import login_dialog, signup_dialog, forgot_password_dialog
from .main_window import main_app
from .project_info import open_project_info
from .encode_gui import encode_smtp_dialog
from .decode_gui import decode_dialog
from .history_gui import history_dialog

__all__ = [
    'login_dialog',
    'signup_dialog', 
    'forgot_password_dialog',
    'main_app',
    'open_project_info',
    'encode_smtp_dialog',
    'decode_dialog', 
    'history_dialog'
]
