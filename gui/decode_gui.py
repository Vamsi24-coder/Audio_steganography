# decode_gui.py
import tkinter as tk
from tkinter import messagebox
import os
from cryptography.fernet import Fernet
from steganography_utils import decode_data, get_folder_security_summary
from gui.file_operations import select_audio_file_dialog
from gui.utils import show_format_info
from audio_player import AudioPreviewWidget
from database import DatabaseManager
from secure_folder_dialogs import secure_folder_selection_dialog, set_theme_mode

# Simple theme variables
DARK_MODE = False

def get_bg_color():
    return "#242424" if DARK_MODE else "#f0f0f0"

def get_fg_color():
    return "#ffffff" if DARK_MODE else "#000000"

def get_button_bg():
    return "#333333" if DARK_MODE else "#4CAF50"

def get_button_fg():
    return "#ffffff"

def get_highlight_color():
    return "#00B8F4" if DARK_MODE else "#2196F3"

def switch_theme(mode, window):
    """Simple theme switching that only affects colors when needed"""
    global DARK_MODE
    DARK_MODE = (mode == "dark")
    set_theme_mode(DARK_MODE)  # Sync with secure_folder_dialogs
    apply_theme_to_window(window)

def apply_theme_to_window(window):
    """Apply theme to window - simple and reliable"""
    bg = get_bg_color()
    fg = get_fg_color()
    button_bg = get_button_bg()
    button_fg = get_button_fg()
    highlight = get_highlight_color()
    
    def update_widget(widget):
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == 'Toplevel':
                widget.configure(bg=bg)
            elif widget_class == 'Frame':
                widget.configure(bg=bg)
            elif widget_class == 'Label':
                current_fg = str(widget.cget('fg'))
                if current_fg in ['#000000', '#ffffff', 'black', 'white', 'SystemWindowText']:
                    widget.configure(bg=bg, fg=fg)
                elif current_fg == 'gray':
                    widget.configure(bg=bg)
                else:
                    widget.configure(bg=bg)
            elif widget_class == 'Button':
                current_bg = str(widget.cget('bg'))
                if current_bg in ['#4CAF50', '#333333', get_bg_color()]:
                    widget.configure(bg=button_bg, fg=button_fg)
            elif widget_class == 'Entry':
                if DARK_MODE:
                    widget.configure(bg=bg, fg=fg, insertbackground=fg)
                else:
                    widget.configure(bg="white", fg="black", insertbackground="black")
            elif widget_class == 'Radiobutton':
                widget.configure(bg=bg, fg=fg, selectcolor=bg, activebackground=bg, activeforeground=fg)
            
            for child in widget.winfo_children():
                update_widget(child)
                
        except Exception:
            pass
    
    update_widget(window)

