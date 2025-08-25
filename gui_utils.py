import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
import time
import datetime
from steganography_utils import (
    encode_data, decode_data, validate_image_file, validate_pdf_file, 
    get_file_size_mb, estimate_audio_duration_needed
)
import ast
import inspect
from email_utils import send_email, show_password_info, validate_email_address, test_smtp_connection
from database import DatabaseManager
from audio_format_handler import AudioFormatHandler
from audio_player import AudioPreviewWidget
import tempfile
import webbrowser

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

def show_format_info(format_info):
    """Display audio format information"""
    return (
        f"Format: {format_info['format'].upper()}\n"
        f"Codec: {format_info.get('codec', 'Unknown')}\n"
        f"Sample Rate: {format_info.get('sample_rate', 0)} Hz\n"
        f"Channels: {format_info.get('channels', 0)}\n"
        f"Duration: {format_info.get('duration', 0):.1f} seconds\n"
        f"Method: LSB Steganography (High Quality)"
    )


def project_info():
    logo_path = os.path.abspath("E:\Audio Stenography\enh_project\gui\logo1.jpg")
    logo_url = urllib.request.pathname2url(logo_path) 
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
            }
            h1, h2 {
                color: #333;
            }
            .logo-container {
                position: absolute;
                top: 20px;
                right: 35px;
            }
            .logo-container img {
                max-height: 800px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.13);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: #fff;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            th, td {
                border: 1px solid #ccc;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
    <div class="logo-container">
        <img src="file://{logo_url}" alt="Project Logo">
    </div>
    <h1>Project Information</h1>
    <p>
        This project was developed by Anonymous as part of a <b>Cyber Security Internship</b>.
        This project is designed to Secure the Organizations in Real World from Cyber Frauds performed by Hackers.</p>
    <table>
        <thead>
            <tr>
                <th>Project Details</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Project Name</td>
                <td>Audio Steganography using LSB</td>
            </tr>
            <tr>
                <td>Project Description</td>
                <td>Hiding Message with Encryption in Audio using LSB Algorithm</td>
            </tr>
            <tr>
                <td>Project Start Date</td>
                <td>01-July-2025</td>
            </tr>
            <tr>
                <td>Project End Date</td>
                <td>21-July-2025</td>
            </tr>
            <tr>
                <td>Project Status</td>
                <td><b>Completed</b></td>
            </tr>
        </tbody>
    </table>
    
    <h2>Developer Details</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Employee ID</th>
                <th>Email</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Siva Kumar Reddy Babu</td>
                <td>ST#IS#7706</td>
                <td>sivakumarreddy.2204@gmail.com</td>
            </tr>
             <tr>
                <td>Siva Manikanta Ballppu</td>
                <td>ST#IS#7707</td>
                <td>Mkanta86988@gmail.com</td>
            </tr>
            <tr>
                <td>T.Venkata Gopi Naveen </td>
                <td>ST#IS#7709</td>
                <td>naveentulluru@gmail.com</td>
            </tr>
            <tr>
                <td>T.Nirmala Jyothi</td>
                <td>ST#IS#7710</td>
                <td>nimmunirmalajyothi@gmail.com</td>
            </tr>
            <tr>
                <td>Talluri Ramya</td>
                <td>ST#IS#7711</td>
                <td>ramyatalluri445@gmail.com</td>
            </tr>
             <tr>
                <td>Shaik Tasneem Firdose</td>
                <td>ST#IS#7705</td>
                <td>tasneemfirdose264@gmail.com</td>
            </tr>
        </tbody>
    </table>

    <h2>Company Information</h2>
    <table>
        <thead>
            <tr>
                <th>Company</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Name</td>
                <td>Supraja Technologies</td>
            </tr>
            <tr>
                <td>Email</td>
                <td>contact@suprajatechnologies.com</td>
            </tr>
        </tbody>
    </table>
    </body>
    </html>
    """
    # Create a temporary HTML file and write the above content
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as temp_file:
        temp_file.write(html_code)
        temp_file_path = temp_file.name
    return temp_file_path

def open_project_info():
    file_path = project_info()
    webbrowser.open('file://' + file_path)




def login_dialog():
    """Login dialog with proper window management - main app becomes master"""
    db = DatabaseManager()
    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.geometry("400x250")
    login_window.grab_set()
    
    tk.Label(login_window, text="🎵 Audio Steganography Login", 
             font=("Arial", 14, "bold")).pack(pady=20)
    
    tk.Label(login_window, text="Username or Email:").pack(pady=5)
    username_entry = tk.Entry(login_window, width=40)
    username_entry.pack(pady=5)
    
    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, width=40, show="*")
    password_entry.pack(pady=5)
    
    def perform_login():
        username = username_entry.get().strip()
        password = password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            success, result = db.login(username, password)
            if success:
                # Get reference to root window (from main.py)
                root_window = login_window.master
                
                # Close login window first
                login_window.destroy()
                
                # Destroy the original root window completely
                if root_window:
                    root_window.destroy()
                
                # Create new root window for main app (becomes the master)
                new_root = tk.Tk()
                new_root.withdraw()  # Hide the new root window
                
                # Show main app window as a Toplevel of new root
                # But configure it to act as master
                main_app_window = main_app(result, master_root=new_root)
                
                # When main app window closes, close the entire application
                def on_main_app_close():
                    new_root.quit()  # Stop the mainloop
                    new_root.destroy()  # Destroy the root window
                
                # Set the close protocol for main app window
                if main_app_window:
                    main_app_window.protocol("WM_DELETE_WINDOW", on_main_app_close)
                
                # Start the new mainloop
                new_root.mainloop()
                
            else:
                messagebox.showerror("Error", result)
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
    
    def on_enter(event):
        """Allow Enter key to trigger login"""
        perform_login()
    
    # Bind Enter key to password field
    password_entry.bind('<Return>', on_enter)
    username_entry.bind('<Return>', on_enter)
    
    tk.Button(login_window, text="Login", command=perform_login,
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=15)
    
    tk.Button(login_window, text="Sign Up", 
              command=lambda: [login_window.destroy(), signup_dialog()],
              bg="#2196F3", fg="white", font=("Arial", 10)).pack(pady=5)
    
    

    
    # Focus on username field when dialog opens
    username_entry.focus_set()


def signup_dialog():
    """Signup dialog"""
    db = DatabaseManager()
    signup_window = tk.Toplevel()
    signup_window.title("Sign Up")
    signup_window.geometry("500x500")
    signup_window.grab_set()
    
    tk.Label(signup_window, text="Create New Account", 
             font=("Arial", 14, "bold")).pack(pady=20)
    
    fields = [
        ("First Name:", "first_name"),
        ("Last Name:", "last_name"),
        ("Username:", "username"),
        ("Email:", "email"),
        ("Password:", "password")
    ]
    
    entries = {}
    for label, field in fields:
        tk.Label(signup_window, text=label).pack(pady=3)
        entry = tk.Entry(signup_window, width=40, show="*" if field == "password" else None)
        entry.pack(pady=3)
        entries[field] = entry
    
    tk.Label(signup_window, text="Password: min 10 chars, letters, numbers, special", 
             font=("Arial", 8), fg="gray").pack()
    
    def perform_signup():
        values = {k: v.get().strip() for k, v in entries.items()}
        
        if not all(values.values()):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            success, message = db.signup(
                values['first_name'], values['last_name'], 
                values['username'], values['email'], values['password']
            )
            
            if success:
                messagebox.showinfo("Success", message)
                signup_window.destroy()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Signup failed: {str(e)}")
    
    tk.Button(signup_window, text="Create Account", command=perform_signup,
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

def forgot_password_dialog():
    """Password reset dialog"""
    db = DatabaseManager()
    forgot_window = tk.Toplevel()
    forgot_window.title("Reset Password")
    forgot_window.geometry("400x300")
    forgot_window.grab_set()
    
    tk.Label(forgot_window, text="Reset Password", 
             font=("Arial", 14, "bold")).pack(pady=20)
    
    tk.Label(forgot_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(forgot_window, width=40)
    username_entry.pack(pady=5)
    
    tk.Label(forgot_window, text="New Password:").pack(pady=5)
    password_entry = tk.Entry(forgot_window, width=40, show="*")
    password_entry.pack(pady=5)
    
    def perform_reset():
        username = username_entry.get().strip()
        new_password = password_entry.get()
        
        if not username or not new_password:
            messagebox.showerror("Error", "Username and new password required")
            return
        
        try:
            success, message = db.reset_password(username, new_password)
            if success:
                messagebox.showinfo("Success", message)
                forgot_window.destroy()
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Password reset failed: {str(e)}")
    
    tk.Button(forgot_window, text="Reset Password", command=perform_reset,
              bg="#FF9800", fg="white", font=("Arial", 12)).pack(pady=15)

def encode_smtp_dialog(user_id):
    """SMTP configuration dialog with email validation and connection testing"""
    db = DatabaseManager()
    smtp_window = tk.Toplevel()
    smtp_window.title("SMTP Configuration")
    smtp_window.geometry("500x500")  # Increased height for additional widgets
    smtp_window.grab_set()
    
    # Load saved credentials
    try:
        credentials = db.get_credentials(user_id)
        default_email = credentials[0] if credentials else ""
        default_username = credentials[1] if credentials else ""
        default_password = credentials[2] if credentials else ""
    except:
        default_email = default_username = default_password = ""
    
    tk.Label(smtp_window, text="📧 Email Configuration", 
             font=("Arial", 14, "bold")).pack(pady=15)
    
    # Sender Email
    tk.Label(smtp_window, text="Sender Email (e.g., user@gmail.com):").pack(pady=5)
    sender_entry = tk.Entry(smtp_window, width=50)
    sender_entry.insert(0, default_email)
    sender_entry.pack(pady=2)
    
    sender_status_label = tk.Label(smtp_window, text="", font=("Arial", 9))
    sender_status_label.pack(pady=2)
    
    # SMTP Username
    tk.Label(smtp_window, text="SMTP Username (same as sender email):").pack(pady=(10,5))
    username_entry = tk.Entry(smtp_window, width=50)
    username_entry.insert(0, default_username)
    username_entry.pack(pady=2)
    
    username_status_label = tk.Label(smtp_window, text="", font=("Arial", 9))
    username_status_label.pack(pady=2)
    
    # SMTP Password
    tk.Label(smtp_window, text="SMTP App Password:").pack(pady=(10,5))
    password_entry = tk.Entry(smtp_window, width=50, show="*")
    password_entry.insert(0, default_password)
    password_entry.pack(pady=5)
    
    tk.Button(smtp_window, text="ℹ️ How to get App Password", 
              command=show_password_info, bg="#FFC107", fg="black").pack(pady=5)
    
    # Test Connection Status
    test_status_label = tk.Label(smtp_window, text="", font=("Arial", 9), wraplength=450)
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
        
        # Final validation (redundant but ensures consistency)
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
    button_frame = tk.Frame(smtp_window)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Test Connection", command=test_connection,
              bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    continue_button = tk.Button(button_frame, text="Continue", command=submit_smtp,
                                bg="#4CAF50", fg="white", font=("Arial", 12),
                                state='normal' if continue_button_state.get() else 'disabled')
    continue_button.pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="Cancel", command=smtp_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    
    # Update continue button state dynamically
    def update_continue_button(*args):
        continue_button.config(state='normal' if continue_button_state.get() else 'disabled')
    
    continue_button_state.trace('w', update_continue_button)
    
def encode_data_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Data type selection dialog"""
    encode_window = tk.Toplevel()
    encode_window.title("Select Data Type")
    encode_window.geometry("500x400")
    encode_window.grab_set()
    
    tk.Label(encode_window, text="What would you like to hide?", 
             font=("Arial", 14, "bold")).pack(pady=20)
    
    data_type_var = tk.StringVar(value="message")
    
    tk.Radiobutton(encode_window, text="📝 Text Message", 
                   variable=data_type_var, value="message", 
                   font=("Arial", 12)).pack(pady=8)
    
    tk.Radiobutton(encode_window, text="🖼️ JPG Image", 
                   variable=data_type_var, value="image", 
                   font=("Arial", 12)).pack(pady=8)
    
    tk.Radiobutton(encode_window, text="📄 PDF Document", 
                   variable=data_type_var, value="pdf", 
                   font=("Arial", 12)).pack(pady=8)
    
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
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

