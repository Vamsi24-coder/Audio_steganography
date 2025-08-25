import pygame
import threading
import tkinter as tk
from tkinter import messagebox
import os
import time

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        self.is_paused = False
        self.current_file = None
        self.position = 0
        self.duration = 0
        
    def load_audio(self, file_path):
        """Load audio file for playback"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError("Audio file not found")
            
            self.current_file = file_path
            pygame.mixer.music.load(file_path)
            
            # Get duration using soundfile
            import soundfile as sf
            info = sf.info(file_path)
            self.duration = info.duration
            
            return True, f"Loaded: {os.path.basename(file_path)} ({self.duration:.1f}s)"
        except Exception as e:
            return False, f"Failed to load audio: {str(e)}"
    
    def play(self):
        """Start or resume playback"""
        try:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.play(start=self.position)
            
            self.is_playing = True
            return True
        except Exception as e:
            return False
    
    def pause(self):
        """Pause playback"""
        try:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False
            return True
        except Exception as e:
            return False
    
    def stop(self):
        """Stop playback"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.position = 0
            return True
        except Exception as e:
            return False
    
    def set_volume(self, volume):
        """Set playback volume (0.0 to 1.0)"""
        try:
            pygame.mixer.music.set_volume(volume)
            return True
        except Exception as e:
            return False
    
    def get_status(self):
        """Get current playback status"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'duration': self.duration,
            'current_file': self.current_file
        }

class AudioPreviewWidget:
    def __init__(self, parent):
        self.parent = parent
        self.player = AudioPlayer()
        self.update_thread = None
        self.should_update = False
        
        # Create preview frame
        self.preview_frame = tk.Frame(parent, relief="groove", bd=2, bg="#f0f0f0")
        self.preview_frame.pack(fill="x", padx=5, pady=5)
        
        # Audio info label
        self.info_label = tk.Label(self.preview_frame, text="No audio loaded", 
                                  bg="#f0f0f0", font=("Arial", 9))
        self.info_label.pack(pady=2)
        
        # Controls frame
        controls_frame = tk.Frame(self.preview_frame, bg="#f0f0f0")
        controls_frame.pack(pady=5)
        
        # Play/Pause button
        self.play_button = tk.Button(controls_frame, text="▶️ Play", 
                                    command=self.toggle_play, width=8,
                                    bg="#4CAF50", fg="white")
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        # Stop button
        self.stop_button = tk.Button(controls_frame, text="⏹️ Stop", 
                                    command=self.stop_audio, width=8,
                                    bg="#f44336", fg="white")
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # Volume control
        tk.Label(controls_frame, text="Vol:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(10,2))
        self.volume_scale = tk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    length=80, command=self.set_volume, bg="#f0f0f0")
        self.volume_scale.set(70)  # Default volume
        self.volume_scale.pack(side=tk.LEFT, padx=2)
        
        # Progress bar (simplified - shows duration)
        self.progress_label = tk.Label(self.preview_frame, text="00:00 / 00:00", 
                                      bg="#f0f0f0", font=("Arial", 8))
        self.progress_label.pack(pady=2)
        
        # Initially disable controls
        self.set_controls_state(False)
    
    def load_audio_file(self, file_path):
        """Load and prepare audio file for preview"""
        success, message = self.player.load_audio(file_path)
        
        if success:
            self.info_label.config(text=message, fg="green")
            self.set_controls_state(True)
            self.update_progress_display()
            return True
        else:
            self.info_label.config(text=message, fg="red")
            self.set_controls_state(False)
            return False
    
    def toggle_play(self):
        """Toggle between play and pause"""
        if self.player.is_playing:
            if self.player.pause():
                self.play_button.config(text="▶️ Play")
        else:
            if self.player.play():
                self.play_button.config(text="⏸️ Pause")
                self.start_update_thread()
    
    def stop_audio(self):
        """Stop audio playback"""
        if self.player.stop():
            self.play_button.config(text="▶️ Play")
            self.stop_update_thread()
            self.update_progress_display()
    
    def set_volume(self, volume):
        """Set playback volume"""
        volume_float = float(volume) / 100.0
        self.player.set_volume(volume_float)
    
    def set_controls_state(self, enabled):
        """Enable or disable playback controls"""
        state = "normal" if enabled else "disabled"
        self.play_button.config(state=state)
        self.stop_button.config(state=state)
        self.volume_scale.config(state=state)
    
    def update_progress_display(self):
        """Update the progress display"""
        status = self.player.get_status()
        duration = status['duration']
        
        duration_str = self.format_time(duration)
        self.progress_label.config(text=f"00:00 / {duration_str}")
    
    def format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def start_update_thread(self):
        """Start the progress update thread"""
        self.should_update = True
        if self.update_thread is None or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def stop_update_thread(self):
        """Stop the progress update thread"""
        self.should_update = False
    
    def update_loop(self):
        """Progress update loop (runs in separate thread)"""
        start_time = time.time()
        while self.should_update and self.player.is_playing:
            elapsed = time.time() - start_time
            status = self.player.get_status()
            
            if elapsed < status['duration']:
                elapsed_str = self.format_time(elapsed)
                duration_str = self.format_time(status['duration'])
                
                # Update GUI in main thread
                self.parent.after(0, lambda: self.progress_label.config(
                    text=f"{elapsed_str} / {duration_str}"))
            
            time.sleep(0.1)
        
        # Reset display when done
        self.parent.after(0, lambda: self.play_button.config(text="▶️ Play"))
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_update_thread()
        self.player.stop()
