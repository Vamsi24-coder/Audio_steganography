import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
from database import DatabaseManager
from steganography_utils import encode_data, validate_image_file, validate_pdf_file, get_file_size_mb
from email_utils import send_email, test_smtp_connection, show_password_info, validate_email_address
from gui.file_operations import select_audio_file_dialog
from gui.utils import show_format_info
from audio_player import AudioPreviewWidget

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
                # Only change text color for normal labels, keep special colors
                if current_fg in ['#000000', '#ffffff', 'black', 'white', 'SystemWindowText']:
                    widget.configure(bg=bg, fg=fg)
                elif current_fg == 'gray':
                    widget.configure(bg=bg)  # Keep gray text as gray
                else:
                    widget.configure(bg=bg)  # Keep special text colors (like green, red, orange)
            elif widget_class == 'Button':
                current_bg = str(widget.cget('bg'))
                # Update themed buttons, leave colored buttons alone
                if current_bg in ['#4CAF50', '#333333', get_bg_color()]:
                    widget.configure(bg=button_bg, fg=button_fg)
                # Leave other colored buttons (like #FF9800, #FF5722, etc.) unchanged
            elif widget_class == 'Entry':
                if DARK_MODE:
                    widget.configure(bg=bg, fg=fg, insertbackground=fg)
                else:
                    widget.configure(bg="white", fg="black", insertbackground="black")
            elif widget_class == 'Radiobutton':
                widget.configure(bg=bg, fg=fg, selectcolor=bg, activebackground=bg, activeforeground=fg)
            
            # Recursively apply to children
            for child in widget.winfo_children():
                update_widget(child)
                
        except Exception:
            pass
    
    update_widget(window)