def encode_message_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Encode message dialog with audio preview functionality"""
    from audio_player import AudioPreviewWidget
    
    window = tk.Toplevel()
    window.title("Encode Message")
    window.geometry("1000x700")  # Increased height for preview controls
    window.grab_set()
    
    tk.Label(window, text="📝 Encode Text Message", 
             font=("Arial", 14, "bold")).pack(pady=10)
    
    # Message input
    tk.Label(window, text="Message (max 255 characters):").pack(pady=5)
    message_entry = tk.Entry(window, width=60)
    message_entry.pack(pady=5)
    
    # Character counter
    char_label = tk.Label(window, text="0/255", fg="gray")
    char_label.pack()
    
    def update_char_count(*args):
        count = len(message_entry.get())
        char_label.config(text=f"{count}/255", fg="red" if count > 255 else "gray")
    
    message_entry.bind('<KeyRelease>', update_char_count)
    
    # Recipient email
    tk.Label(window, text="Recipient Email:").pack(pady=(15,5))
    recipient_entry = tk.Entry(window, width=60)
    recipient_entry.pack(pady=5)
    
    # Audio file selection
    audio_path_var = tk.StringVar()
    format_info = {}
    
    tk.Label(window, text="Select Audio File (WAV or FLAC):", 
             font=("Arial", 12, "bold")).pack(pady=(15,5))
    
    audio_frame = tk.Frame(window)
    audio_frame.pack(pady=5)
    
    tk.Entry(audio_frame, textvariable=audio_path_var, width=50, 
             state='readonly').pack(side=tk.LEFT, padx=5)
    
    info_label = tk.Label(window, text="No audio file selected", fg="gray")
    info_label.pack(pady=5)
    
    # Status label for audio loading feedback (replaces pop-up messages)
    status_label = tk.Label(window, text="", font=("Arial", 9))
    status_label.pack(pady=2)
    
    # Audio preview widget
    tk.Label(window, text="🎵 Audio Preview:", 
             font=("Arial", 11, "bold")).pack(pady=(10,5))
    
    audio_preview = AudioPreviewWidget(window)
    
    def browse_audio():
        path, info = select_audio_file_dialog("Select Audio File for Message")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            info_label.config(text=show_format_info(info), fg="green")
            
            # Load audio for preview (no pop-up message)
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
              bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
    
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
        if not audio_path:
            status_label.config(text="❌ Please select an audio file", fg="red")
            return
        
        # Clear any previous status messages
        status_label.config(text="", fg="black")
        
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
            tk.Label(progress, text="Encoding message, please wait...", 
                    font=("Arial", 11)).pack(pady=20)
            tk.Label(progress, text="This may take a moment for large files...", 
                    font=("Arial", 9), fg="gray").pack()
            progress.update()
            
            # Encode
            key = encode_data(audio_path, message, output_path, "message", 
                            user_id, message, recipient)
            
            progress.destroy()
            
            # Send email
            send_email(recipient, key, output_path, sender_email, 
                      smtp_username, smtp_password, "message", 
                      format_info['format'], 'lsb')
            
            # Show simple success message (no preview option)
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
    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🎤 Encode & Send", command=perform_encode,
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=cleanup_and_close,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    # Instructions
    instructions_frame = tk.Frame(window, bg="#e8f5e8", relief="groove", bd=1)
    instructions_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(instructions_frame, text="💡 Instructions:", 
             bg="#e8f5e8", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=2)
    tk.Label(instructions_frame, text="1. Select your audio file and preview it to ensure quality", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="2. Enter your message and recipient email", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="3. Click 'Encode & Send' to hide your message in the audio", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0,5))




def preview_encoded_audio(audio_path, audio_format):
    """Show a dedicated audio preview window for encoded files"""
    from audio_player import AudioPreviewWidget
    
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


def encode_image_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Encode image dialog"""
    window = tk.Toplevel()
    window.title("Encode Image")
    window.geometry("650x450")
    window.grab_set()
    
    tk.Label(window, text="🖼️ Encode JPG Image", 
             font=("Arial", 14, "bold")).pack(pady=10)
    
    # Image selection
    image_path_var = tk.StringVar()
    tk.Label(window, text="Select JPG Image:").pack(pady=5)
    
    image_frame = tk.Frame(window)
    image_frame.pack(pady=5)
    
    tk.Entry(image_frame, textvariable=image_path_var, width=50, state='readonly').pack(side=tk.LEFT, padx=5)
    
    image_info_label = tk.Label(window, text="No image selected", fg="gray")
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
    
    tk.Label(window, text="Select Audio File (WAV or FLAC):").pack(pady=(15,5))
    
    audio_frame = tk.Frame(window)
    audio_frame.pack(pady=5)
    
    tk.Entry(audio_frame, textvariable=audio_path_var, width=50, state='readonly').pack(side=tk.LEFT, padx=5)
    
    audio_info_label = tk.Label(window, text="No audio file selected", fg="gray")
    audio_info_label.pack(pady=5)
    
    def browse_audio():
        path, info = select_audio_file_dialog("Select Audio File for Image")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            audio_info_label.config(text=show_format_info(info), fg="green")
        elif info and 'error' in info:
            messagebox.showerror("Audio Error", info['error'])
    
    tk.Button(audio_frame, text="Browse", command=browse_audio,
              bg="#2196F3", fg="white").pack(side=tk.LEFT)
    
    # Recipient email
    tk.Label(window, text="Recipient Email:").pack(pady=(15,5))
    recipient_entry = tk.Entry(window, width=60)
    recipient_entry.pack(pady=5)
    
    def perform_encode():
        image_path = image_path_var.get()
        audio_path = audio_path_var.get()
        recipient = recipient_entry.get().strip()
        
        if not image_path:
            messagebox.showerror("Error", "Please select an image file")
            return
        if not audio_path:
            messagebox.showerror("Error", "Please select an audio file")
            return
        if not recipient:
            messagebox.showerror("Error", "Please enter recipient email")
            return
        
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
            progress.geometry("300x100")
            progress.grab_set()
            tk.Label(progress, text="Encoding image, please wait...", 
                    font=("Arial", 11)).pack(pady=30)
            progress.update()
            
            # Encode
            key = encode_data(audio_path, image_data, output_path, "image", 
                            user_id, image_path, recipient)
            
            progress.destroy()
            
            # Send email
            send_email(recipient, key, output_path, sender_email, 
                      smtp_username, smtp_password, "image", 
                      format_info['format'], 'lsb')
            
            messagebox.showinfo("Success", 
                               f"✅ Image encoded successfully!\n\n"
                               f"Output: {output_filename}\n"
                               f"Format: {format_info['format'].upper()}")
            
            window.destroy()
            
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            messagebox.showerror("Encoding Failed", str(e))
    
    # Buttons
    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Encode & Send", command=perform_encode,
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cancel", command=window.destroy,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

