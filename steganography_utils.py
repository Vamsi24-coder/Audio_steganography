# steganography_utils.py
import os
import numpy as np
from cryptography.fernet import Fernet, InvalidToken
from audio_format_handler import AudioFormatHandler
from database import DatabaseManager
from PIL import Image
import PyPDF2
import hashlib
from datetime import datetime
import subprocess
import tempfile
import shutil
# Add this at the top of steganography_utils.py
import bcrypt


def validate_image_file(file_path):
    """Validate JPG image file"""
    try:
        with Image.open(file_path) as img:
            if img.format.lower() not in ['jpeg', 'jpg']:
                return False, "File is not a JPG image"
            return True, "Valid JPG image"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def validate_pdf_file(file_path):
    """Validate PDF file"""
    try:
        with open(file_path, 'rb') as file:
            header = file.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "File is not a valid PDF"
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            if page_count == 0:
                return False, "PDF file is empty"
        
        return True, f"Valid PDF with {page_count} pages"
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0

def estimate_audio_duration_needed(data_size_bytes, format_info=None):
    """Estimate required audio duration"""
    samples_needed = data_size_bytes * 8  # 8 bits per byte for LSB
    sample_rate = format_info.get('sample_rate', 44100) if format_info else 44100
    return (samples_needed / sample_rate) / 60  # minutes

def _embed_lsb(pcm_data, data_bytes):
    """Embed data in PCM using LSB - ENHANCED version with better reliability"""
    data_length = len(data_bytes)
    required_samples = 32 + data_length * 8
    
    if len(pcm_data) < required_samples:
        raise ValueError(f"Audio too small: need {required_samples} samples, have {len(pcm_data)}")
    
    # Ensure correct data type
    if pcm_data.dtype != np.int16:
        pcm_data = pcm_data.astype(np.int16)
    
    # Create copy to avoid modifying original
    modified_pcm = pcm_data.copy()
    
    # Use unsigned view to prevent overflow
    pcm_uint16 = modified_pcm.view(np.uint16)
    
    # Embed length (32 bits, MSB first)
    for i in range(32):
        bit = (data_length >> (31 - i)) & 1
        pcm_uint16[i] = (pcm_uint16[i] & 0xFFFE) | bit
    
    # Embed data
    index = 32
    for byte in data_bytes:
        for j in range(8):
            bit = (byte >> (7 - j)) & 1
            pcm_uint16[index] = (pcm_uint16[index] & 0xFFFE) | bit
            index += 1
    
    # Return as signed int16
    return pcm_uint16.view(np.int16)

def _extract_lsb(pcm_data):
    """Extract data from PCM using LSB - ENHANCED version with better error handling"""
    if len(pcm_data) < 32:
        raise ValueError("Audio too small to contain data")
    
    # Ensure correct data type
    if pcm_data.dtype != np.int16:
        pcm_data = pcm_data.astype(np.int16)
    
    # Use unsigned view for consistent bit operations
    pcm_uint16 = pcm_data.view(np.uint16)
    
    # Extract length (32 bits, MSB first)
    data_length = 0
    for i in range(32):
        bit = pcm_uint16[i] & 1
        data_length = (data_length << 1) | bit
    
    if data_length <= 0 or data_length > 10000000:  # Sanity check
        raise ValueError(f"Invalid data length extracted: {data_length}")
    
    if len(pcm_data) < 32 + data_length * 8:
        raise ValueError(f"Audio too small for declared data length: {data_length}")
    
    # Extract data
    data_bytes = bytearray()
    index = 32
    for _ in range(data_length):
        byte = 0
        for _ in range(8):
            bit = pcm_uint16[index] & 1
            byte = (byte << 1) | bit
            index += 1
        data_bytes.append(byte)
    
    return bytes(data_bytes)

def create_user_default_folder(user_id):
    """Create user-specific default folder for non-secure saves"""
    db = DatabaseManager()
    user_details = db.get_user_details(user_id)
    username = user_details['user_info']['username']
    
    user_folder = os.path.join("UserData", f"user_{username}_{user_id}")
    images_dir = os.path.join(user_folder, "Images")
    pdfs_dir = os.path.join(user_folder, "PDFs")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(pdfs_dir, exist_ok=True)
    
    return user_folder, images_dir, pdfs_dir

