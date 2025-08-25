import tkinter as tk
import os
from audio_player import AudioPreviewWidget

def preview_encoded_audio(audio_path, audio_format):
    """Show a dedicated audio preview window for encoded files"""
    
    preview_window = tk.Toplevel()
    preview_window.title("Encoded Audio Preview")
    preview_window.geometry("500x300")
    preview_window.grab_set()
    
    tk.Label(preview_window, text="🎵 Encoded Audio Preview", 
             font=("Arial", 16, "bold"), fg="#1976D2").pack(pady=15)
    
    tk.Label(preview_window, text=f"📁 File: {os.path.basename(audio_path)}", 
             font=("Arial", 11)).pack(pady=5)
    
    tk.Label(preview_window, text=f"🎶 Format: {audio_format.upper()}", 
             font=("Arial", 11)).pack(pady=5)
    
    # Quality notice
    quality_frame = tk.Frame(preview_window, bg="#e8f5e8", relief="groove", bd=1)
    quality_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(quality_frame, text="✅ Quality Check:", 
             bg="#e8f5e8", font=("Arial", 10, "bold"), fg="#2E7D32").pack(anchor="w", padx=5, pady=2)
    tk.Label(quality_frame, text="The encoded audio should sound identical to the original.", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15)
    tk.Label(quality_frame, text="LSB steganography preserves perfect audio quality.", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0,5))
    
    # Audio preview widget
    audio_preview = AudioPreviewWidget(preview_window)
    
    # Load audio file
    if audio_preview.load_audio_file(audio_path):
        tk.Label(preview_window, text="🔊 Use the controls above to play the encoded audio", 
                 font=("Arial", 9), fg="gray").pack(pady=5)
    else:
        tk.Label(preview_window, text="❌ Failed to load audio file for preview", 
                 font=("Arial", 10), fg="red").pack(pady=10)
    
    def close_preview():
        """Close preview window and cleanup"""
        try:
            audio_preview.cleanup()
        except:
            pass
        preview_window.destroy()
    
    # Buttons
    button_frame = tk.Frame(preview_window)
    button_frame.pack(pady=15)
    
    tk.Button(button_frame, text="✅ Sounds Good", command=close_preview,
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    tk.Button(button_frame, text="📁 Open Output Folder", 
              command=lambda: os.startfile(os.path.dirname(audio_path)),
              bg="#2196F3", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
    
    # Override window close to cleanup
    preview_window.protocol("WM_DELETE_WINDOW", close_preview)