def encode_pdf_dialog(user_id, sender_email, smtp_username, smtp_password):
    """Encode PDF dialog"""
    window = tk.Toplevel()
    window.title("Encode PDF")
    window.geometry("650x450")
    window.grab_set()
    
    tk.Label(window, text="📄 Encode PDF Document", 
             font=("Arial", 14, "bold")).pack(pady=10)
    
    # PDF selection
    pdf_path_var = tk.StringVar()
    tk.Label(window, text="Select PDF Document:").pack(pady=5)
    
    pdf_frame = tk.Frame(window)
    pdf_frame.pack(pady=5)
    
    tk.Entry(pdf_frame, textvariable=pdf_path_var, width=50, state='readonly').pack(side=tk.LEFT, padx=5)
    
    pdf_info_label = tk.Label(window, text="No PDF selected", fg="gray")
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
    
    tk.Label(window, text="Select Audio File (WAV or FLAC):").pack(pady=(15,5))
    
    audio_frame = tk.Frame(window)
    audio_frame.pack(pady=5)
    
    tk.Entry(audio_frame, textvariable=audio_path_var, width=50, state='readonly').pack(side=tk.LEFT, padx=5)
    
    audio_info_label = tk.Label(window, text="No audio file selected", fg="gray")
    audio_info_label.pack(pady=5)
    
    def browse_audio():
        path, info = select_audio_file_dialog("Select Audio File for PDF")
        if path and info and 'error' not in info:
            audio_path_var.set(path)
            format_info.clear()
            format_info.update(info)
            audio_info_label.config(text=show_format_info(info), fg="green")
        elif info and 'error' in info:
            messagebox.showerror("Audio Error", info['error'])
    
    tk.Button(audio_frame, text="Browse", command=browse_audio,
              bg="#2196F3", fg="white").pack(side=tk.LEFT)
    
    # Recipient email
    tk.Label(window, text="Recipient Email:").pack(pady=(15,5))
    recipient_entry = tk.Entry(window, width=60)
    recipient_entry.pack(pady=5)
    
    def perform_encode():
        pdf_path = pdf_path_var.get()
        audio_path = audio_path_var.get()
        recipient = recipient_entry.get().strip()
        
        if not pdf_path:
            messagebox.showerror("Error", "Please select a PDF file")
            return
        if not audio_path:
            messagebox.showerror("Error", "Please select an audio file")
            return
        if not recipient:
            messagebox.showerror("Error", "Please enter recipient email")
            return
        
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
            progress.geometry("300x100")
            progress.grab_set()
            tk.Label(progress, text="Encoding PDF, please wait...", 
                    font=("Arial", 11)).pack(pady=30)
            progress.update()
            
            # Encode
            key = encode_data(audio_path, pdf_data, output_path, "pdf", 
                            user_id, pdf_path, recipient)
            
            progress.destroy()
            
            # Send email
            send_email(recipient, key, output_path, sender_email, 
                      smtp_username, smtp_password, "pdf", 
                      format_info['format'], 'lsb')
            
            messagebox.showinfo("Success", 
                               f"✅ PDF encoded successfully!\n\n"
                               f"Output: {output_filename}\n"
                               f"Format: {format_info['format'].upper()}")
            
            window.destroy()
            
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            messagebox.showerror("Encoding Failed", str(e))
    
    # Buttons
    button_frame = tk.Frame(window)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Encode & Send", command=perform_encode,
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cancel", command=window.destroy,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

