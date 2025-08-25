import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from tkinter import messagebox
from datetime import datetime


def send_email(receiver_email, key, audio_path, sender_email, smtp_username, smtp_password, 
               data_type="message", audio_format=None, steganography_method=None, custom_body=None):
    """Enhanced email sending with custom body support for informative emails"""
    
    # Simple subject line
    format_text = f" ({audio_format.upper()})" if audio_format else ""
    subject = f"The Key and Encoded Audio{format_text} ({data_type})"
    
    # Use custom body if provided, otherwise use default message
    if custom_body:
        message = f"""{custom_body}

═══════════════════════════════════════════════════════════════════

🔑 DECRYPTION KEY:
{key.decode()}

═══════════════════════════════════════════════════════════════════

Technical Details:
• Audio Format: {audio_format.upper() if audio_format else 'Unknown'}
• Method: {steganography_method.upper() if steganography_method else 'LSB'}
• Encoded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Keep this key safe and secure!
"""
    else:
        # Default message (original functionality)
        message = f"""The Key for Encoded Audio with hidden {data_type} is:


{key.decode()}


INSTRUCTIONS:
1. Save the attached audio file
2. Open the Audio Steganography application
3. Select "Decode Audio File"
4. Choose "{data_type}" as the data type
5. Enter the key above
6. Select the saved audio file
7. Click "Decode"


Audio Format: {audio_format.upper() if audio_format else 'Unknown'}
Method: {steganography_method.upper() if steganography_method else 'LSB'}
Encoded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


Keep this key safe and secure!
"""
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    # Attach audio file (same as your working code)
    try:
        with open(audio_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(audio_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(audio_path)}"'
            msg.attach(part)
    except OSError as e:
        messagebox.showerror("Error", f"Failed to attach audio file: {str(e)}")
        raise
    
    # Send email (exactly like your working code)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        # Enhanced success message
        success_msg = "Email sent successfully!"
        if audio_format:
            success_msg += f"\n\nEncoded {data_type} in {audio_format.upper()} format sent to {receiver_email}"
        
        messagebox.showinfo("Success", success_msg)
        
    except smtplib.SMTPException as e:
        messagebox.showerror("Error", f"Failed to send email: {str(e)}")
        raise


def send_data_export_email(receiver_email, export_files, sender_email, smtp_username, smtp_password, export_format):
    """Send data export using the same reliable method"""
    
    subject = f"Your Audio Steganography Data Export ({export_format.upper()})"
    
    message = f"""Your account data export is attached.


Export Format: {export_format.upper()}
Files: {len(export_files)}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


This data contains your complete steganography history and settings.
Keep these files secure.
"""
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    # Attach all export files
    try:
        for file_path in export_files:
            with open(file_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)
    except OSError as e:
        messagebox.showerror("Error", f"Failed to attach export files: {str(e)}")
        return False
    
    # Send using the same reliable method
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        messagebox.showinfo("Export Sent", f"Data export sent successfully to {receiver_email}!")
        return True
        
    except smtplib.SMTPException as e:
        messagebox.showerror("Export Send Failed", f"Failed to send export: {str(e)}")
        return False


def show_password_info():
    """Your working password info (unchanged)"""
    info_text = (
        "How to get SMTP Password (for Gmail):\n"
        "1. Go to your Google Account settings > Security.\n"
        "2. Enable 2-Step Verification if not already.\n"
        "3. Search for 'App passwords'.\n"
        "4. Generate a password for 'Mail' on your device.\n"
        "5. Copy the 16-character code (no spaces) and paste here.\n"
        "Note: If spaces appear, remove them."
    )
    messagebox.showinfo("SMTP Password Guide", info_text)


def get_file_size_info(file_path):
    """Simple file size helper"""
    if not file_path or not os.path.exists(file_path):
        return "Unknown"
    
    try:
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    except:
        return "Unknown"


def validate_email_address(email):
    """Simple email validation"""
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return True, "Valid email address"
    return False, "Invalid email format"


def test_smtp_connection(smtp_username, smtp_password, sender_email):
    """Test SMTP connection using the working method"""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.quit()
        return True, "SMTP connection successful!"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Check your email and app password."
    except smtplib.SMTPConnectError:
        return False, "Could not connect to Gmail SMTP server."
    except Exception as e:
        return False, f"Connection test failed: {str(e)}"