# ===== COMPLETE 7-ZIP ARCHIVE FUNCTIONS =====

def create_encrypted_7z_directly(folder_path, archive_path, password, folder_name):
    """Create encrypted .7z archive directly from folder using py7zr or 7-Zip command line"""
    try:
        # Try py7zr first (cleaner Python approach)
        try:
            import py7zr
            
            print(f"Creating 7z archive using py7zr: {archive_path}")
            
            # Create the .7z file directly with password
            with py7zr.SevenZipFile(archive_path, 'w', password=password) as archive:
                # Add entire folder contents to archive
                archive.writeall(folder_path, folder_name)
            
            return True, f"✅ Encrypted archive created: {os.path.basename(archive_path)}"
            
        except ImportError:
            print("py7zr not available, falling back to command line")
            # Fallback to 7-Zip command line if py7zr not available
            return create_encrypted_7z_via_command(folder_path, archive_path, password)
            
    except Exception as e:
        print(f"7z creation error: {str(e)}")
        return False, f"❌ Failed to create archive: {str(e)}"

def create_encrypted_7z_via_command(folder_path, archive_path, password):
    """Fallback method using 7-Zip command line"""
    try:
        print(f"Creating 7z archive using command line: {archive_path}")
        
        # Remove existing archive
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        # 7-Zip command for creating encrypted archive
        cmd = [
            '7z', 'a',              # Add to archive
            '-t7z',                 # Format: 7z
            f'-p{password}',        # Password
            '-mhe=on',              # Encrypt headers (filenames)
            '-mx=9',                # Maximum compression
            '-y',                   # Yes to all prompts
            archive_path,           # Output archive
            f'{folder_path}/*'      # Input folder contents
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            return True, f"✅ Encrypted archive created: {os.path.basename(archive_path)}"
        else:
            print(f"7z command failed with code {result.returncode}")
            print(f"stderr: {result.stderr}")
            return False, f"❌ 7-Zip error: {result.stderr.strip() or 'Unknown error'}"
            
    except subprocess.TimeoutExpired:
        return False, "❌ 7-Zip operation timed out - folder may be too large"
    except FileNotFoundError:
        return False, "❌ 7-Zip command not found - please install 7-Zip"
    except Exception as e:
        print(f"Command line 7z error: {str(e)}")
        return False, f"❌ Failed to create archive: {str(e)}"

def add_file_to_secure_archive(archive_path, password, file_data, filename, subfolder="Images"):
    """Add a file to an existing encrypted .7z archive"""
    try:
        print(f"Adding file {filename} to archive {archive_path}")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try py7zr first
            try:
                import py7zr
                
                print("Using py7zr for archive manipulation")
                
                # Extract existing archive
                with py7zr.SevenZipFile(archive_path, mode="r", password=password) as archive:
                    archive.extractall(path=temp_dir)
                
                # Find the extracted folder
                extracted_folders = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                if not extracted_folders:
                    return False, "No folder found in archive"
                
                extracted_folder = os.path.join(temp_dir, extracted_folders[0])
                
                # Add new file
                target_dir = os.path.join(extracted_folder, subfolder)
                os.makedirs(target_dir, exist_ok=True)
                
                with open(os.path.join(target_dir, filename), "wb") as f:
                    f.write(file_data)
                
                # Remove old archive
                os.remove(archive_path)
                
                # Create new archive with updated contents
                with py7zr.SevenZipFile(archive_path, 'w', password=password) as new_archive:
                    new_archive.writeall(extracted_folder, extracted_folders[0])
                
                return True, f"File added to secure archive: {filename}"
                
            except ImportError:
                print("py7zr not available, using command line")
                # Fallback to 7-Zip command line
                return add_file_to_archive_via_command(archive_path, password, file_data, filename, subfolder, temp_dir)
                
    except Exception as e:
        print(f"Archive manipulation error: {str(e)}")
        return False, f"Failed to add file to archive: {str(e)}"

def add_file_to_archive_via_command(archive_path, password, file_data, filename, subfolder, temp_dir):
    """Fallback method using 7-Zip command line"""
    try:
        print("Using 7-Zip command line for archive manipulation")
        
        # Extract archive using 7-Zip command
        extract_cmd = [
            '7z', 'x',
            f'-p{password}',
            f'-o{temp_dir}',
            '-y',
            archive_path
        ]
        
        result = subprocess.run(extract_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return False, f"Failed to extract archive: {result.stderr}"
        
        # Find extracted folder
        extracted_folders = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        if not extracted_folders:
            return False, "No folder found in archive"
        
        extracted_folder = os.path.join(temp_dir, extracted_folders[0])
        
        # Add new file
        target_dir = os.path.join(extracted_folder, subfolder)
        os.makedirs(target_dir, exist_ok=True)
        
        with open(os.path.join(target_dir, filename), "wb") as f:
            f.write(file_data)
        
        # Remove old archive
        os.remove(archive_path)
        
        # Create new archive
        create_cmd = [
            '7z', 'a',
            '-t7z',
            f'-p{password}',
            '-mhe=on',
            '-mx=9',
            '-y',
            archive_path,
            f'{extracted_folder}/*'
        ]
        
        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True, f"File added to secure archive: {filename}"
        else:
            return False, f"Failed to recreate archive: {result.stderr}"
            
    except Exception as e:
        print(f"Command line archive manipulation error: {str(e)}")
        return False, f"Command line archive operation failed: {str(e)}"

def check_folder_encryption_status(folder_path, db):
    """Check if a folder is encrypted and return status information with direct .7z support"""
    try:
        # Check if folder has 7-Zip archive (direct .7z approach)
        archive_path = folder_path + "_secure.7z"
        if os.path.exists(archive_path):
            # Check if original folder still exists
            if os.path.exists(folder_path):
                return {
                    'is_encrypted': True,
                    'method': '7zip_ready',
                    'status_text': '7-Zip Ready (Folder + Archive)',
                    'icon': '🔓',
                    'color': 'orange'
                }
            else:
                return {
                    'is_encrypted': True,
                    'method': '7zip_archived',
                    'status_text': '7-Zip AES-256 Archived',
                    'icon': '🛡️',
                    'color': 'green'
                }
        
        # Check if folder is hidden
        try:
            result = subprocess.run(['attrib', folder_path], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0 and 'H' in result.stdout:
                return {
                    'is_encrypted': False,
                    'method': 'hidden',
                    'status_text': 'Hidden Folder',
                    'icon': '🫥',
                    'color': 'blue'
                }
        except:
            pass
        
        # Standard folder
        return {
            'is_encrypted': False,
            'method': 'app_level',
            'status_text': 'App-level Security',
            'icon': '🔓',
            'color': 'orange'
        }
    except Exception:
        return {
            'is_encrypted': False,
            'method': 'unknown',
            'status_text': 'Unknown Status',
            'icon': '❓',
            'color': 'gray'
        }

# ===== COMPLETE MAIN FUNCTIONS WITH ALL ENHANCEMENTS =====

def encode_data(audio_path, data, output_path, data_type, user_id, input_file_path=None, receiver_email=None):
    """Main encoding function with recipient email embedding - COMPLETE ENHANCED VERSION"""
    handler = AudioFormatHandler()
    db = DatabaseManager()
    
    print(f"=== Encoding {data_type} ===")
    print(f"Audio: {audio_path}")
    print(f"Output: {output_path}")
    
    # Detect format
    format_info = handler.detect_format(audio_path)
    if 'error' in format_info:
        raise ValueError(format_info['error'])
    
    print(f"Format: {format_info['format'].upper()}")
    
    # Prepare data with enhanced validation
    if data_type == "message":
        if not isinstance(data, str):
            raise ValueError(f"Message data must be string, got {type(data)}")
        if len(data) > 255:
            raise ValueError("Message too long (max 255 characters)")
        raw_data = data.encode('utf-8')
        print(f"Message: {data} ({len(raw_data)} bytes)")
    else:
        if not isinstance(data, bytes):
            raise ValueError(f"File data must be bytes, got {type(data)}")
        raw_data = data
        print(f"Data size: {len(raw_data)} bytes ({len(raw_data)/1024:.1f} KB)")
    
    # Encrypt data
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(raw_data)
    print(f"Encrypted size: {len(encrypted_data)} bytes")
    
    # Embed recipient email and hash
    if receiver_email:
        email_prefix = f"EMAIL:{receiver_email}|".encode()
        email_hash = hashlib.sha256(receiver_email.encode()).hexdigest()[:8].encode()
        data_to_encode = email_prefix + email_hash + b"|" + encrypted_data
        print(f"Using recipient email: {receiver_email}")
    else:
        # Fallback for backward compatibility or no email
        data_to_encode = b"EMAIL:NONE|" + b"00000000|" + encrypted_data
        print("No recipient email specified")
    
    print(f"Total data to encode: {len(data_to_encode)} bytes")
    
    # Check capacity
    capacity_info = handler.estimate_capacity(format_info, len(data_to_encode))
    if not capacity_info['can_hold']:
        error_msg = f"Audio file too small. Need ~{estimate_audio_duration_needed(len(data_to_encode), format_info):.1f} minutes"
        raise ValueError(error_msg)
    
    print(f"Capacity: {capacity_info['capacity_percentage']:.1f}% used")
    
    # Convert to PCM and embed
    pcm_data = handler.to_pcm(audio_path, format_info)
    modified_pcm = _embed_lsb(pcm_data, data_to_encode)
    
    # Save result - CRITICAL FIX: Create directory first
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    handler.from_pcm(modified_pcm, output_path, format_info)
    
    # Verify output file exists and has reasonable size
    if os.path.exists(output_path):
        output_size = os.path.getsize(output_path)
        print(f"Output file created successfully, size: {output_size} bytes")
    else:
        raise ValueError("Failed to create output file")
    
    # Save to database (no secure folder for encoding)
    try:
        success, message, history_id = db.save_history(
            user_id, "encode", data_type, input_file_path, audio_path, 
            output_path, receiver_email, key.decode(),
            format_info['format'], format_info.get('codec'), 'lsb',
            get_file_size_mb(output_path), None, True, None, None  # No secure folder for encode
        )
        if success:
            db.save_log(user_id, history_id, "encode", data_type, 
                       f"Successfully encoded {data_type} in {format_info['format'].upper()}")
    except Exception as e:
        print(f"Database error: {e}")
    
    print(f"✅ Encoding complete: {output_path}")
    return key

def decode_data(file_path, key, expected_type, user_id, folder_id=None):
    """Main decoding function with direct .7z archive support and all enhancements"""
    handler = AudioFormatHandler()
    db = DatabaseManager()
    
    print(f"=== Decoding {expected_type} ===")
    print(f"Audio: {file_path}")
    
    # Detect format
    format_info = handler.detect_format(file_path)
    if 'error' in format_info:
        raise ValueError(format_info['error'])
    
    print(f"Format: {format_info['format'].upper()}")
    
    # Convert to PCM and extract
    pcm_data = handler.to_pcm(file_path, format_info)
    extracted_data = _extract_lsb(pcm_data)
    
    # Extract email, hash, and encrypted data
    if not extracted_data.startswith(b"EMAIL:"):
        raise ValueError("Invalid encoded data: Missing email prefix")
    
    parts = extracted_data.split(b"|", 2)
    if len(parts) != 3:
        raise ValueError("Invalid encoded data format")
    
    email_str = parts[0][6:].decode()  # Remove "EMAIL:" prefix
    email_hash = parts[1].decode()
    encrypted_data = parts[2]
    
    # Verify email hash
    if email_str != "NONE":
        computed_hash = hashlib.sha256(email_str.encode()).hexdigest()[:8]
        if email_hash != computed_hash:
            raise ValueError("Invalid encoded data: Email hash mismatch")
        
        # Verify recipient email against logged-in user's email
        user_details = db.get_user_details(user_id)
        user_email = user_details['user_info']['email']
        if email_str != user_email:
            try:
                db.save_history(
                    user_id, "decode", expected_type,
                    None, file_path, None, None, key.decode(),
                    format_info['format'], format_info.get('codec'), 'lsb',
                    None, None, False, "Unauthorized: Email does not match recipient",
                    folder_id
                )
            except:
                pass
            raise ValueError("Unauthorized: Your email does not match the recipient email")
    
    # Decrypt
    try:
        raw_data = Fernet(key).decrypt(encrypted_data)
    except InvalidToken:
        try:
            db.save_history(
                user_id, "decode", expected_type,
                None, file_path, None, None, key.decode(),
                format_info['format'], format_info.get('codec'), 'lsb',
                None, None, False, "Invalid decryption key",
                folder_id
            )
        except:
            pass
        raise ValueError("Invalid decryption key or corrupted data")
    
    # Handle secure folder or default folder with enhanced 7-Zip support
    folder_path = None
    folder_name = "Default"
    folder_encryption_info = None
    folder_needs_securing = False
    
    if folder_id is not None:
        folder_info = db.get_folder_info(folder_id, user_id)
        if folder_info:
            folder_path = folder_info[2]
            folder_name = folder_info[1]
            archive_path = folder_info[7] if len(folder_info) > 7 else None
            
            # Get encryption status from database - updated for 7-Zip
            is_encrypted = len(folder_info) > 5 and folder_info[5]  # is_encrypted field
            encryption_method = folder_info[6] if len(folder_info) > 6 else 'none'
            is_hidden = len(folder_info) > 8 and folder_info[8] if len(folder_info) > 8 else False
            
            # Check if this is a direct .7z archive (folder doesn't exist, archive does)
            if archive_path and os.path.exists(archive_path) and not os.path.exists(folder_path):
                # This is a direct .7z archive - add file to it
                print(f"🛡️ Adding file to encrypted .7z archive: {archive_path}")
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if expected_type == "message":
                    filename = f"decoded_message_{format_info['format']}_{timestamp}.txt"
                    subfolder = "Messages"
                elif expected_type == "image":
                    filename = f"decoded_image_{format_info['format']}_{timestamp}.jpg"
                    subfolder = "Images"
                elif expected_type == "pdf":
                    filename = f"decoded_document_{format_info['format']}_{timestamp}.pdf"
                    subfolder = "PDFs"
                
                # Add file to archive
                success, message = add_file_to_secure_archive(
                    archive_path, key.decode(), raw_data, filename, subfolder
                )
                
                if success:
                    print(f"✅ File added to secure archive: {filename}")
                    
                    # Save to database
                    try:
                        db.save_history(
                            user_id, "decode", expected_type,
                            None, file_path, f"[ARCHIVE]/{subfolder}/{filename}", None, key.decode(),
                            format_info['format'], format_info.get('codec'), 'lsb',
                            len(raw_data) / (1024 * 1024), None, True, None,
                            folder_id
                        )
                        db.save_log(user_id, None, "decode", expected_type, 
                                   f"Successfully decoded {expected_type} to encrypted archive: {folder_name}")
                    except Exception as e:
                        print(f"Database error: {e}")
                    
                    if expected_type == "message":
                        return raw_data.decode("utf-8")
                    else:
                        return f"[ARCHIVE]/{subfolder}/{filename}"
                else:
                    print(f"❌ Failed to add to archive: {message}")
                    # Fall back to regular folder creation
            
            # Enhanced encryption status detection
            if is_encrypted and encryption_method == '7zip_aes256':
                folder_encryption_info = {
                    'is_encrypted': True,
                    'method': '7zip_aes256',
                    'status_text': '7-Zip AES-256 Encrypted',
                    'icon': '🛡️'
                }
                folder_needs_securing = True  # Will need to re-encrypt after use
                print(f"🛡️ Using 7-Zip encrypted secure folder: {folder_name} at {folder_path}")
            elif is_hidden:
                folder_encryption_info = {
                    'is_encrypted': False,
                    'method': 'hidden',
                    'status_text': 'Hidden + App Security',
                    'icon': '🫥'
                }
                print(f"🫥 Using hidden secure folder: {folder_name} at {folder_path}")
            else:
                folder_encryption_info = {
                    'is_encrypted': False,
                    'method': 'app_level',
                    'status_text': 'App-level Security',
                    'icon': '🔓'
                }
                print(f"🔓 Using app-secured folder: {folder_name} at {folder_path}")
    
    # Determine output directory
    if folder_path and (os.path.exists(folder_path) or folder_id):
        # Use secure folder with subdirectories
        if expected_type == "image":
            output_dir = os.path.join(folder_path, "Images")
        elif expected_type == "pdf":
            output_dir = os.path.join(folder_path, "PDFs")
        else:
            # For messages, save directly in folder
            output_dir = folder_path
        
        # Ensure subdirectories exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Enhanced logging with 7-Zip encryption status
        if folder_encryption_info:
            if folder_encryption_info['method'] == '7zip_aes256':
                print(f"🛡️ Saving to 7-Zip ready secure folder: {output_dir}")
            elif folder_encryption_info['method'] == 'hidden':
                print(f"🫥 Saving to hidden secure folder: {output_dir}")
            else:
                print(f"🔓 Saving to app-secured folder: {output_dir}")
        
    else:
        # Use user-specific default folder
        user_folder, images_dir, pdfs_dir = create_user_default_folder(user_id)
        
        if expected_type == "image":
            output_dir = images_dir
        elif expected_type == "pdf":
            output_dir = pdfs_dir
        else:
            output_dir = user_folder
        
        print(f"📁 Saving to user default folder: {output_dir}")
        folder_name = "Default User Folder"
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Process result based on type
    output_path = None
    try:
        if expected_type == "message":
            message = raw_data.decode("utf-8")
            print(f"✅ Decoded message: {message}")
            output_path = os.path.join(output_dir, f"decoded_message_{format_info['format']}_{timestamp}.txt")
            with open(output_path, "w", encoding="utf-8") as txt:
                txt.write(message)
            
            # Enhanced success message
            if folder_encryption_info and folder_encryption_info['method'] == '7zip_aes256':
                print(f"🛡️ Message saved to 7-Zip ready secure folder: {output_path}")
            elif folder_encryption_info and folder_encryption_info['method'] == 'hidden':
                print(f"🫥 Message saved to hidden folder: {output_path}")
            else:
                print(f"✅ Message saved: {output_path}")
            
            result = message
        
        elif expected_type == "image":
            output_path = os.path.join(output_dir, f"decoded_image_{format_info['format']}_{timestamp}.jpg")
            with open(output_path, 'wb') as f:
                f.write(raw_data)
            
            # Enhanced success message with encryption status
            if folder_encryption_info and folder_encryption_info['method'] == '7zip_aes256':
                print(f"🛡️ Image saved to 7-Zip ready secure folder: {output_path}")
            elif folder_encryption_info and folder_encryption_info['method'] == 'hidden':
                print(f"🫥 Image saved to hidden folder: {output_path}")
            else:
                print(f"✅ Image saved: {output_path}")
            
            # Validate saved image
            is_valid, validation_msg = validate_image_file(output_path)
            if not is_valid:
                print(f"Warning: {validation_msg}")
            
            result = output_path
        
        elif expected_type == "pdf":
            output_path = os.path.join(output_dir, f"decoded_document_{format_info['format']}_{timestamp}.pdf")
            with open(output_path, 'wb') as f:
                f.write(raw_data)
            
            # Validate saved PDF
            is_valid, validation_msg = validate_pdf_file(output_path)
            
            # Enhanced success message with encryption status
            if folder_encryption_info and folder_encryption_info['method'] == '7zip_aes256':
                print(f"🛡️ PDF saved to 7-Zip ready secure folder: {output_path} - {validation_msg}")
            elif folder_encryption_info and folder_encryption_info['method'] == 'hidden':
                print(f"🫥 PDF saved to hidden folder: {output_path} - {validation_msg}")
            else:
                print(f"✅ PDF saved: {output_path} - {validation_msg}")
            
            result = output_path
        
        # Save to database with enhanced logging
        try:
            db.save_history(
                user_id, "decode", expected_type,
                None, file_path, output_path, None, key.decode(),
                format_info['format'], format_info.get('codec'), 'lsb',
                get_file_size_mb(output_path) if output_path else None, None, True, None,
                folder_id
            )
            
            # Enhanced logging with detailed encryption status
            if folder_encryption_info:
                if folder_encryption_info['method'] == '7zip_aes256':
                    log_message = f"Successfully decoded {expected_type} from {format_info['format'].upper()} to 7-Zip ready secure folder: {folder_name}"
                elif folder_encryption_info['method'] == 'hidden':
                    log_message = f"Successfully decoded {expected_type} from {format_info['format'].upper()} to hidden secure folder: {folder_name}"
                else:
                    log_message = f"Successfully decoded {expected_type} from {format_info['format'].upper()} to app-secured folder: {folder_name}"
            else:
                log_message = f"Successfully decoded {expected_type} from {format_info['format'].upper()} to folder: {folder_name}"
            
            db.save_log(user_id, None, "decode", expected_type, log_message)
        except Exception as e:
            print(f"Database error: {e}")
        
        # Re-secure folder if it was 7-Zip encrypted
        if folder_needs_securing and folder_id:
            print("🔒 Re-securing folder after file operations...")
            try:
                secure_success, secure_message = db.secure_folder_after_use(folder_id, key.decode(), user_id)
                if secure_success:
                    print(f"✅ Folder re-secured: {secure_message}")
                else:
                    print(f"⚠️ Folder re-securing warning: {secure_message}")
            except Exception as e:
                print(f"⚠️ Re-securing error: {e}")
        
        print(f"💡 Tip: Use 'Manage Folders' → 'Secure Folders Now' to create encrypted .7z archive when ready!")
        
        return result
        
    except Exception as e:
        # If error occurred and folder needs securing, attempt to secure it anyway
        if folder_needs_securing and folder_id:
            try:
                db.secure_folder_after_use(folder_id, key.decode(), user_id)
            except:
                pass
        raise e

def get_folder_security_summary(folder_id, user_id):
    """Get a comprehensive security summary for a folder with complete 7-Zip support"""
    if folder_id is None:
        return {
            'folder_name': 'Default User Folder',
            'security_level': 'Basic',
            'encryption_status': 'Not encrypted',
            'icon': '📁',
            'description': 'Standard user folder with no additional security'
        }
    
    db = DatabaseManager()
    folder_info = db.get_folder_info(folder_id, user_id)
    
    if not folder_info:
        return {
            'folder_name': 'Unknown Folder',
            'security_level': 'Unknown',
            'encryption_status': 'Unknown',
            'icon': '❓',
            'description': 'Folder information not available'
        }
    
    folder_name = folder_info[1]
    folder_path = folder_info[2]
    is_encrypted = len(folder_info) > 5 and folder_info[5]
    encryption_method = folder_info[6] if len(folder_info) > 6 else 'none'
    is_hidden = len(folder_info) > 8 and folder_info[8] if len(folder_info) > 8 else False
    archive_path = folder_info[7] if len(folder_info) > 7 else None
    
    # Check current status - direct .7z approach
    folder_exists = os.path.exists(folder_path)
    archive_exists = archive_path and os.path.exists(archive_path)
    
    if archive_exists and not folder_exists:
        # Direct .7z archive (fully secured)
        return {
            'folder_name': folder_name,
            'security_level': 'Maximum',
            'encryption_status': '7-Zip AES-256 encrypted archive (double-click to access)',
            'icon': '🛡️',
            'description': 'Fully encrypted archive - double-click .7z file with your password!'
        }
    elif is_encrypted and encryption_method == '7zip_aes256':
        # 7-Zip ready (folder exists, may have archive too)
        return {
            'folder_name': folder_name,
            'security_level': 'Enhanced',
            'encryption_status': '7-Zip ready + App password protected + Compression ready',
            'icon': '🔓',
            'description': 'Ready for 7-Zip encryption - use "Secure Folders Now" to create encrypted archive'
        }
    elif is_hidden:
        return {
            'folder_name': folder_name,
            'security_level': 'Enhanced',
            'encryption_status': 'Hidden from File Explorer + App password protected',
            'icon': '🫥',
            'description': 'Hidden folder with app-level password protection'
        }
    else:
        return {
            'folder_name': folder_name,
            'security_level': 'Standard',
            'encryption_status': 'App password protected only',
            'icon': '🔓',
            'description': 'App-level password protection without additional encryption'
        }

def estimate_folder_compression_ratio(folder_path):
    """Estimate compression ratio for 7-Zip encryption"""
    try:
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    continue
        
        # Estimate compression (typical 7-Zip ratios)
        if total_size == 0:
            return 0, 0, "No files to compress"
        
        # Better estimates based on file types and sizes
        if total_size < 1024 * 1024:  # Less than 1MB
            estimated_compressed = total_size * 0.8  # 20% compression for small files
        else:
            estimated_compressed = total_size * 0.6  # 40% compression for larger files
            
        savings_mb = (total_size - estimated_compressed) / (1024 * 1024)
        compression_percent = ((total_size - estimated_compressed) / total_size) * 100
        
        return (total_size, estimated_compressed, 
                f"Estimated savings: {savings_mb:.1f} MB ({compression_percent:.1f}%) for {file_count} files")
        
    except Exception as e:
        return 0, 0, f"Could not estimate compression: {str(e)}"

def verify_folder_integrity(folder_id, user_id):
    """Verify the integrity of a secure folder and its encryption with complete 7-Zip support"""
    db = DatabaseManager()
    folder_info = db.get_folder_info(folder_id, user_id)
    
    if not folder_info:
        return False, "Folder not found"
    
    folder_path = folder_info[2]
    is_encrypted = len(folder_info) > 5 and folder_info[5]
    encryption_method = folder_info[6] if len(folder_info) > 6 else 'none'
    archive_path = folder_info[7] if len(folder_info) > 7 else None
    
    integrity_issues = []
    
    # Check direct .7z archive integrity
    folder_exists = os.path.exists(folder_path)
    archive_exists = archive_path and os.path.exists(archive_path)
    
    if archive_exists and not folder_exists:
        # Direct .7z archive mode - check archive integrity
        try:
            result = subprocess.run(['7z', 't', archive_path], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                integrity_issues.append("7-Zip archive integrity check failed")
            else:
                print(f"✅ Archive integrity verified: {archive_path}")
        except Exception as e:
            integrity_issues.append(f"Could not verify archive integrity: {str(e)}")
    elif folder_exists:
        # Regular folder mode - check folder structure
        expected_subdirs = ["Images", "PDFs"]
        for subdir in expected_subdirs:
            subdir_path = os.path.join(folder_path, subdir)
            if not os.path.exists(subdir_path):
                integrity_issues.append(f"Missing subdirectory: {subdir}")
                
        # Check if 7-Zip encryption is configured properly
        if is_encrypted and encryption_method == '7zip_aes256':
            if not archive_path:
                integrity_issues.append("7-Zip encryption configured but no archive path set")
    else:
        integrity_issues.append("Neither folder nor archive exists")
    
    if integrity_issues:
        return False, "; ".join(integrity_issues)
    else:
        if archive_exists and not folder_exists:
            return True, "Encrypted archive integrity verified - ready for direct access"
        else:
            return True, "Folder structure verified successfully"

def get_folder_status_message(folder_id, user_id):
    """Get user-friendly status message for folder with complete 7-Zip support"""
    if not folder_id:
        return "📁 Saving to default user folder (no security)"
    
    db = DatabaseManager()
    folder_info = db.get_folder_info(folder_id, user_id)
    
    if not folder_info:
        return "❓ Unknown folder status"
    
    folder_name = folder_info[1]
    folder_path = folder_info[2]
    is_encrypted = len(folder_info) > 5 and folder_info[5]
    encryption_method = folder_info[6] if len(folder_info) > 6 else 'none'
    archive_path = folder_info[7] if len(folder_info) > 7 else None
    
    # Check current status
    folder_exists = os.path.exists(folder_path)
    archive_exists = archive_path and os.path.exists(archive_path)
    
    if archive_exists and not folder_exists:
        return f"🛡️ Folder '{folder_name}' is fully encrypted (double-click .7z to access)"
    elif is_encrypted and encryption_method == '7zip_aes256':
        return f"🔓 Folder '{folder_name}' is ready for 7-Zip encryption"
    else:
        return f"📁 Folder '{folder_name}' has app-level security"