def decode_dialog(user_id):
    """Decode dialog with audio preview functionality and email verification"""
    from audio_player import AudioPreviewWidget
    
    decode_window = tk.Toplevel()
    decode_window.title("Decode Audio File")
    decode_window.geometry("1000x700")
    decode_window.grab_set()
    
    tk.Label(decode_window, text="🔍 Decode Audio File", 
             font=("Arial", 14, "bold")).pack(pady=15)
    
    # Data type selection
    tk.Label(decode_window, text="What type of data is hidden?", 
             font=("Arial", 12)).pack(pady=10)
    data_type_var = tk.StringVar(value="message")
    
    type_frame = tk.Frame(decode_window)
    type_frame.pack(pady=5)
    
    tk.Radiobutton(type_frame, text="📝 Text Message", variable=data_type_var, 
                   value="message", font=("Arial", 10)).pack(side=tk.LEFT, padx=15)
    tk.Radiobutton(type_frame, text="🖼️ JPG Image", variable=data_type_var, 
                   value="image", font=("Arial", 10)).pack(side=tk.LEFT, padx=15)
    tk.Radiobutton(type_frame, text="📄 PDF Document", variable=data_type_var, 
                   value="pdf", font=("Arial", 10)).pack(side=tk.LEFT, padx=15)
    
    # Key input
    tk.Label(decode_window, text="Decryption Key:", font=("Arial", 12)).pack(pady=(20,5))
    key_entry = tk.Entry(decode_window, width=70)
    key_entry.pack(pady=5)
    
    # Audio file selection
    audio_path_var = tk.StringVar()
    format_info = {}
    
    tk.Label(decode_window, text="Select Encoded Audio File (WAV or FLAC):", 
             font=("Arial", 12, "bold")).pack(pady=(20,5))
    
    file_frame = tk.Frame(decode_window)
    file_frame.pack(pady=5)
    
    tk.Entry(file_frame, textvariable=audio_path_var, width=50, 
             state='readonly').pack(side=tk.LEFT, padx=5)
    
    file_info_label = tk.Label(decode_window, text="No audio file selected", fg="gray")
    file_info_label.pack(pady=5)
    
    # Status label for audio loading feedback
    status_label = tk.Label(decode_window, text="", font=("Arial", 9))
    status_label.pack(pady=2)
    
    # Audio preview widget
    tk.Label(decode_window, text="🎵 Audio Preview:", 
             font=("Arial", 11, "bold")).pack(pady=(10,5))
    
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
              bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
    
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
        status_label.config(text="", fg="black")
        
        try:
            # Validate key format
            key_bytes = key_str.encode()
            from cryptography.fernet import Fernet
            Fernet(key_bytes)  # This will raise an exception if key is invalid
            
            # Show progress
            progress = tk.Toplevel(decode_window)
            progress.title("Decoding...")
            progress.geometry("300x100")
            progress.grab_set()
            tk.Label(progress, text=f"Decoding {data_type}, please wait...", 
                    font=("Arial", 11)).pack(pady=30)
            progress.update()
            
            # Decode
            result = decode_data(audio_path, key_bytes, data_type, user_id)
            
            progress.destroy()
            
            # Show result
            format_name = format_info.get('format', 'audio').upper()
            
            if data_type == "message":
                messagebox.showinfo("Decoded Message", 
                                  f"✅ Successfully decoded from {format_name}!\n\n"
                                  f"📝 Message: {result}")
            elif data_type == "image":
                messagebox.showinfo("Decoded Image", 
                                  f"✅ Successfully decoded from {format_name}!\n\n"
                                  f"🖼️ Image saved to: {os.path.basename(result)}")
            elif data_type == "pdf":
                messagebox.showinfo("Decoded PDF", 
                                  f"✅ Successfully decoded from {format_name}!\n\n"
                                  f"📄 PDF saved to: {os.path.basename(result)}")
            
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
            else:
                status_label.config(text=f"❌ Decoding failed: {str(e)}", fg="red")
                
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            status_label.config(text=f"❌ Decoding error: {str(e)}", fg="red")
    
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
    button_frame = tk.Frame(decode_window)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🔓 Decode", command=perform_decode, 
              bg="#FF9800", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=cleanup_and_close,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    # Instructions
    instructions_frame = tk.Frame(decode_window, bg="#e8f5e8", relief="groove", bd=1)
    instructions_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(instructions_frame, text="💡 Instructions:", 
             bg="#e8f5e8", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=2)
    tk.Label(instructions_frame, text="1. Select your encoded audio file and preview it if needed", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="2. Enter the decryption key provided during encoding", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="3. Choose the correct data type and click 'Decode'", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15)
    tk.Label(instructions_frame, text="4. Note: You must be logged in with the recipient email", 
             bg="#e8f5e8", font=("Arial", 9)).pack(anchor="w", padx=15, pady=(0,5))