def encode_data_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Data type selection dialog with simple, reliable theme management"""
    encode_window = tk.Toplevel()
    encode_window.title("Select Data Type")
    encode_window.geometry("500x400")
    encode_window.grab_set()
    encode_window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(encode_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", encode_window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", encode_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    encode_window.config(menu=menubar)
    
    tk.Label(encode_window, text="What would you like to hide?", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)
    
    data_type_var = tk.StringVar(value="message")
    
    tk.Radiobutton(encode_window, text="📝 Text Message", 
                   variable=data_type_var, value="message", 
                   font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color(),
                   selectcolor=get_bg_color(), activebackground=get_bg_color(),
                   activeforeground=get_fg_color()).pack(pady=8)
    
    tk.Radiobutton(encode_window, text="🖼️ JPG Image", 
                   variable=data_type_var, value="image", 
                   font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color(),
                   selectcolor=get_bg_color(), activebackground=get_bg_color(),
                   activeforeground=get_fg_color()).pack(pady=8)
    
    tk.Radiobutton(encode_window, text="📄 PDF Document", 
                   variable=data_type_var, value="pdf", 
                   font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color(),
                   selectcolor=get_bg_color(), activebackground=get_bg_color(),
                   activeforeground=get_fg_color()).pack(pady=8)
    
    def proceed():
        data_type = data_type_var.get()
        encode_window.destroy()
        
        if data_type == "message":
            encode_message_dialog(user_id, sender_email, smtp_username, smtp_password)
        elif data_type == "image":
            encode_image_dialog(user_id, sender_email, smtp_username, smtp_password)
        elif data_type == "pdf":
            encode_pdf_dialog(user_id, sender_email, smtp_username, smtp_password)
    
    tk.Button(encode_window, text="Continue", command=proceed,
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12)).pack(pady=20)


def encode_message_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Encode message dialog with audio preview functionality and simple theme management"""
    
    window = tk.Toplevel()
    window.title("Encode Message")
    window.geometry("1000x700")
    window.grab_set()
    window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    window.config(menu=menubar)
    
    tk.Label(window, text="📝 Encode Text Message", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=10)
    
    # Message input
    tk.Label(window, text="Message (max 255 characters):", 
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    message_entry = tk.Entry(window, width=60, 
                            bg="white" if not DARK_MODE else get_bg_color(), 
                            fg="black" if not DARK_MODE else get_fg_color(),
                            insertbackground="black" if not DARK_MODE else get_fg_color())
    message_entry.pack(pady=5)
    
    # Character counter
    char_label = tk.Label(window, text="0/255", fg="gray", bg=get_bg_color())
    char_label.pack()
    
    def update_char_count(*args):
        count = len(message_entry.get())
        char_label.config(text=f"{count}/255", fg="red" if count > 255 else "gray")
    
    message_entry.bind('<KeyRelease>', update_char_count)
    
    # Recipient email
    tk.Label(window, text="Recipient Email:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))
    recipient_entry = tk.Entry(window, width=60, 
                              bg="white" if not DARK_MODE else get_bg_color(), 
                              fg="black" if not DARK_MODE else get_fg_color(),
                              insertbackground="black" if not DARK_MODE else get_fg_color())
    recipient_entry.pack(pady=5)
    
    # Audio file selection
    audio_path_var = tk.StringVar()
    format_info = {}
    
    tk.Label(window, text="Select Audio File (WAV or FLAC):", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))
    
    audio_frame = tk.Frame(window, bg=get_bg_color())
    audio_frame.pack(pady=5)
    
    tk.Entry(audio_frame, textvariable=audio_path_var, width=50, 
             state='readonly', bg="white" if not DARK_MODE else get_bg_color(), 
             fg="black" if not DARK_MODE else get_fg_color()).pack(side=tk.LEFT, padx=5)
    
    info_label = tk.Label(window, text="No audio file selected", fg="gray", bg=get_bg_color())
    info_label.pack(pady=5)
    
    # Status label for audio loading feedback
    status_label = tk.Label(window, text="", font=("Arial", 9), bg=get_bg_color())
    status_label.pack(pady=2)
    
    # Audio preview widget
    tk.Label(window, text="🎵 Audio Preview:", 
             font=("Arial", 11, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))
    
    audio_preview = AudioPreviewWidget(window)
    
    def browse_audio():
        path, info = select_audio_file_dialog("Select Audio File for Message")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            info_label.config(text=show_format_info(info), fg="green")
            
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
            info_label.config(text="No audio file selected", fg="gray")
    
    tk.Button(audio_frame, text="Browse & Load Audio", command=browse_audio,
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
    
    def perform_encode():
        # Stop any playing audio before encoding
        try:
            audio_preview.stop_audio()
        except:
            pass
        
        message = message_entry.get().strip()
        recipient = recipient_entry.get().strip()
        audio_path = audio_path_var.get()
        
        if not message:
            status_label.config(text="❌ Please enter a message", fg="red")
            return
        if len(message) > 255:
            status_label.config(text="❌ Message too long (max 255 characters)", fg="red")
            return
        if not recipient:
            status_label.config(text="❌ Please enter recipient email", fg="red")
            return
        # Add email validation
        is_valid_email, email_message = validate_email_address(recipient)
        if not is_valid_email:
            status_label.config(text=f"❌ {email_message}", fg="red")
            return

        if not audio_path:
            status_label.config(text="❌ Please select an audio file", fg="red")
            return
        
        # Clear any previous status messages
        status_label.config(text="", fg=get_fg_color())
        
        # Create output
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = int(time.time())
        base_name = os.path.basename(audio_path)
        output_filename = f"encoded_message_{format_info['format']}_{timestamp}_{base_name}"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Show progress
            progress = tk.Toplevel(window)
            progress.title("Encoding...")
            progress.geometry("350x120")
            progress.grab_set()
            progress.configure(bg=get_bg_color())
            tk.Label(progress, text="Encoding message, please wait...", 
                    font=("Arial", 11), bg=get_bg_color(), fg=get_fg_color()).pack(pady=20)
            tk.Label(progress, text="This may take a moment for large files...", 
                    font=("Arial", 9), fg="gray", bg=get_bg_color()).pack()
            progress.update()
            
            # Encode
            key = encode_data(audio_path, message, output_path, "message", 
                            user_id, message, recipient)
            
            progress.destroy()
            # Create informative email body
            email_body = f"""Hello {recipient},

            🎵 You have received a TEXT MESSAGE from {sender_email}

            Data Type: Text Message
            Audio Format: {format_info['format'].upper()}
            Encoding Method: LSB Steganography

            To decode this message:
            1. Open the Audio Steganography application
            2. Select "Decode Audio File" 
            3. Choose "Text Message" as the data type
            4. Use the decryption key provided below

            The encoded audio file is attached to this email.

            Best regards,
            Audio Steganography System"""

            # Send email with custom body
            send_email(recipient, key, output_path, sender_email, 
                    smtp_username, smtp_password, "message", 
                    format_info['format'], 'lsb', custom_body=email_body)

            
            # Show simple success message
            messagebox.showinfo("Encoding Complete", 
                               f"✅ Message encoded successfully!\n\n"
                               f"📄 Output: {output_filename}\n"
                               f"🎵 Format: {format_info['format'].upper()}\n"
                               f"📧 Email sent to: {recipient}")
            
            window.destroy()
            
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            status_label.config(text=f"❌ Encoding Failed: {str(e)}", fg="red")
    
    def cleanup_and_close():
        """Cleanup audio resources when closing"""
        try:
            audio_preview.cleanup()
        except:
            pass
        window.destroy()
    
    # Override window close button to cleanup audio
    window.protocol("WM_DELETE_WINDOW", cleanup_and_close)
    
    # Buttons
    button_frame = tk.Frame(window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🎤 Encode & Send", command=perform_encode,
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=cleanup_and_close,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    # Instructions
    instructions_frame = tk.Frame(window, bg=get_bg_color(), relief="groove", bd=1)
    instructions_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(instructions_frame, text="💡 Instructions:", 
             bg=get_bg_color(), font=("Arial", 10, "bold"), fg=get_fg_color()).pack(anchor="w", padx=5, pady=2)
    tk.Label(instructions_frame, text="1. Select your audio file and preview it to ensure quality", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="2. Enter your message and recipient email", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="3. Click 'Encode & Send' to hide your message in the audio", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack(anchor="w", padx=15, pady=(0,5))


def encode_image_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Encode image dialog with audio preview functionality and simple theme management"""
    window = tk.Toplevel()
    window.title("Encode Image")
    window.geometry("700x750")  # Increased height for audio preview
    window.grab_set()
    window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    window.config(menu=menubar)
    
    tk.Label(window, text="🖼️ Encode JPG Image", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=10)
    
    # Image selection
    image_path_var = tk.StringVar()
    tk.Label(window, text="Select JPG Image:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
    image_frame = tk.Frame(window, bg=get_bg_color())
    image_frame.pack(pady=5)
    
    tk.Entry(image_frame, textvariable=image_path_var, width=50, state='readonly',
             bg="white" if not DARK_MODE else get_bg_color(), 
             fg="black" if not DARK_MODE else get_fg_color()).pack(side=tk.LEFT, padx=5)
    
    image_info_label = tk.Label(window, text="No image selected", fg="gray", bg=get_bg_color())
    image_info_label.pack(pady=5)
    
    def browse_image():
        file_path = filedialog.askopenfilename(
            title="Select JPG Image",
            filetypes=[("JPG files", "*.jpg"), ("JPEG files", "*.jpeg")]
        )
        if file_path:
            is_valid, message = validate_image_file(file_path)
            if is_valid:
                image_path_var.set(file_path)
                size_mb = get_file_size_mb(file_path)
                image_info_label.config(
                    text=f"✅ Image: {os.path.basename(file_path)} ({size_mb:.1f}MB)",
                    fg="green"
                )
            else:
                messagebox.showerror("Error", message)
    
    tk.Button(image_frame, text="Browse", command=browse_image,
              bg="#FF5722", fg="white").pack(side=tk.LEFT)
    
    # Audio file selection
    audio_path_var = tk.StringVar()
    format_info = {}
    
    tk.Label(window, text="Select Audio File (WAV or FLAC):", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))
    
    audio_frame = tk.Frame(window, bg=get_bg_color())
    audio_frame.pack(pady=5)
    
    tk.Entry(audio_frame, textvariable=audio_path_var, width=50, state='readonly',
             bg="white" if not DARK_MODE else get_bg_color(), 
             fg="black" if not DARK_MODE else get_fg_color()).pack(side=tk.LEFT, padx=5)
    
    audio_info_label = tk.Label(window, text="No audio file selected", fg="gray", bg=get_bg_color())
    audio_info_label.pack(pady=5)
    
    # Status label for audio loading feedback
    status_label = tk.Label(window, text="", font=("Arial", 9), bg=get_bg_color())
    status_label.pack(pady=2)
    
    # Audio preview widget
    tk.Label(window, text="🎵 Audio Preview:", 
             font=("Arial", 11, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))
    
    audio_preview = AudioPreviewWidget(window)
    
    def browse_audio():
        path, info = select_audio_file_dialog("Select Audio File for Image")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            audio_info_label.config(text=show_format_info(info), fg="green")
            
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
            audio_info_label.config(text="No audio file selected", fg="gray")
    
    tk.Button(audio_frame, text="Browse & Load Audio", command=browse_audio,
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
    
    # Recipient email
    tk.Label(window, text="Recipient Email:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))
    recipient_entry = tk.Entry(window, width=60, 
                              bg="white" if not DARK_MODE else get_bg_color(), 
                              fg="black" if not DARK_MODE else get_fg_color(),
                              insertbackground="black" if not DARK_MODE else get_fg_color())
    recipient_entry.pack(pady=5)
    
    def perform_encode():
        # Stop any playing audio before encoding
        try:
            audio_preview.stop_audio()
        except:
            pass
            
        image_path = image_path_var.get()
        audio_path = audio_path_var.get()
        recipient = recipient_entry.get().strip()
        
        if not image_path:
            status_label.config(text="❌ Please select an image file", fg="red")
            return
        if not audio_path:
            status_label.config(text="❌ Please select an audio file", fg="red")
            return
        if not recipient:
            status_label.config(text="❌ Please enter recipient email", fg="red")
            return
        
        # Clear any previous status messages
        status_label.config(text="", fg=get_fg_color())
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            output_dir = "Output"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = int(time.time())
            base_name = os.path.basename(audio_path)
            output_filename = f"encoded_image_{format_info['format']}_{timestamp}_{base_name}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Show progress
            progress = tk.Toplevel(window)
            progress.title("Encoding...")
            progress.geometry("350x120")
            progress.grab_set()
            progress.configure(bg=get_bg_color())
            tk.Label(progress, text="Encoding image, please wait...", 
                    font=("Arial", 11), bg=get_bg_color(), fg=get_fg_color()).pack(pady=20)
            tk.Label(progress, text="This may take a moment for large files...", 
                    font=("Arial", 9), fg="gray", bg=get_bg_color()).pack()
            progress.update()
            
            # Encode
            key = encode_data(audio_path, image_data, output_path, "image", 
                            user_id, image_path, recipient)
            
            progress.destroy()
            
            # Create informative email body
            email_body = f"""Hello {recipient},

🖼️ You have received a JPG IMAGE from {sender_email}

Data Type: JPG Image
Audio Format: {format_info['format'].upper()}
Encoding Method: LSB Steganography

To decode this image:
1. Open the Audio Steganography application
2. Select "Decode Audio File"
3. Choose "JPG Image" as the data type
4. Use the decryption key provided below

The encoded audio file is attached to this email.

Best regards,
Audio Steganography System"""

            # Send email with custom body
            send_email(recipient, key, output_path, sender_email, 
                      smtp_username, smtp_password, "image", 
                      format_info['format'], 'lsb', custom_body=email_body)
            
            messagebox.showinfo("Encoding Complete", 
                               f"✅ Image encoded successfully!\n\n"
                               f"📄 Output: {output_filename}\n"
                               f"🎵 Format: {format_info['format'].upper()}\n"
                               f"📧 Email sent to: {recipient}")
            
            window.destroy()
            
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            status_label.config(text=f"❌ Encoding Failed: {str(e)}", fg="red")
    
    def cleanup_and_close():
        """Cleanup audio resources when closing"""
        try:
            audio_preview.cleanup()
        except:
            pass
        window.destroy()
    
    # Override window close button to cleanup audio
    window.protocol("WM_DELETE_WINDOW", cleanup_and_close)
    
    # Buttons
    button_frame = tk.Frame(window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🖼️ Encode & Send", command=perform_encode,
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=cleanup_and_close,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)



def encode_pdf_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Encode PDF dialog with audio preview functionality and simple theme management"""
    window = tk.Toplevel()
    window.title("Encode PDF")
    window.geometry("700x750")  # Increased height for audio preview
    window.grab_set()
    window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    window.config(menu=menubar)
    
    tk.Label(window, text="📄 Encode PDF Document", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=10)
    
    # PDF selection
    pdf_path_var = tk.StringVar()
    tk.Label(window, text="Select PDF Document:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
    pdf_frame = tk.Frame(window, bg=get_bg_color())
    pdf_frame.pack(pady=5)
    
    tk.Entry(pdf_frame, textvariable=pdf_path_var, width=50, state='readonly',
             bg="white" if not DARK_MODE else get_bg_color(), 
             fg="black" if not DARK_MODE else get_fg_color()).pack(side=tk.LEFT, padx=5)
    
    pdf_info_label = tk.Label(window, text="No PDF selected", fg="gray", bg=get_bg_color())
    pdf_info_label.pack(pady=5)
    
    def browse_pdf():
        file_path = filedialog.askopenfilename(
            title="Select PDF Document",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            is_valid, message = validate_pdf_file(file_path)
            if is_valid:
                pdf_path_var.set(file_path)
                size_mb = get_file_size_mb(file_path)
                pdf_info_label.config(
                    text=f"✅ PDF: {os.path.basename(file_path)} ({size_mb:.1f}MB)",
                    fg="green"
                )
            else:
                messagebox.showerror("Error", message)
    
    tk.Button(pdf_frame, text="Browse", command=browse_pdf,
              bg="#FF5722", fg="white").pack(side=tk.LEFT)
    
    # Audio file selection
    audio_path_var = tk.StringVar()
    format_info = {}
    
    tk.Label(window, text="Select Audio File (WAV or FLAC):", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))
    
    audio_frame = tk.Frame(window, bg=get_bg_color())
    audio_frame.pack(pady=5)
    
    tk.Entry(audio_frame, textvariable=audio_path_var, width=50, state='readonly',
             bg="white" if not DARK_MODE else get_bg_color(), 
             fg="black" if not DARK_MODE else get_fg_color()).pack(side=tk.LEFT, padx=5)
    
    audio_info_label = tk.Label(window, text="No audio file selected", fg="gray", bg=get_bg_color())
    audio_info_label.pack(pady=5)
    
    # Status label for audio loading feedback
    status_label = tk.Label(window, text="", font=("Arial", 9), bg=get_bg_color())
    status_label.pack(pady=2)
    
    # Audio preview widget
    tk.Label(window, text="🎵 Audio Preview:", 
             font=("Arial", 11, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))
    
    audio_preview = AudioPreviewWidget(window)
    
    def browse_audio():
        path, info = select_audio_file_dialog("Select Audio File for PDF")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            audio_info_label.config(text=show_format_info(info), fg="green")
            
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
            audio_info_label.config(text="No audio file selected", fg="gray")
    
    tk.Button(audio_frame, text="Browse & Load Audio", command=browse_audio,
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
    
    # Recipient email
    tk.Label(window, text="Recipient Email:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))
    recipient_entry = tk.Entry(window, width=60, 
                              bg="white" if not DARK_MODE else get_bg_color(), 
                              fg="black" if not DARK_MODE else get_fg_color(),
                              insertbackground="black" if not DARK_MODE else get_fg_color())
    recipient_entry.pack(pady=5)
    
    def perform_encode():
        # Stop any playing audio before encoding
        try:
            audio_preview.stop_audio()
        except:
            pass
            
        pdf_path = pdf_path_var.get()
        audio_path = audio_path_var.get()
        recipient = recipient_entry.get().strip()
        
        if not pdf_path:
            status_label.config(text="❌ Please select a PDF file", fg="red")
            return
        if not audio_path:
            status_label.config(text="❌ Please select an audio file", fg="red")
            return
        if not recipient:
            status_label.config(text="❌ Please enter recipient email", fg="red")
            return
        
        # Clear any previous status messages
        status_label.config(text="", fg=get_fg_color())
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
            
            output_dir = "Output"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = int(time.time())
            base_name = os.path.basename(audio_path)
            output_filename = f"encoded_pdf_{format_info['format']}_{timestamp}_{base_name}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Show progress
            progress = tk.Toplevel(window)
            progress.title("Encoding...")
            progress.geometry("350x120")
            progress.grab_set()
            progress.configure(bg=get_bg_color())
            tk.Label(progress, text="Encoding PDF, please wait...", 
                    font=("Arial", 11), bg=get_bg_color(), fg=get_fg_color()).pack(pady=20)
            tk.Label(progress, text="This may take a moment for large files...", 
                    font=("Arial", 9), fg="gray", bg=get_bg_color()).pack()
            progress.update()
            
            # Encode
            key = encode_data(audio_path, pdf_data, output_path, "pdf", 
                            user_id, pdf_path, recipient)
            
            progress.destroy()
            
            # Create informative email body
            email_body = f"""Hello {recipient},

📄 You have received a PDF DOCUMENT from {sender_email}

Data Type: PDF Document  
Audio Format: {format_info['format'].upper()}
Encoding Method: LSB Steganography

To decode this PDF:
1. Open the Audio Steganography application
2. Select "Decode Audio File"
3. Choose "PDF Document" as the data type
4. Use the decryption key provided below

The encoded audio file is attached to this email.

Best regards,
Audio Steganography System"""

            # Send email with custom body
            send_email(recipient, key, output_path, sender_email, 
                      smtp_username, smtp_password, "pdf", 
                      format_info['format'], 'lsb', custom_body=email_body)
            
            messagebox.showinfo("Encoding Complete", 
                               f"✅ PDF encoded successfully!\n\n"
                               f"📄 Output: {output_filename}\n"
                               f"🎵 Format: {format_info['format'].upper()}\n"
                               f"📧 Email sent to: {recipient}")
            
            window.destroy()
            
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            status_label.config(text=f"❌ Encoding Failed: {str(e)}", fg="red")
    
    def cleanup_and_close():
        """Cleanup audio resources when closing"""
        try:
            audio_preview.cleanup()
        except:
            pass
        window.destroy()
    
    # Override window close button to cleanup audio
    window.protocol("WM_DELETE_WINDOW", cleanup_and_close)
    
    # Buttons
    button_frame = tk.Frame(window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="📄 Encode & Send", command=perform_encode,
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=cleanup_and_close,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)


def encode_smtp_dialog(user_id):
    """SMTP configuration dialog with simple, reliable theme management"""
    db = DatabaseManager()
    smtp_window = tk.Toplevel()
    smtp_window.title("SMTP Configuration")
    smtp_window.geometry("500x500")
    smtp_window.grab_set()
    smtp_window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(smtp_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", smtp_window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", smtp_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    smtp_window.config(menu=menubar)
    
    # Load saved credentials
    try:
        credentials = db.get_credentials(user_id)
        default_email = credentials[0] if credentials else ""
        default_username = credentials[1] if credentials else ""
        default_password = credentials[2] if credentials else ""
    except:
        default_email = default_username = default_password = ""
    
    tk.Label(smtp_window, text="📧 Email Configuration", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
    
    # Sender Email
    tk.Label(smtp_window, text="Sender Email (e.g., user@gmail.com):", 
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    sender_entry = tk.Entry(smtp_window, width=50, 
                           bg="white" if not DARK_MODE else get_bg_color(), 
                           fg="black" if not DARK_MODE else get_fg_color(),
                           insertbackground="black" if not DARK_MODE else get_fg_color())
    sender_entry.insert(0, default_email)
    sender_entry.pack(pady=2)
    
    sender_status_label = tk.Label(smtp_window, text="", font=("Arial", 9), bg=get_bg_color())
    sender_status_label.pack(pady=2)
    
    # SMTP Username
    tk.Label(smtp_window, text="SMTP Username (same as sender email):", 
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))
    username_entry = tk.Entry(smtp_window, width=50, 
                             bg="white" if not DARK_MODE else get_bg_color(), 
                             fg="black" if not DARK_MODE else get_fg_color(),
                             insertbackground="black" if not DARK_MODE else get_fg_color())
    username_entry.insert(0, default_username)
    username_entry.pack(pady=2)
    
    username_status_label = tk.Label(smtp_window, text="", font=("Arial", 9), bg=get_bg_color())
    username_status_label.pack(pady=2)
    
    # SMTP Password
    tk.Label(smtp_window, text="SMTP App Password:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))
    password_entry = tk.Entry(smtp_window, width=50, show="*", 
                             bg="white" if not DARK_MODE else get_bg_color(), 
                             fg="black" if not DARK_MODE else get_fg_color(),
                             insertbackground="black" if not DARK_MODE else get_fg_color())
    password_entry.insert(0, default_password)
    password_entry.pack(pady=5)
    
    tk.Button(smtp_window, text="ℹ️ How to get App Password", 
              command=show_password_info, bg="#FFC107", fg="black").pack(pady=5)
    
    # Test Connection Status
    test_status_label = tk.Label(smtp_window, text="", font=("Arial", 9), 
                                wraplength=450, bg=get_bg_color(), fg=get_fg_color())
    test_status_label.pack(pady=5)
    
    # State variable for button enable/disable
    continue_button_state = tk.BooleanVar(value=False)
    
    def validate_inputs():
        """Validate email and username, update button state"""
        sender_email = sender_entry.get().strip()
        smtp_username = username_entry.get().strip()
        smtp_password = password_entry.get().strip()
        
        # Validate sender email
        is_valid_email, email_message = validate_email_address(sender_email)
        sender_status_label.config(
            text=email_message,
            fg="green" if is_valid_email else "red"
        )
        
        # Validate username (must match sender email)
        username_valid = smtp_username == sender_email and is_valid_email
        username_status_label.config(
            text="✅ Matches sender email" if username_valid else "❌ Must match sender email",
            fg="green" if username_valid else "red"
        )
        
        # Enable continue button only if all inputs are valid
        continue_button_state.set(is_valid_email and username_valid and bool(smtp_password))
    
    def test_connection():
        """Test SMTP connection and show result"""
        sender_email = sender_entry.get().strip()
        smtp_username = username_entry.get().strip()
        smtp_password = password_entry.get().strip()
        
        if not sender_email or not smtp_username or not smtp_password:
            test_status_label.config(text="❌ Please fill all fields before testing", fg="red")
            return
        
        test_status_label.config(text="🔄 Testing connection, please wait...", fg="blue")
        smtp_window.update()
        
        try:
            success, message = test_smtp_connection(smtp_username, smtp_password, sender_email)
            test_status_label.config(text=message, fg="green" if success else "red")
        except Exception as e:
            test_status_label.config(text=f"❌ Test failed: {str(e)}", fg="red")
    
    def submit_smtp():
        sender_email = sender_entry.get().strip()
        smtp_username = username_entry.get().strip()
        smtp_password = password_entry.get().strip()
        
        # Final validation
        is_valid_email, _ = validate_email_address(sender_email)
        if not is_valid_email:
            messagebox.showerror("Error", "Invalid email format")
            return
        if smtp_username != sender_email:
            messagebox.showerror("Error", "SMTP username must match sender email")
            return
        if not smtp_password:
            messagebox.showerror("Error", "SMTP password required")
            return
        
        try:
            db.save_credentials(user_id, sender_email, smtp_username, smtp_password)
            smtp_window.destroy()
            encode_data_dialog(user_id, sender_email, smtp_username, smtp_password)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")
    
    # Bind validation to entry fields
    sender_entry.bind('<KeyRelease>', lambda e: validate_inputs())
    username_entry.bind('<KeyRelease>', lambda e: validate_inputs())
    password_entry.bind('<KeyRelease>', lambda e: validate_inputs())
    
    # Initial validation
    validate_inputs()
    
    # Button Frame
    button_frame = tk.Frame(smtp_window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Test Connection", command=test_connection,
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    continue_button = tk.Button(button_frame, text="Continue", command=submit_smtp,
                                bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12),
                                state='normal' if continue_button_state.get() else 'disabled')
    continue_button.pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Cancel", command=smtp_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    
    # Update continue button state dynamically
    def update_continue_button(*args):
        continue_button.config(state='normal' if continue_button_state.get() else 'disabled')
    
    continue_button_state.trace('w', update_continue_button)
