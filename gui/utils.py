from steganography_utils import get_file_size_mb, estimate_audio_duration_needed

def show_format_info(format_info):
    """Display audio format information"""
    if not format_info or 'error' in format_info:
        return "Error: Invalid audio format information"
    
    return (
        f"Format: {format_info['format'].upper()}\n"
        f"Codec: {format_info.get('codec', 'Unknown')}\n"
        f"Sample Rate: {format_info.get('sample_rate', 0)} Hz\n"
        f"Channels: {format_info.get('channels', 0)}\n"
        f"Duration: {format_info.get('duration', 0):.1f} seconds\n"
        f"Method: LSB Steganography (High Quality)"
    )