def history_dialog(user_id):
    """Enhanced history dialog with separate encoded/decoded sections and download options"""
    db = DatabaseManager()
    history_window = tk.Toplevel()
    history_window.title("Operation History")
    history_window.geometry("1200x600")
    history_window.grab_set()
    
    tk.Label(history_window, text="📚 Your Audio Steganography History", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    # Create notebook for tabs
    notebook = ttk.Notebook(history_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Encoded Data Tab
    encoded_frame = ttk.Frame(notebook)
    notebook.add(encoded_frame, text="📤 Encoded Data")
    
    # Decoded Data Tab
    decoded_frame = ttk.Frame(notebook)
    notebook.add(decoded_frame, text="📥 Decoded Data")
    
    # Create encoded data view
    create_encoded_view(encoded_frame, user_id, db)
    
    # Create decoded data view
    create_decoded_view(decoded_frame, user_id, db)
    
    # Control buttons
    button_frame = tk.Frame(history_window)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="🔄 Refresh All", 
              command=lambda: refresh_all_views(),
              bg="#2196F3", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="📊 Export All Data", 
              command=lambda: export_user_data_dialog(user_id),
              bg="#4CAF50", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="❌ Close", 
              command=history_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def refresh_all_views():
        # Refresh both tabs
        for widget in encoded_frame.winfo_children():
            widget.destroy()
        for widget in decoded_frame.winfo_children():
            widget.destroy()
        
        create_encoded_view(encoded_frame, user_id, db)
        create_decoded_view(decoded_frame, user_id, db)


def create_encoded_view(parent_frame, user_id, db):
    """Create the encoded data view"""
    tk.Label(parent_frame, text="📤 Encoded Data Records", 
             font=("Arial", 12, "bold")).pack(pady=5)
    
    # Create treeview for encoded data
    columns = ("ID", "Data Type", "Audio Format", "Input File", "Audio Used", 
               "Output File", "Recipient Email", "Date", "Size (MB)")
    
    encoded_tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=15)
    encoded_tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Configure columns
    column_widths = {
        "ID": 50, "Data Type": 80, "Audio Format": 80, "Input File": 120,
        "Audio Used": 120, "Output File": 120, "Recipient Email": 150,
        "Date": 130, "Size (MB)": 80
    }
    
    for col in columns:
        encoded_tree.heading(col, text=col)
        encoded_tree.column(col, width=column_widths.get(col, 100))
    
    # Scrollbars
    v_scroll_enc = ttk.Scrollbar(parent_frame, orient="vertical", command=encoded_tree.yview)
    v_scroll_enc.pack(side="right", fill="y")
    encoded_tree.configure(yscrollcommand=v_scroll_enc.set)
    
    # Load encoded data
    load_encoded_data(encoded_tree, user_id, db)
    
    # Bind events
    encoded_tree.bind("<Button-3>", lambda e: show_encoded_context_menu(e, encoded_tree, user_id, db))
    encoded_tree.bind("<Double-1>", lambda e: download_complete_record(encoded_tree, user_id, db, "encoded"))


def create_decoded_view(parent_frame, user_id, db):
    """Create the decoded data view"""
    tk.Label(parent_frame, text="📥 Decoded Data Records", 
             font=("Arial", 12, "bold")).pack(pady=5)
    
    # Create treeview for decoded data
    columns = ("ID", "Data Type", "Audio Format", "Input Audio", "Decryption Key", 
               "Output File", "Date", "Success")
    
    decoded_tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=15)
    decoded_tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Configure columns
    column_widths = {
        "ID": 50, "Data Type": 80, "Audio Format": 80, "Input Audio": 150,
        "Decryption Key": 200, "Output File": 150, "Date": 130, "Success": 70
    }
    
    for col in columns:
        decoded_tree.heading(col, text=col)
        decoded_tree.column(col, width=column_widths.get(col, 100))
    
    # Scrollbars
    v_scroll_dec = ttk.Scrollbar(parent_frame, orient="vertical", command=decoded_tree.yview)
    v_scroll_dec.pack(side="right", fill="y")
    decoded_tree.configure(yscrollcommand=v_scroll_dec.set)
    
    # Load decoded data
    load_decoded_data(decoded_tree, user_id, db)
    
    # Bind events
    decoded_tree.bind("<Button-3>", lambda e: show_decoded_context_menu(e, decoded_tree, user_id, db))
    decoded_tree.bind("<Double-1>", lambda e: download_complete_record(decoded_tree, user_id, db, "decoded"))


