import tkinter as tk
from tkinter import filedialog
from audio_format_handler import AudioFormatHandler
from steganography_utils import validate_image_file, validate_pdf_file

def select_audio_file_dialog(title="Select Audio File"):
    """Select WAV or FLAC file"""
    filetypes = [
        ("WAV or FLAC", "*.wav;*.flac"),
        ("WAV files", "*.wav"),
        ("FLAC files", "*.flac"),
        ("All files", "*.*")
    ]
    
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    if not file_path:
        return None, None
    
    handler = AudioFormatHandler()
    format_info = handler.detect_format(file_path)
    
    if 'error' in format_info:
        return None, format_info
    
    return file_path, format_info