def show_security_preview(parent, folder_id, user_id):
    """Show a preview of folder security status"""
    security_info = get_folder_security_summary(folder_id, user_id)
    
    preview_window = tk.Toplevel(parent)
    preview_window.title("🛡️ Security Preview")
    preview_window.geometry("400x200")
    preview_window.grab_set()
    preview_window.configure(bg=get_bg_color())
    
    # Center the window
    preview_window.transient(parent)
    preview_window.update_idletasks()
    width = preview_window.winfo_width()
    height = preview_window.winfo_height()
    x = (preview_window.winfo_screenwidth() // 2) - (width // 2)
    y = (preview_window.winfo_screenheight() // 2) - (height // 2)
    preview_window.geometry(f"{width}x{height}+{x}+{y}")
    
    tk.Label(preview_window, text=f"{security_info['icon']} {security_info['folder_name']}", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
    
    tk.Label(preview_window, text=f"Security Level: {security_info['security_level']}", 
             font=("Arial", 11, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
    tk.Label(preview_window, text=security_info['encryption_status'], 
             font=("Arial", 10), bg=get_bg_color(), fg="green").pack(pady=5)
    
    tk.Label(preview_window, text=security_info['description'], 
             font=("Arial", 9), bg=get_bg_color(), fg="gray", wraplength=350).pack(pady=10)
    
    tk.Button(preview_window, text="✅ OK", command=preview_window.destroy,
              bg="#4CAF50", fg="white", font=("Arial", 10)).pack(pady=10)

def decode_dialog(user_id):
    """Decode dialog with enhanced 7-Zip secure folder integration and audio preview functionality"""
    
    # Set theme mode for secure folder dialogs
    set_theme_mode(DARK_MODE)
    
    decode_window = tk.Toplevel()
    decode_window.title("🔍 Decode Audio File")
    decode_window.geometry("1000x750")  # Slightly larger for enhanced features
    decode_window.grab_set()
    decode_window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(decode_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", decode_window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", decode_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    decode_window.config(menu=menubar)
    
    tk.Label(decode_window, text="🔍 Decode Audio File", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
    
    # Check 7-Zip availability and show status
    db = DatabaseManager()
    zip_available, zip_msg = db.check_7zip_available()
    
    if zip_available:
        security_status = "🛡️ 7-Zip AES-256 encryption available for secure folders"
        security_color = "green"
    else:
        security_status = f"🔓 7-Zip encryption unavailable: {zip_msg}"
        security_color = "orange"
    
    tk.Label(decode_window, text=security_status, 
             font=("Arial", 9), fg=security_color, bg=get_bg_color()).pack(pady=5)
    
    # Data type selection
    tk.Label(decode_window, text="What type of data is hidden?", 
             font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color()).pack(pady=10)
    data_type_var = tk.StringVar(value="message")
    
    type_frame = tk.Frame(decode_window, bg=get_bg_color())
    type_frame.pack(pady=5)
    
    tk.Radiobutton(type_frame, text="📝 Text Message", variable=data_type_var, 
                   value="message", font=("Arial", 10), bg=get_bg_color(), fg=get_fg_color(),
                   selectcolor=get_bg_color(), activebackground=get_bg_color(),
                   activeforeground=get_fg_color()).pack(side=tk.LEFT, padx=15)
    tk.Radiobutton(type_frame, text="🖼️ JPG Image", variable=data_type_var, 
                   value="image", font=("Arial", 10), bg=get_bg_color(), fg=get_fg_color(),
                   selectcolor=get_bg_color(), activebackground=get_bg_color(),
                   activeforeground=get_fg_color()).pack(side=tk.LEFT, padx=15)
    tk.Radiobutton(type_frame, text="📄 PDF Document", variable=data_type_var, 
                   value="pdf", font=("Arial", 10), bg=get_bg_color(), fg=get_fg_color(),
                   selectcolor=get_bg_color(), activebackground=get_bg_color(),
                   activeforeground=get_fg_color()).pack(side=tk.LEFT, padx=15)
    
    # Key input
    tk.Label(decode_window, text="Decryption Key:", font=("Arial", 12), 
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=(20,5))
    key_entry = tk.Entry(decode_window, width=70, 
                        bg="white" if not DARK_MODE else get_bg_color(), 
                        fg="black" if not DARK_MODE else get_fg_color(),
                        insertbackground="black" if not DARK_MODE else get_fg_color())
    key_entry.pack(pady=5)
    
    # Audio file selection
    audio_path_var = tk.StringVar()
    format_info = {}
    
    tk.Label(decode_window, text="Select Encoded Audio File (WAV or FLAC):", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(20,5))
    
    file_frame = tk.Frame(decode_window, bg=get_bg_color())
    file_frame.pack(pady=5)
    
    tk.Entry(file_frame, textvariable=audio_path_var, width=50, 
             state='readonly', bg="white" if not DARK_MODE else get_bg_color(), 
             fg="black" if not DARK_MODE else get_fg_color()).pack(side=tk.LEFT, padx=5)
    
    file_info_label = tk.Label(decode_window, text="No audio file selected", fg="gray", bg=get_bg_color())
    file_info_label.pack(pady=5)
    
    # Status label for audio loading feedback
    status_label = tk.Label(decode_window, text="", font=("Arial", 9), bg=get_bg_color())
    status_label.pack(pady=2)
    
    # Audio preview widget
    tk.Label(decode_window, text="🎵 Audio Preview:", 
             font=("Arial", 11, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))
    
    audio_preview = AudioPreviewWidget(decode_window)
    
    def browse_file():
        path, info = select_audio_file_dialog("Select Encoded Audio File")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            file_info_label.config(text=show_format_info(info), fg="green")
            
            # Load audio for preview
            if audio_preview.load_audio_file(path):
                status_label.config(text="✅ Audio file loaded successfully! Use controls below to preview.", 
                                  fg="green")
            else:
                status_label.config(text="⚠️ Audio loaded but preview may not work properly.", 
                                  fg="orange")
            
        elif info and 'error' in info:
            status_label.config(text=f"❌ Audio Error: {info['error']}", fg="red")
            audio_path_var.set("")
            file_info_label.config(text="No audio file selected", fg="gray")
    
    tk.Button(file_frame, text="Browse & Load Audio", command=browse_file,
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
    
    # Selected folder preview
    selected_folder_info = tk.Label(decode_window, text="", font=("Arial", 9), bg=get_bg_color())
    selected_folder_info.pack(pady=5)
    
    def perform_decode():
        # Stop any playing audio before decoding
        try:
            audio_preview.stop_audio()
        except:
            pass
        
        key_str = key_entry.get().strip()
        audio_path = audio_path_var.get()
        data_type = data_type_var.get()
        
        if not key_str:
            status_label.config(text="❌ Please enter the decryption key", fg="red")
            return
        if not audio_path:
            status_label.config(text="❌ Please select an audio file", fg="red")
            return
        
        # Clear any previous status messages
        status_label.config(text="", fg=get_fg_color())
        selected_folder_info.config(text="")
        
        try:
            # Validate key format
            key_bytes = key_str.encode()
            Fernet(key_bytes)  # This will raise an exception if key is invalid
            
            # Only show folder selection for image and PDF types
            folder_id = None
            folder_security_summary = None
            
            if data_type in ["image", "pdf"]:
                folder_selection = secure_folder_selection_dialog(user_id, data_type, decode_window)
                if folder_selection["cancelled"]:
                    return  # User cancelled folder selection
                
                if folder_selection["use_security"]:
                    folder_id = folder_selection["folder_id"]
                    folder_security_summary = get_folder_security_summary(folder_id, user_id)
                    
                    # Show selected folder info
                    selected_folder_info.config(
                        text=f"{folder_security_summary['icon']} Selected: {folder_security_summary['folder_name']} "
                             f"({folder_security_summary['security_level']} Security)",
                        fg="blue"
                    )
                    decode_window.update()
                else:
                    selected_folder_info.config(text="📁 Saving to default user folder (no security)", fg="gray")
                    decode_window.update()
            
            # Enhanced progress dialog
            progress = tk.Toplevel(decode_window)
            progress.title("🔍 Decoding...")
            progress.geometry("350x120")
            progress.grab_set()
            progress.configure(bg=get_bg_color())
            
            progress_text = f"Decoding {data_type} from audio file..."
            if folder_id and folder_security_summary:
                if folder_security_summary['security_level'] == 'Maximum':
                    progress_text += f"\n🛡️ Preparing 7-Zip encrypted folder..."
                elif folder_security_summary['security_level'] == 'Enhanced':
                    progress_text += f"\n🫥 Preparing hidden secure folder..."
            
            tk.Label(progress, text=progress_text, 
                    font=("Arial", 10), bg=get_bg_color(), fg=get_fg_color()).pack(pady=20)
            progress.update()
            
            # Decode with folder information
            result = decode_data(audio_path, key_bytes, data_type, user_id, folder_id)
            
            progress.destroy()
            
            # Show enhanced result with security information
            format_name = format_info.get('format', 'audio').upper()
            
            if data_type == "message":
                messagebox.showinfo("✅ Decoded Message", 
                                  f"Successfully decoded from {format_name}!\n\n"
                                  f"📝 Message: {result}")
            elif data_type == "image":
                folder_info = ""
                if folder_id and folder_security_summary:
                    if folder_security_summary['security_level'] == 'Maximum':
                        folder_info = f"\n\n🛡️ Saved to 7-Zip AES-256 encrypted folder: {folder_security_summary['folder_name']}"
                        folder_info += f"\n🔒 Files are encrypted with military-grade security"
                    elif folder_security_summary['security_level'] == 'Enhanced':
                        folder_info = f"\n\n🫥 Saved to hidden secure folder: {folder_security_summary['folder_name']}"
                        folder_info += f"\n🔒 Folder is hidden from File Explorer"
                    else:
                        folder_info = f"\n\n🔓 Saved to secure folder: {folder_security_summary['folder_name']}"
                        folder_info += f"\n🔒 App-level password protection"
                else:
                    folder_info = f"\n\n📁 Saved to default user folder (no additional security)"
                
                messagebox.showinfo("✅ Decoded Image", 
                                  f"Successfully decoded from {format_name}!\n\n"
                                  f"🖼️ Image saved: {os.path.basename(result)}{folder_info}")
            elif data_type == "pdf":
                folder_info = ""
                if folder_id and folder_security_summary:
                    if folder_security_summary['security_level'] == 'Maximum':
                        folder_info = f"\n\n🛡️ Saved to 7-Zip AES-256 encrypted folder: {folder_security_summary['folder_name']}"
                        folder_info += f"\n🔒 Files are encrypted with military-grade security"
                    elif folder_security_summary['security_level'] == 'Enhanced':
                        folder_info = f"\n\n🫥 Saved to hidden secure folder: {folder_security_summary['folder_name']}"
                        folder_info += f"\n🔒 Folder is hidden from File Explorer"
                    else:
                        folder_info = f"\n\n🔓 Saved to secure folder: {folder_security_summary['folder_name']}"
                        folder_info += f"\n🔒 App-level password protection"
                else:
                    folder_info = f"\n\n📁 Saved to default user folder (no additional security)"
                
                messagebox.showinfo("✅ Decoded PDF", 
                                  f"Successfully decoded from {format_name}!\n\n"
                                  f"📄 PDF saved: {os.path.basename(result)}{folder_info}")
            
            decode_window.destroy()
            
        except ValueError as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            
            if "Invalid" in str(e) and "key" in str(e):
                status_label.config(text="❌ Invalid decryption key format", fg="red")
            elif "Unauthorized" in str(e):
                status_label.config(text="❌ Unauthorized: Your email does not match the recipient email", fg="red")
            elif "Invalid encoded data" in str(e):
                status_label.config(text=f"❌ {str(e)}", fg="red")
            elif "Could not decrypt folder" in str(e):
                status_label.config(text="❌ Could not access secure folder - check folder password", fg="red")
            else:
                status_label.config(text=f"❌ Decoding failed: {str(e)}", fg="red")
                
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            status_label.config(text=f"❌ Decoding error: {str(e)}", fg="red")
    
    def show_folder_preview():
        """Show a preview of available secure folders"""
        folders = db.get_user_secure_folders(user_id)
        if not folders:
            messagebox.showinfo("No Secure Folders", 
                              "You don't have any secure folders yet.\n"
                              "Create one during the decode process!", parent=decode_window)
            return
        
        preview_window = tk.Toplevel(decode_window)
        preview_window.title("🗂️ Your Secure Folders")
        preview_window.geometry("600x400")
        preview_window.grab_set()
        preview_window.configure(bg=get_bg_color())
        
        tk.Label(preview_window, text="🗂️ Your Secure Folders", 
                 font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
        
        # Statistics
        encrypted_count = sum(1 for folder in folders if len(folder) > 5 and folder[5] and folder[6] == '7zip_aes256')
        hidden_count = sum(1 for folder in folders if len(folder) > 8 and folder[8])
        
        stats_text = f"📊 {len(folders)} total folders • {encrypted_count} 7-Zip encrypted • {hidden_count} hidden"
        tk.Label(preview_window, text=stats_text, 
                 font=("Arial", 10), bg=get_bg_color(), fg="gray").pack(pady=5)
        
        # Folder list
        list_frame = tk.Frame(preview_window, bg=get_bg_color())
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for folder in folders[:5]:  # Show first 5 folders
            folder_frame = tk.Frame(list_frame, bg=get_bg_color(), relief="ridge", bd=1)
            folder_frame.pack(fill="x", pady=2)
            
            is_encrypted = len(folder) > 5 and folder[5]
            encryption_method = folder[6] if len(folder) > 6 else 'none'
            is_hidden = len(folder) > 8 and folder[8] if len(folder) > 8 else False
            
            if is_encrypted and encryption_method == '7zip_aes256':
                icon, status = "🛡️", "7-Zip AES-256"
            elif is_hidden:
                icon, status = "🫥", "Hidden"
            else:
                icon, status = "🔓", "App-level"
            
            tk.Label(folder_frame, text=f"{icon} {folder[1]} • {status}", 
                     font=("Arial", 9), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", padx=10, pady=3)
        
        if len(folders) > 5:
            tk.Label(list_frame, text=f"... and {len(folders) - 5} more folders", 
                     font=("Arial", 8), bg=get_bg_color(), fg="gray").pack(pady=5)
        
        tk.Button(preview_window, text="✅ Close", command=preview_window.destroy,
                  bg="#4CAF50", fg="white", font=("Arial", 10)).pack(pady=15)
    
    def cleanup_and_close():
        """Cleanup audio resources when closing"""
        try:
            audio_preview.cleanup()
        except:
            pass
        decode_window.destroy()
    
    # Override window close button to cleanup audio
    decode_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)
    
    # Buttons
    button_frame = tk.Frame(decode_window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🔓 Decode", command=perform_decode, 
              bg="#FF9800", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="🗂️ View Folders", command=show_folder_preview,
              bg="#2196F3", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=cleanup_and_close,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    # Enhanced Instructions with 7-Zip security info
    instructions_frame = tk.Frame(decode_window, bg=get_bg_color(), relief="groove", bd=1)
    instructions_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(instructions_frame, text="💡 Instructions:", 
             bg=get_bg_color(), font=("Arial", 10, "bold"), fg=get_fg_color()).pack(anchor="w", padx=5, pady=2)
    tk.Label(instructions_frame, text="1. Select your encoded audio file and preview it if needed", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="2. Enter the decryption key provided during encoding", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="3. Choose the correct data type and click 'Decode'", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15)
    
    if zip_available:
        tk.Label(instructions_frame, text="4. For images/PDFs: Choose 7-Zip encrypted, hidden, or standard secure folders", 
                 bg=get_bg_color(), font=("Arial", 9), fg="green").pack(anchor="w", padx=15)
    else:
        tk.Label(instructions_frame, text="4. For images/PDFs: Choose hidden or standard secure folders", 
                 bg=get_bg_color(), font=("Arial", 9), fg="orange").pack(anchor="w", padx=15)
    
    tk.Label(instructions_frame, text="5. Note: You must be logged in with the recipient email", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15, pady=(0,5))