def load_encoded_data(tree, user_id, db):
    """Load encoded data into the tree"""
    try:
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Get encoded records
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT id, data_type, audio_format, input_file_path, audio_file_path,
                   output_file_path, receiver_email, operation_date, file_size_mb
            FROM history 
            WHERE user_id = ? AND operation = 'encode'
            ORDER BY operation_date DESC
        ''', (user_id,))
        
        records = cursor.fetchall()
        
        for record in records:
            display_record = (
                record[0],  # ID
                record[1],  # Data Type
                record[2] or "Unknown",  # Audio Format
                os.path.basename(record[3]) if record[3] else "N/A",  # Input File
                os.path.basename(record[4]) if record[4] else "N/A",  # Audio Used
                os.path.basename(record[5]) if record[5] else "N/A",  # Output File
                record[6] or "N/A",  # Recipient Email
                record[7][:16] if record[7] else "N/A",  # Date (truncated)
                f"{record[8]:.2f}" if record[8] else "N/A"  # Size (MB)
            )
            tree.insert("", "end", values=display_record)
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load encoded data: {str(e)}")


def load_decoded_data(tree, user_id, db):
    """Load decoded data into the tree"""
    try:
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Get decoded records
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT id, data_type, audio_format, audio_file_path, decryption_key,
                   output_file_path, operation_date, success
            FROM history 
            WHERE user_id = ? AND operation = 'decode'
            ORDER BY operation_date DESC
        ''', (user_id,))
        
        records = cursor.fetchall()
        
        for record in records:
            display_record = (
                record[0],  # ID
                record[1],  # Data Type
                record[2] or "Unknown",  # Audio Format
                os.path.basename(record[3]) if record[3] else "N/A",  # Input Audio
                record[4][:20] + "..." if record[4] and len(record[4]) > 20 else record[4] or "N/A",  # Key (truncated)
                os.path.basename(record[5]) if record[5] else "N/A",  # Output File
                record[6][:16] if record[6] else "N/A",  # Date (truncated)
                "✅ Success" if record[7] else "❌ Failed"  # Success
            )
            tree.insert("", "end", values=display_record)
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load decoded data: {str(e)}")


def show_encoded_context_menu(event, tree, user_id, db):
    """Show context menu for encoded records"""
    try:
        item = tree.selection()[0]
        values = tree.item(item, "values")
        record_id = values[0]
        
        context_menu = tk.Menu(tree, tearoff=0)
        
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="📄 Download Input File",
            command=lambda: download_specific_file(record_id, user_id, db, "input")
        )
        
        context_menu.add_command(
            label="🎵 Download Audio File",
            command=lambda: download_specific_file(record_id, user_id, db, "audio")
        )
        
        context_menu.add_command(
            label="📤 Download Output File",
            command=lambda: download_specific_file(record_id, user_id, db, "output")
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="📧 Copy Recipient Email",
            command=lambda: copy_to_clipboard(get_record_detail(record_id, user_id, db, "receiver_email"))
        )
        
        context_menu.add_command(
            label="🔑 Copy Decryption Key",
            command=lambda: copy_to_clipboard(get_record_detail(record_id, user_id, db, "decryption_key"))
        )
        
        context_menu.add_separator()
        
       
        
        context_menu.add_command(
            label="🗑️ Delete Record",
            command=lambda: delete_record_with_confirmation(record_id, user_id, db, tree, "encoded")
        )
        
        context_menu.post(event.x_root, event.y_root)
        
    except IndexError:
        pass  # No item selected
    except Exception as e:
        messagebox.showerror("Error", f"Context menu error: {str(e)}")


def show_decoded_context_menu(event, tree, user_id, db):
    """Show context menu for decoded records"""
    try:
        item = tree.selection()[0]
        values = tree.item(item, "values")
        record_id = values[0]
        
        context_menu = tk.Menu(tree, tearoff=0)
        
       
        
        
        context_menu.add_command(
            label="🎵 Download Input Audio",
            command=lambda: download_specific_file(record_id, user_id, db, "audio")
        )
        
        context_menu.add_command(
            label="📤 Download Output File",
            command=lambda: download_specific_file(record_id, user_id, db, "output")
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="🔑 Copy Decryption Key",
            command=lambda: copy_to_clipboard(get_record_detail(record_id, user_id, db, "decryption_key"))
        )
        
        context_menu.add_separator()
        
        
        context_menu.add_command(
            label="🗑️ Delete Record",
            command=lambda: delete_record_with_confirmation(record_id, user_id, db, tree, "decoded")
        )
        
        context_menu.post(event.x_root, event.y_root)
        
    except IndexError:
        pass  # No item selected
    except Exception as e:
        messagebox.showerror("Error", f"Context menu error: {str(e)}")


def download_complete_record(tree, user_id, db, record_type):
    """Download complete record as ZIP file"""
    try:
        if not tree.selection():
            messagebox.showwarning("Warning", "Please select a record first")
            return
        
        item = tree.selection()[0]
        values = tree.item(item, "values")
        record_id = values[0]
        
        # Get complete record details
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT * FROM history WHERE id = ? AND user_id = ?
        ''', (record_id, user_id))
        
        record = cursor.fetchone()
        if not record:
            messagebox.showerror("Error", "Record not found")
            return
        
        # Ask user where to save
        import tkinter.filedialog as fd
        save_path = fd.asksaveasfilename(
            title="Save Complete Record",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialname=f"{record_type}_record_{record_id}_{record[2]}_{int(time.time())}.zip"
        )
        
        if not save_path:
            return
        
        # Create ZIP file with all available files
        import zipfile
        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            files_added = 0
            
            # Add record info as text file
            info_content = create_record_info_text(record)
            zipf.writestr(f"record_info_{record_id}.txt", info_content)
            files_added += 1
            
            # Add actual files if they exist
            file_paths = [
                (record[7], "input_file"),      # input_file_path
                (record[8], "audio_file"),      # audio_file_path
                (record[9], "output_file")      # output_file_path
            ]
            
            for file_path, file_type in file_paths:
                if file_path and os.path.exists(file_path):
                    try:
                        zipf.write(file_path, f"{file_type}_{os.path.basename(file_path)}")
                        files_added += 1
                    except Exception as e:
                        print(f"Could not add {file_path}: {e}")
        
        messagebox.showinfo("Success", 
                          f"✅ Complete record downloaded!\n\n"
                          f"📦 File: {os.path.basename(save_path)}\n"
                          f"📁 Files included: {files_added}\n"
                          f"💾 Saved to: {save_path}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Download failed: {str(e)}")


def download_specific_file(record_id, user_id, db, file_type):
    """Download the input message as .txt, or the input/audio/output file to chosen location."""
    import tkinter.filedialog as fd
    import shutil
    try:
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT input_file_path, audio_file_path, output_file_path, data_type
            FROM history WHERE id = ? AND user_id = ?
        ''', (record_id, user_id))
        record = cursor.fetchone()
        if not record:
            messagebox.showerror("Error", "Record not found")
            return

        file_map = {
            "input": (record[0], "Input"),
            "audio": (record[1], "Audio"),
            "output": (record[2], "Output")
        }
        file_path, file_desc = file_map.get(file_type, (None, None))

        if not file_path:
            messagebox.showwarning("Warning", f"No {file_desc} file path recorded")
            return

        # Handle message-input (not a file, it's the text itself)
        if file_type == "input" and record[3] == "message":
            save_path = fd.asksaveasfilename(
                title="Save Message as Text File",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"message_input_{record_id}.txt"
            )
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(file_path)
                messagebox.showinfo("Success", f"✅ Message saved to {save_path}")
            return

        # File (audio, output, or image/pdf input) case
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"{file_desc} file not found:\n{file_path}")
            return

        save_path = fd.asksaveasfilename(
            title=f"Save {file_desc} File",
            initialfile=os.path.basename(file_path)
        )
        if not save_path:
            return

        shutil.copy2(file_path, save_path)
        messagebox.showinfo("Success",
            f"✅ {file_desc} file downloaded!\n\n"
            f"📁 Original: {os.path.basename(file_path)}\n"
            f"💾 Saved to: {save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Download failed: {str(e)}")



def get_record_detail(record_id, user_id, db, field):
    """Get specific field from a record"""
    try:
        cursor = db.conn.cursor()
        cursor.execute(f'SELECT {field} FROM history WHERE id = ? AND user_id = ?', 
                      (record_id, user_id))
        result = cursor.fetchone()
        return result[0] if result else ""
    except:
        return ""


def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(str(text) if text else "")
        root.update()
        root.destroy()
        messagebox.showinfo("Copied", "Text copied to clipboard!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy: {str(e)}")


def show_record_details(record_id, user_id, db):
    """Show detailed information about a record"""
    try:
        cursor = db.conn.cursor()
        cursor.execute('SELECT * FROM history WHERE id = ? AND user_id = ?', 
                      (record_id, user_id))
        record = cursor.fetchone()
        
        if not record:
            messagebox.showerror("Error", "Record not found")
            return
        
        details_window = tk.Toplevel()
        details_window.title(f"Record Details - ID {record_id}")
        details_window.geometry("800x600")
        details_window.grab_set()
        
        # Create scrollable text widget
        text_frame = tk.Frame(details_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Courier", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Create detailed information
        details_text = create_record_info_text(record)
        text_widget.insert("1.0", details_text)
        text_widget.configure(state="disabled")
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(details_window, text="Close", command=details_window.destroy,
                 bg="#f44336", fg="white").pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to show details: {str(e)}")


def create_record_info_text(record):
    """Create formatted text information for a record"""
    column_names = [
        "ID", "User ID", "Operation", "Data Type", "Audio Format", "Audio Codec",
        "Steganography Method", "Input File Path", "Audio File Path", "Output File Path",
        "Receiver Email", "Decryption Key", "File Size (MB)", "Processing Time (s)",
        "Success", "Error Message", "Operation Date"
    ]
    
    details = f"""AUDIO STEGANOGRAPHY RECORD DETAILS
{'='*60}

"""
    
    for i, value in enumerate(record):
        if i < len(column_names):
            field_name = column_names[i]
            field_value = value if value is not None else "N/A"
            
            # Format specific fields
            if field_name == "Success":
                field_value = "✅ Yes" if value else "❌ No"
            elif field_name == "File Size (MB)" and value:
                field_value = f"{value:.2f} MB"
            elif field_name == "Processing Time (s)" and value:
                field_value = f"{value:.2f} seconds"
            
            details += f"{field_name:<25}: {field_value}\n"
    
    details += f"\n{'='*60}\n"
    details += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return details


def delete_record_with_confirmation(record_id, user_id, db, tree, record_type):
    """Delete record with confirmation"""
    try:
        # Get record details for confirmation
        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT operation, data_type, operation_date 
            FROM history WHERE id = ? AND user_id = ?
        ''', (record_id, user_id))
        
        record = cursor.fetchone()
        if not record:
            messagebox.showerror("Error", "Record not found")
            return
        
        # Confirmation dialog
        confirm_msg = (f"Are you sure you want to delete this record?\n\n"
                      f"🔹 Operation: {record[0].title()}\n"
                      f"🔹 Data Type: {record[1].title()}\n"
                      f"🔹 Date: {record[2]}\n\n"
                      f"⚠️ This action cannot be undone!")
        
        if messagebox.askyesno("Confirm Deletion", confirm_msg):
            success, message = db.delete_history(record_id, user_id)
            
            if success:
                messagebox.showinfo("Success", "✅ Record deleted successfully")
                
                # Refresh the tree
                if record_type == "encoded":
                    load_encoded_data(tree, user_id, db)
                else:
                    load_decoded_data(tree, user_id, db)
            else:
                messagebox.showerror("Error", f"Failed to delete record: {message}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Delete failed: {str(e)}")


def export_user_data_dialog(user_id):
    """Dialog for exporting all user data"""
    db = DatabaseManager()
    
    export_window = tk.Toplevel()
    export_window.title("Export User Data")
    export_window.geometry("400x300")
    export_window.grab_set()
    
    tk.Label(export_window, text="📊 Export Your Complete Data", 
             font=("Arial", 14, "bold")).pack(pady=20)
    
    # Export format selection
    tk.Label(export_window, text="Select Export Format:").pack(pady=5)
    format_var = tk.StringVar(value="csv")
    
    tk.Radiobutton(export_window, text="📊 CSV Format (Excel compatible)", 
                   variable=format_var, value="csv").pack(pady=5)
    tk.Radiobutton(export_window, text="📄 JSON Format (Complete data)", 
                   variable=format_var, value="json").pack(pady=5)
    
    # Include logs option
    include_logs_var = tk.BooleanVar()
    tk.Checkbutton(export_window, text="📝 Include detailed logs", 
                   variable=include_logs_var).pack(pady=10)
    
    def perform_export():
        try:
            export_format = format_var.get()
            include_logs = include_logs_var.get()
            
            # Show progress
            progress = tk.Toplevel(export_window)
            progress.title("Exporting...")
            progress.geometry("300x100")
            progress.grab_set()
            tk.Label(progress, text="Exporting your data, please wait...", 
                    font=("Arial", 11)).pack(pady=30)
            progress.update()
            
            # Export data
            success, message, files = db.export_user_data(user_id, export_format, include_logs)
            
            progress.destroy()
            
            if success:
                messagebox.showinfo("Export Complete", 
                                  f"✅ {message}\n\n"
                                  f"📁 Files created: {len(files)}\n"
                                  f"💾 Location: Exports folder")
                export_window.destroy()
            else:
                messagebox.showerror("Export Failed", message)
                
        except Exception as e:
            if 'progress' in locals():
                try:
                    progress.destroy()
                except:
                    pass
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    tk.Button(export_window, text="📤 Export Data", command=perform_export,
              bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)
    
    tk.Button(export_window, text="Cancel", command=export_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 10)).pack(pady=5)


def main_app(user_id, master_root=None):
    """Main application window that acts as master after login"""
    if master_root:
        app_window = tk.Toplevel(master_root)
    else:
        app_window = tk.Toplevel()
    
    app_window.title("Audio Steganography (WAV & FLAC)")
    app_window.geometry("800x600")
    app_window.grab_set()
    
    # Make this window visible and bring to front
    app_window.deiconify()
    app_window.lift()
    app_window.focus_force()
    
    tk.Label(app_window, text="🎵 Audio Steganography", 
             font=("Arial", 18, "bold"), fg="#1976D2").pack(pady=20)
    
    tk.Label(app_window, text="Hide messages, images, or PDF documents in audio files", 
             font=("Arial", 11), fg="#666").pack(pady=5)
    
    # Supported formats info
    format_frame = tk.Frame(app_window, bg="#f0f0f0", relief="ridge", bd=2)
    format_frame.pack(pady=15, padx=30, fill="x")
    
    tk.Label(format_frame, text="📊 SUPPORTED FORMATS & FEATURES", 
             bg="#f0f0f0", font=("Arial", 11, "bold")).pack(pady=5)
    tk.Label(format_frame, text="🎵 Audio: WAV (16-bit PCM) • FLAC (Lossless)", 
             bg="#f0f0f0", font=("Arial", 9)).pack()
    tk.Label(format_frame, text="📄 Data: Text Messages • JPG Images • PDF Documents", 
             bg="#f0f0f0", font=("Arial", 9)).pack()
    tk.Label(format_frame, text="🔒 Method: LSB Steganography (Perfect Quality)", 
             bg="#f0f0f0", font=("Arial", 9), fg="#2E7D32").pack(pady=(0,5))
    
    tk.Label(app_window, text="Choose an Action:", font=("Arial", 12, "bold")).pack(pady=(20,10))
    
    # Action buttons
    tk.Button(app_window, text="🎤 Encode Data in Audio", 
              command=lambda: encode_smtp_dialog(user_id),
              width=25, height=2, bg="#4CAF50", fg="white", 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    tk.Button(app_window, text="🔍 Decode Audio File", 
              command=lambda: decode_dialog(user_id),
              width=25, height=2, bg="#FF9800", fg="white", 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    tk.Button(app_window, text="📚 View History", 
              command=lambda: history_dialog(user_id),
              width=25, height=2, bg="#2196F3", fg="white", 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    # Status info
    status_frame = tk.Frame(app_window, bg="#e8f5e8", relief="groove", bd=1)
    status_frame.pack(pady=20, padx=30, fill="x")
    
    tk.Label(status_frame, text="ℹ️ QUALITY & COMPATIBILITY", 
             bg="#e8f5e8", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Label(status_frame, text="✅ Perfect audio quality preservation with LSB method", 
             bg="#e8f5e8", font=("Arial", 8)).pack()
    tk.Label(status_frame, text="🔄 Supports both encoding and decoding operations", 
             bg="#e8f5e8", font=("Arial", 8)).pack()
    tk.Label(status_frame, text="🔐 AES-256 encryption for maximum security", 
             bg="#e8f5e8", font=("Arial", 8)).pack(pady=(0,5))
    
    return app_window  # Return the window reference