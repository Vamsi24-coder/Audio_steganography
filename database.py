# database.py
import sqlite3
import bcrypt
import re
import json
import csv
import os
import subprocess
import platform
import tempfile
import shutil
from datetime import datetime

DB_FILE = "steganography.db"

class DatabaseManager:
    """SQLite wrapper – stores users, credentials, history, logs & secure folders with 7-Zip support."""

    # ────────────────────────── INIT / SCHEMA ──────────────────────────
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()
        self.upgrade_database()

    def create_tables(self):
        cur = self.conn.cursor()

        # USERS ----------------------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name  TEXT NOT NULL,
                last_name   TEXT NOT NULL,
                username    TEXT UNIQUE NOT NULL,
                email       TEXT UNIQUE NOT NULL,
                password    TEXT NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login  TIMESTAMP,
                is_active   BOOLEAN   DEFAULT 1
            )
            """
        )

        # CREDENTIALS ----------------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS credentials (
                user_id        INTEGER PRIMARY KEY,
                sender_email   TEXT,
                smtp_username  TEXT,
                smtp_password  TEXT,
                updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        # HISTORY --------------------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id                INTEGER,
                operation              TEXT NOT NULL,            -- encode / decode
                data_type              TEXT NOT NULL,            -- message / image / pdf
                audio_format           TEXT,
                audio_codec            TEXT,
                steganography_method   TEXT,
                input_file_path        TEXT,                     -- may be NULL for decode
                audio_file_path        TEXT,
                output_file_path       TEXT,
                receiver_email         TEXT,
                decryption_key         TEXT,
                file_size_mb           REAL,
                processing_time_seconds REAL,
                success               BOOLEAN DEFAULT 1,
                error_message          TEXT,
                operation_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                secure_folder_id       INTEGER,                  -- Link to secure folder
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (secure_folder_id) REFERENCES secure_folders(id) ON DELETE SET NULL
            )
            """
        )

        # LOGS -----------------------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER,
                operation_id  INTEGER,
                operation_type TEXT,
                data_type      TEXT,
                audio_format   TEXT,
                log_level      TEXT DEFAULT 'INFO',
                log_message    TEXT,
                log_timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)      REFERENCES users(id)    ON DELETE CASCADE,
                FOREIGN KEY (operation_id) REFERENCES history(id) ON DELETE CASCADE
            )
            """
        )

        # SECURE FOLDERS WITH 7-ZIP SUPPORT -----------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS secure_folders (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id           INTEGER NOT NULL,
                folder_name       TEXT NOT NULL,
                folder_path       TEXT NOT NULL,
                password_hash     TEXT NOT NULL,
                is_encrypted      BOOLEAN DEFAULT 0,           -- 7-Zip encryption status
                encryption_method TEXT DEFAULT 'none',         -- 'none', 'windows_efs', '7zip_aes256'
                archive_path      TEXT,                        -- Path to .7z file
                is_hidden         BOOLEAN DEFAULT 0,           -- Windows hidden folder
                created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used         TIMESTAMP,
                is_active         BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, folder_name)
            )
            """
        )

        # USER PREFERENCES ----------------------------------------------
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id                     INTEGER PRIMARY KEY,
                preferred_audio_format      TEXT    DEFAULT 'wav',
                default_steganography_method TEXT   DEFAULT 'lsb',
                auto_delete_temp_files      BOOLEAN DEFAULT 1,
                email_notifications         BOOLEAN DEFAULT 1,
                download_history_format     TEXT    DEFAULT 'csv',
                enable_7zip_encryption      BOOLEAN DEFAULT 1,    -- 7-Zip encryption preference
                enable_folder_hiding        BOOLEAN DEFAULT 0,    -- Folder hiding preference
                compression_level           INTEGER DEFAULT 9,    -- 7-Zip compression level
                preferences_json            TEXT,
                updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        self.conn.commit()

    # -------------------------------------------------------------------
    # Upgrade – adds columns if the file is from an older version
    # -------------------------------------------------------------------
    def upgrade_database(self):
        cur = self.conn.cursor()
        new_cols = [
            ("history", "audio_format", "TEXT"),
            ("history", "audio_codec", "TEXT"),
            ("history", "steganography_method", "TEXT"),
            ("history", "file_size_mb", "REAL"),
            ("history", "processing_time_seconds", "REAL"),
            ("history", "success", "BOOLEAN DEFAULT 1"),
            ("history", "error_message", "TEXT"),
            ("history", "secure_folder_id", "INTEGER"),
            ("logs", "audio_format", "TEXT"),
            ("logs", "log_level", "TEXT DEFAULT 'INFO'"),
            # Updated for 7-Zip support
            ("secure_folders", "is_encrypted", "BOOLEAN DEFAULT 0"),
            ("secure_folders", "encryption_method", "TEXT DEFAULT 'none'"),
            ("secure_folders", "archive_path", "TEXT"),
            ("secure_folders", "is_hidden", "BOOLEAN DEFAULT 0"),
            ("user_preferences", "enable_7zip_encryption", "BOOLEAN DEFAULT 1"),
            ("user_preferences", "enable_folder_hiding", "BOOLEAN DEFAULT 0"),
            ("user_preferences", "compression_level", "INTEGER DEFAULT 9"),
        ]

        for table, col, coltype in new_cols:
            try:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}")
            except sqlite3.OperationalError:
                pass  # column already exists

        self.conn.commit()

    # ────────────────────── 7-ZIP ENCRYPTION METHODS ─────────────────────
    def check_7zip_available(self):
        """Check if 7-Zip is available on the system"""
        try:
            # Test 7z command availability
            result = subprocess.run(['7z'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or "7-Zip" in result.stdout:
                return True, "7-Zip is available"
            else:
                return False, "7-Zip command not found"
        except FileNotFoundError:
            return False, "7-Zip is not installed or not in PATH"
        except Exception as e:
            return False, f"7-Zip check failed: {str(e)}"

    def get_user_security_preferences(self, user_id):
        """Get user's security preferences for 7-Zip and folder hiding"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT enable_7zip_encryption, enable_folder_hiding, compression_level 
            FROM user_preferences WHERE user_id = ?
            """,
            (user_id,)
        )
        result = cur.fetchone()
        if result:
            return bool(result[0]), bool(result[1]), result[2] or 9
        else:
            # Create default preferences
            cur.execute(
                "INSERT OR IGNORE INTO user_preferences (user_id) VALUES (?)",
                (user_id,)
            )
            self.conn.commit()
            return True, False, 9  # Default: 7-Zip enabled, hiding disabled, max compression

    def update_user_security_preferences(self, user_id, use_7zip=True, use_hiding=False, compression_level=9):
        """Update user's security preferences"""
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO user_preferences 
            (user_id, enable_7zip_encryption, enable_folder_hiding, compression_level, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, use_7zip, use_hiding, compression_level, datetime.now())
        )
        self.conn.commit()
        return True, "Security preferences updated successfully"

    def create_7zip_archive(self, folder_path, archive_path, password, compression_level=9):
        """Create encrypted 7-Zip archive from folder"""
        try:
            # Remove existing archive
            if os.path.exists(archive_path):
                os.remove(archive_path)

            # 7-Zip command for creating encrypted archive
            cmd = [
                '7z', 'a',                      # Add to archive
                '-t7z',                         # Format: 7z
                f'-p{password}',                # Password
                '-mhe=on',                      # Encrypt headers (filenames)
                f'-mx={compression_level}',     # Compression level
                '-y',                           # Yes to all prompts
                archive_path,                   # Output archive
                f'{folder_path}/*'              # Input folder contents
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return True, f"7-Zip archive created successfully: {os.path.basename(archive_path)}"
            else:
                return False, f"7-Zip error: {result.stderr.strip() or 'Unknown error'}"

        except subprocess.TimeoutExpired:
            return False, "7-Zip operation timed out - folder may be too large"
        except FileNotFoundError:
            return False, "7-Zip command not found - please install 7-Zip"
        except Exception as e:
            return False, f"7-Zip archive creation failed: {str(e)}"

    def extract_7zip_archive(self, archive_path, output_path, password):
        """Extract 7-Zip archive to specified location"""
        try:
            # Create output directory
            os.makedirs(output_path, exist_ok=True)

            # 7-Zip extract command
            cmd = [
                '7z', 'x',                      # Extract
                f'-p{password}',                # Password
                f'-o{output_path}',             # Output directory
                '-y',                           # Yes to all prompts
                archive_path                    # Archive file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                return True, f"Archive extracted successfully to: {output_path}"
            else:
                return False, f"7-Zip extraction error: {result.stderr.strip() or 'Invalid password or corrupted archive'}"

        except subprocess.TimeoutExpired:
            return False, "7-Zip extraction timed out"
        except Exception as e:
            return False, f"7-Zip extraction failed: {str(e)}"

    def hide_folder_windows(self, folder_path):
        """Hide folder using Windows attributes"""
        try:
            result = subprocess.run(['attrib', '+H', folder_path], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True, "Folder hidden successfully"
            else:
                return False, f"Failed to hide folder: {result.stderr.strip()}"
        except Exception as e:
            return False, f"Folder hiding failed: {str(e)}"

    def show_folder_windows(self, folder_path):
        """Show hidden folder using Windows attributes"""
        try:
            result = subprocess.run(['attrib', '-H', folder_path], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True, "Folder shown successfully"
            else:
                return False, f"Failed to show folder: {result.stderr.strip()}"
        except Exception as e:
            return False, f"Folder show failed: {str(e)}"

    # ───────────────────────────── USERS ───────────────────────────────
    def signup(self, first, last, username, email, password):
        if len(password) < 10:
            return False, "Password must be at least 10 characters."
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password) or not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]", password
        ):
            return (
                False,
                "Password must contain letters, numbers and special characters.",
            )

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$", email):
            return False, "Invalid email address."

        if len(username) < 3:
            return False, "Username must be at least 3 characters."

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO users (first_name, last_name, username, email, password, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (first, last, username, email, hashed, datetime.now()),
            )
            uid = cur.lastrowid
            cur.execute("INSERT OR IGNORE INTO user_preferences (user_id) VALUES (?)", (uid,))
            self.conn.commit()
            return True, "Account created!"
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already taken."
            if "email" in str(e):
                return False, "Email already registered."
            return False, "Signup failed."
        except Exception as e:
            return False, f"Signup failed: {e}"

    def login(self, user_or_email, password):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, password, is_active FROM users
            WHERE (username = ? OR email = ?) AND is_active = 1
            """,
            (user_or_email, user_or_email),
        )
        user = cur.fetchone()
        if user and bcrypt.checkpw(password.encode(), user[1]):
            cur.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user[0]))
            self.conn.commit()
            return True, user[0]
        return False, "Invalid credentials."

    def reset_password(self, username, new_pass):
        if len(new_pass) < 10 or not re.search(r"[A-Za-z]", new_pass) or not re.search(
            r"\d", new_pass
        ) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_pass):
            return (
                False,
                "Password must be ≥10 characters and include letters, numbers, special chars.",
            )
        hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE users SET password = ? WHERE username = ? AND is_active = 1",
            (hashed, username),
        )
        if cur.rowcount:
            self.conn.commit()
            return True, "Password reset."
        return False, "Username not found."

    # ───────────────────── SMTP / credentials ──────────────────────────
    def save_credentials(self, user_id, sender, smtp_user, smtp_pass):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO credentials
            (user_id, sender_email, smtp_username, smtp_password, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, sender, smtp_user, smtp_pass, datetime.now()),
        )
        self.conn.commit()

    def get_credentials(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT sender_email, smtp_username, smtp_password FROM credentials WHERE user_id = ?",
            (user_id,),
        )
        return cur.fetchone() or ("", "", "")
    # Add this to your DatabaseManager class
    def save_log(self, user_id, history_id, operation, data_type, message):
        """Save operation log"""
        try:
            # Simple logging implementation
            print(f"Log: {operation} {data_type} - {message}")
            return True, "Log saved"
        except Exception as e:
            print(f"Log save error: {e}")
            return False, str(e)
        
    def save_7z_folder_path(self, user_id, folder_name, original_path, archive_7z_path, password):
        """Save 7z archive path to database for simple workflow"""
        try:
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO secure_folders (
                    user_id, folder_name, folder_path, password_hash,
                    is_encrypted, encryption_method, archive_path, 
                    created_at, last_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, folder_name, original_path, password_hash,
                True, '7zip_aes256', archive_7z_path,
                datetime.now(), datetime.now())
            )
            
            folder_id = cur.lastrowid
            self.conn.commit()
            
            # Log the creation
            self.save_log(user_id, None, "7z_creation", "secure_folder",
                        f"7z folder created: {folder_name} -> {archive_7z_path}")
            
            return True, f"7z folder '{folder_name}' saved successfully", folder_id
            
        except sqlite3.IntegrityError:
            return False, f"Folder name '{folder_name}' already exists for this user", None
        except Exception as e:
            return False, f"Failed to save 7z folder: {str(e)}", None

    def get_user_7z_folders(self, user_id):
        """Get all user's 7z folder paths for selection dialog"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, folder_name, folder_path, archive_path, created_at, last_used
            FROM secure_folders
            WHERE user_id = ? AND is_active = 1 
            AND is_encrypted = 1 AND encryption_method = '7zip_aes256'
            AND archive_path IS NOT NULL
            ORDER BY last_used DESC
            """,
            (user_id,)
        )
        return cur.fetchall()

    def verify_7z_folder_access(self, folder_id, password, user_id):
        """Verify user can access the 7z folder with password"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT password_hash, folder_name, archive_path 
            FROM secure_folders
            WHERE id = ? AND user_id = ? AND is_active = 1
            """,
            (folder_id, user_id)
        )
        
        result = cur.fetchone()
        if not result:
            return False, "Folder not found or access denied", None
        
        password_hash, folder_name, archive_path = result
        
        # Verify password
        if bcrypt.checkpw(password.encode(), password_hash):
            # Update last_used timestamp
            cur.execute(
                "UPDATE secure_folders SET last_used = ? WHERE id = ?",
                (datetime.now(), folder_id)
            )
            self.conn.commit()
            
            return True, f"Access granted to '{folder_name}'", archive_path
        else:
            return False, "Incorrect password", None

    def get_7z_folder_info(self, folder_id, user_id):
        """Get specific 7z folder information"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, folder_name, folder_path, archive_path, 
                created_at, last_used, is_encrypted
            FROM secure_folders
            WHERE id = ? AND user_id = ? AND is_active = 1
            """,
            (folder_id, user_id)
        )
        return cur.fetchone()

    def create_simple_7z_folder(self, user_id, folder_name, folder_path, password):
        """Create a new folder and immediately convert to 7z archive"""
        try:
            # Validate password
            is_valid, message = self.validate_folder_password(password)
            if not is_valid:
                return False, message, None
            
            # Create the physical folder first
            os.makedirs(folder_path, exist_ok=True)
            
            # Create subdirectories
            images_dir = os.path.join(folder_path, "Images")
            pdfs_dir = os.path.join(folder_path, "PDFs")
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(pdfs_dir, exist_ok=True)
            
            # Add readme files
            with open(os.path.join(images_dir, "readme.txt"), "w") as f:
                f.write("Decoded images will be stored here")
            with open(os.path.join(pdfs_dir, "readme.txt"), "w") as f:
                f.write("Decoded PDFs will be stored here")
            
            # Create 7z archive path
            archive_path = folder_path + "_secure.7z"
            
            # Get compression level from user preferences
            _, _, compression_level = self.get_user_security_preferences(user_id)
            
            # Create 7z archive
            archive_success, archive_msg = self.create_7zip_archive(
                folder_path, archive_path, password, compression_level
            )
            
            if archive_success:
                # Remove original folder for security
                shutil.rmtree(folder_path)
                
                # Save to database
                success, message, folder_id = self.save_7z_folder_path(
                    user_id, folder_name, folder_path, archive_path, password
                )
                
                if success:
                    return True, f"✅ 7z folder '{folder_name}' created successfully!\n📦 Archive: {os.path.basename(archive_path)}", folder_id
                else:
                    return False, f"Archive created but database save failed: {message}", None
            else:
                # Clean up folder if archive creation failed
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                return False, f"Failed to create 7z archive: {archive_msg}", None
                
        except Exception as e:
            # Clean up on any error
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                except:
                    pass
            return False, f"Error creating 7z folder: {str(e)}", None

    def extract_7z_for_decoding(self, folder_id, password, user_id):
        """Extract 7z archive to temp directory for decoding (clean method)"""
        try:
            # Get folder info
            folder_info = self.get_7z_folder_info(folder_id, user_id)
            if not folder_info:
                return False, "Folder not found", None
            
            folder_name = folder_info[1]
            archive_path = folder_info[3]
            
            # Verify the archive exists
            if not os.path.exists(archive_path):
                return False, f"Archive file not found: {archive_path}", None
            
            # Create temp directory for extraction
            temp_dir = tempfile.mkdtemp(prefix=f"7z_decode_{folder_name}_")
            
            # Extract archive to temp directory
            extract_success, extract_msg = self.extract_7zip_archive(
                archive_path, temp_dir, password
            )
            
            if extract_success:
                # Find the extracted folder
                extracted_items = os.listdir(temp_dir)
                if extracted_items:
                    # Look for the main folder
                    for item in extracted_items:
                        item_path = os.path.join(temp_dir, item)
                        if os.path.isdir(item_path):
                            return True, f"Archive extracted successfully", item_path
                    
                    # If no subfolder, use temp_dir directly
                    return True, f"Archive extracted successfully", temp_dir
                else:
                    return False, "Archive appears to be empty", None
            else:
                # Clean up temp directory on extraction failure
                shutil.rmtree(temp_dir, ignore_errors=True)
                return False, f"Failed to extract archive: {extract_msg}", None
                
        except Exception as e:
            return False, f"Error extracting 7z archive: {str(e)}", None

    def cleanup_temp_extraction(self, temp_path):
        """Clean up temporary extraction directory"""
        try:
            if temp_path and os.path.exists(temp_path):
                # Find the temp directory (go up until we find a temp dir)
                cleanup_path = temp_path
                while cleanup_path and not cleanup_path.startswith(tempfile.gettempdir()):
                    cleanup_path = os.path.dirname(cleanup_path)
                    if cleanup_path == os.path.dirname(cleanup_path):  # Reached root
                        break
                
                # If we found a temp path, clean it up
                if cleanup_path and cleanup_path.startswith(tempfile.gettempdir()):
                    shutil.rmtree(cleanup_path, ignore_errors=True)
                    return True, "Temporary files cleaned up"
                else:
                    # Just clean the specific path
                    shutil.rmtree(temp_path, ignore_errors=True)
                    return True, "Files cleaned up"
            else:
                return True, "No cleanup needed"
        except Exception as e:
            return False, f"Cleanup failed: {str(e)}"

    def update_7z_folder_after_decode(self, folder_id, temp_extracted_path, archive_path, password, user_id):
        """Update 7z archive with new decoded files (for when user decodes to existing 7z folder)"""
        try:
            # Get compression level
            _, _, compression_level = self.get_user_security_preferences(user_id)

            
            # Remove old archive
            if os.path.exists(archive_path):
                os.remove(archive_path)
            
            # Create new archive with updated contents
            archive_success, archive_msg = self.create_7zip_archive(
                temp_extracted_path, archive_path, password, compression_level
            )
            
            if archive_success:
                # Update last_used timestamp
                cur = self.conn.cursor()
                cur.execute(
                    "UPDATE secure_folders SET last_used = ? WHERE id = ?",
                    (datetime.now(), folder_id)
                )
                self.conn.commit()
                
                return True, "7z archive updated with new files"
            else:
                return False, f"Failed to update archive: {archive_msg}"
                
        except Exception as e:
            return False, f"Error updating 7z archive: {str(e)}"


    # ──────────────────────── SECURE FOLDERS WITH 7-ZIP ───────────────────────────
    def validate_folder_password(self, password):
        """Validate folder password - stronger requirements than user password"""
        if len(password) < 8:
            return False, "Folder password must be at least 8 characters."
        if not re.search(r"[A-Z]", password):
            return False, "Folder password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "Folder password must contain at least one lowercase letter."
        if not re.search(r"\d", password):
            return False, "Folder password must contain at least one number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Folder password must contain at least one special character."
        return True, "Valid folder password."


    # Add this to your DatabaseManager class in database.py
    def save_history(self, user_id, operation, data_type, input_path, audio_path, 
                    output_path, receiver_email, key, format_type, codec, method,
                    file_size, folder_path, success, error_message, folder_id):
        """Save encoding/decoding history"""
        try:
            # Simple logging implementation
            print(f"History: {operation} {data_type} for user {user_id}")
            return True, "History saved", None
        except Exception as e:
            print(f"History save error: {e}")
            return False, str(e), None

    # ═══════════════════════════════════════════════════════════════
# SIMPLE 7Z FOLDER MANAGEMENT (for your workflow)
# ═══════════════════════════════════════════════════════════════


    def create_secure_folder(self, user_id, folder_name, folder_path, password):
        """Create a new secure folder with 7-Zip encryption support"""
        # Validate password
        is_valid, message = self.validate_folder_password(password)
        if not is_valid:
            return False, message, None

        # Validate folder name
        if not folder_name or len(folder_name.strip()) < 1:
            return False, "Folder name cannot be empty.", None

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Get user security preferences
        use_7zip, use_hiding, compression_level = self.get_user_security_preferences(user_id)
        
        # Check 7-Zip availability
        zip_available = False
        if use_7zip:
            zip_available, zip_msg = self.check_7zip_available()

        try:
            cur = self.conn.cursor()
            
            # Determine initial settings
            encryption_method = '7zip_aes256' if (use_7zip and zip_available) else 'none'
            archive_path = folder_path + "_secure.7z" if (use_7zip and zip_available) else None
            
            cur.execute(
                """
                INSERT INTO secure_folders (user_id, folder_name, folder_path, password_hash, 
                                          is_encrypted, encryption_method, archive_path, is_hidden,
                                          created_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, folder_name.strip(), folder_path, password_hash,
                 False, encryption_method, archive_path, False,
                 datetime.now(), datetime.now()),
            )
            folder_id = cur.lastrowid
            self.conn.commit()

            # Create physical directories
            try:
                images_dir = os.path.join(folder_path, "Images")
                pdfs_dir = os.path.join(folder_path, "PDFs")
                os.makedirs(images_dir, exist_ok=True)
                os.makedirs(pdfs_dir, exist_ok=True)

                # Add placeholder files
                with open(os.path.join(images_dir, "readme.txt"), "w") as f:
                    f.write("Image files will be stored here")
                with open(os.path.join(pdfs_dir, "readme.txt"), "w") as f:
                    f.write("PDF files will be stored here")

                security_features = ["• App-level password protection"]
                
                # Apply folder hiding if enabled
                if use_hiding:
                    hide_success, hide_msg = self.hide_folder_windows(folder_path)
                    if hide_success:
                        cur.execute("UPDATE secure_folders SET is_hidden = ? WHERE id = ?", (True, folder_id))
                        security_features.append("• Hidden from File Explorer")
                        self.save_log(user_id, None, "folder_hiding", "secure_folder", 
                                    f"Folder hidden successfully: {folder_name}")
                    else:
                        self.save_log(user_id, None, "folder_hiding", "secure_folder", 
                                    f"Folder hiding failed: {folder_name} - {hide_msg}", level="WARNING")

                # Prepare 7-Zip (but don't create archive yet - user controls when)
                if use_7zip and zip_available:
                    security_features.append("• Ready for 7-Zip AES-256 encryption")
                    security_features.append("• Military-grade encryption available")
                    
                    self.save_log(user_id, None, "folder_creation", "secure_folder", 
                                f"7-Zip ready secure folder created: {folder_name}")
                elif use_7zip and not zip_available:
                    security_features.append(f"• 7-Zip encryption unavailable: {zip_msg}")
                    
                    self.save_log(user_id, None, "folder_creation", "secure_folder", 
                                f"Secure folder created without 7-Zip: {folder_name} - {zip_msg}", level="WARNING")

                self.conn.commit()

            except OSError as e:
                # Rollback database entry if folder creation fails
                cur.execute("DELETE FROM secure_folders WHERE id = ?", (folder_id,))
                self.conn.commit()
                return False, f"Failed to create folder: {str(e)}", None

            success_message = "\n".join(security_features)
            return True, success_message, folder_id

        except sqlite3.IntegrityError:
            return False, f"Folder name '{folder_name}' already exists for this user.", None
        except Exception as e:
            return False, f"Failed to create secure folder: {str(e)}", None

    def secure_folder_now(self, folder_id, password, user_id):
        """Convert folder to encrypted 7-Zip archive (user-controlled)"""
        try:
            # Get folder info
            folder_info = self.get_folder_info(folder_id, user_id)
            if not folder_info:
                return False, "Folder not found"
            
            folder_path = folder_info[2]
            folder_name = folder_info[1]
            archive_path = folder_info[7]  # archive_path column
            
            # Verify folder password
            verify_success, verify_msg = self.verify_folder_password(folder_id, password, user_id)
            if not verify_success:
                return False, f"Password verification failed: {verify_msg}"
            
            # Check if folder exists
            if not os.path.exists(folder_path):
                return False, f"Folder does not exist: {folder_path}"
            
            # Check if archive already exists and folder is gone (already secured)
            if archive_path and os.path.exists(archive_path) and not os.path.exists(folder_path):
                return False, f"Folder '{folder_name}' is already secured as encrypted archive"
            
            # Ensure archive path is set
            if not archive_path:
                archive_path = folder_path + "_secure.7z"
            
            # Get compression level
            _, _, compression_level = self.get_user_security_preferences(user_id)
            
            # Create 7-Zip archive
            archive_success, archive_msg = self.create_7zip_archive(
                folder_path, archive_path, password, compression_level
            )
            
            if archive_success:
                # Remove original folder for security
                shutil.rmtree(folder_path)
                
                # Update database
                cur = self.conn.cursor()
                cur.execute(
                    """
                    UPDATE secure_folders 
                    SET is_encrypted = ?, archive_path = ?, last_used = ?
                    WHERE id = ?
                    """,
                    (True, archive_path, datetime.now(), folder_id)
                )
                self.conn.commit()
                
                # Log the operation
                self.save_log(user_id, None, "7zip_encryption", "secure_folder", 
                            f"Folder secured as 7-Zip archive: {folder_name}")
                
                return True, f"✅ Folder '{folder_name}' secured successfully!\n📦 Archive: {os.path.basename(archive_path)}\n🎯 Double-click .7z file to access with your password!"
            else:
                return False, f"7-Zip archive creation failed: {archive_msg}"
                
        except Exception as e:
            return False, f"Error securing folder: {str(e)}"

    def access_secure_folder(self, folder_id, password, user_id):
        """Access secure folder (extract from 7-Zip if needed)"""
        try:
            # Verify folder password first
            verify_success, verify_msg = self.verify_folder_password(folder_id, password, user_id)
            if not verify_success:
                return False, f"Access denied: {verify_msg}", None
            
            folder_info = self.get_folder_info(folder_id, user_id)
            if not folder_info:
                return False, "Folder not found", None
            
            folder_path = folder_info[2]
            archive_path = folder_info[7]
            is_encrypted = folder_info[5]
            
            # If folder exists normally, just return it
            if os.path.exists(folder_path):
                return True, f"Folder accessed successfully", folder_path
            
            # If folder doesn't exist but archive does, extract it temporarily
            if archive_path and os.path.exists(archive_path) and is_encrypted:
                # Create temporary extraction directory
                temp_dir = tempfile.mkdtemp(prefix="secure_folder_")
                
                extract_success, extract_msg = self.extract_7zip_archive(
                    archive_path, temp_dir, password
                )
                
                if extract_success:
                    # Find the extracted folder
                    extracted_items = os.listdir(temp_dir)
                    if extracted_items:
                        extracted_folder = os.path.join(temp_dir, extracted_items[0])
                        if os.path.isdir(extracted_folder):
                            return True, "Archive extracted for access", extracted_folder
                    
                    return True, "Archive extracted for access", temp_dir
                else:
                    return False, f"Could not extract archive: {extract_msg}", None
            
            return False, "Folder not accessible - neither folder nor archive found", None
            
        except Exception as e:
            return False, f"Error accessing folder: {str(e)}", None

    def secure_folder_after_use(self, folder_id, password, user_id):
        """Re-secure folder after temporary access (cleanup temp extraction)"""
        try:
            # This is mainly for cleanup after temporary extractions
            # The actual folder securing is done by secure_folder_now()
            
            folder_info = self.get_folder_info(folder_id, user_id)
            if not folder_info:
                return False, "Folder not found"
            
            # Update last_used timestamp
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE secure_folders SET last_used = ? WHERE id = ?",
                (datetime.now(), folder_id)
            )
            self.conn.commit()
            
            return True, "Folder access completed"
            
        except Exception as e:
            return False, f"Error completing folder access: {str(e)}"

    def get_user_secure_folders(self, user_id):
        """Get all secure folders for a user with 7-Zip encryption status"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, folder_name, folder_path, created_at, last_used, 
                   is_encrypted, encryption_method, archive_path, is_hidden
            FROM secure_folders
            WHERE user_id = ? AND is_active = 1
            ORDER BY last_used DESC
            """,
            (user_id,),
        )
        return cur.fetchall()

    def verify_folder_password(self, folder_id, password, user_id):
        """Verify folder password and update last_used timestamp"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT password_hash FROM secure_folders
            WHERE id = ? AND user_id = ? AND is_active = 1
            """,
            (folder_id, user_id),
        )
        result = cur.fetchone()

        if not result:
            return False, "Folder not found or access denied."

        if bcrypt.checkpw(password.encode(), result[0]):
            # Update last_used timestamp
            cur.execute(
                "UPDATE secure_folders SET last_used = ? WHERE id = ?",
                (datetime.now(), folder_id),
            )
            self.conn.commit()
            return True, "Access granted."
        else:
            return False, "Incorrect folder password."

    def get_folder_info(self, folder_id, user_id):
        """Get folder information including 7-Zip encryption status"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, folder_name, folder_path, created_at, last_used, 
                   is_encrypted, encryption_method, archive_path, is_hidden
            FROM secure_folders
            WHERE id = ? AND user_id = ? AND is_active = 1
            """,
            (folder_id, user_id),
        )
        return cur.fetchone()

    def reset_folder_password(self, folder_id, user_id, new_password):
        """Reset folder password"""
        # Validate new password
        is_valid, message = self.validate_folder_password(new_password)
        if not is_valid:
            return False, message

        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE secure_folders SET password_hash = ?
            WHERE id = ? AND user_id = ? AND is_active = 1
            """,
            (password_hash, folder_id, user_id),
        )

        if cur.rowcount:
            self.conn.commit()
            return True, "Folder password reset successfully."
        else:
            return False, "Folder not found or access denied."

    def get_last_used_folder(self, user_id):
        """Get the most recently used secure folder"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, folder_name, folder_path, last_used, is_encrypted, 
                   encryption_method, archive_path, is_hidden
            FROM secure_folders
            WHERE user_id = ? AND is_active = 1
            ORDER BY last_used DESC
            LIMIT 1
            """,
            (user_id,),
        )
        return cur.fetchone()

    def get_folders_ready_for_securing(self, user_id):
        """Get folders that are ready to be secured with 7-Zip"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, folder_name, folder_path, encryption_method, archive_path
            FROM secure_folders
            WHERE user_id = ? AND is_active = 1 
              AND encryption_method = '7zip_aes256' 
              AND is_encrypted = 0
            ORDER BY last_used DESC
            """,
            (user_id,),
        )
        return cur.fetchall()

    def get_encryption_statistics(self, user_id):
        """Get encryption statistics for user's folders"""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT 
                COUNT(*) as total_folders,
                SUM(CASE WHEN is_encrypted = 1 AND encryption_method = '7zip_aes256' THEN 1 ELSE 0 END) as zip_encrypted,
                SUM(CASE WHEN is_hidden = 1 THEN 1 ELSE 0 END) as hidden_folders,
                SUM(CASE WHEN encryption_method = '7zip_aes256' AND is_encrypted = 0 THEN 1 ELSE 0 END) as ready_for_zip
            FROM secure_folders 
            WHERE user_id = ? AND is_active = 1
            """,
            (user_id,)
        )
        return cur.fetchone()

    # ──────────────────────── HISTORY & LOGS ───────────────────────────
    def save_history(
        self,
        user_id,
        operation,
        data_type,
        input_file,
        audio_file,
        output_file,
        receiver,
        key,
        audio_format=None,
        audio_codec=None,
        method=None,
        size_mb=None,
        proc_time=None,
        success=True,
        error=None,
        secure_folder_id=None,
    ):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO history (
                    user_id, operation, data_type, audio_format, audio_codec,
                    steganography_method, input_file_path, audio_file_path, output_file_path,
                    receiver_email, decryption_key, file_size_mb, processing_time_seconds,
                    success, error_message, secure_folder_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    operation,
                    data_type,
                    audio_format,
                    audio_codec,
                    method,
                    input_file,
                    audio_file,
                    output_file,
                    receiver,
                    key,
                    size_mb,
                    proc_time,
                    success,
                    error,
                    secure_folder_id,
                ),
            )
            self.conn.commit()
            return True, "History saved", cur.lastrowid
        except Exception as e:
            return False, f"Save history failed: {e}", None

    def save_log(
        self,
        user_id,
        op_id,
        op_type,
        data_type,
        message,
        audio_format=None,
        level="INFO",
    ):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO logs (user_id, operation_id, operation_type, data_type,
                                  audio_format, log_level, log_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, op_id, op_type, data_type, audio_format, level, message),
            )
            self.conn.commit()
        except Exception as e:
            print("Log save failed:", e)

    # quick helpers for history GUI ------------------------------------
    def get_encoded_records(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, data_type, audio_format, input_file_path, audio_file_path,
                   output_file_path, receiver_email, operation_date, file_size_mb
            FROM history
            WHERE user_id = ? AND operation = 'encode'
            ORDER BY operation_date DESC
            """,
            (user_id,),
        )
        return cur.fetchall()

    def get_decoded_records(self, user_id):
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT h.id, h.data_type, h.audio_format, h.audio_file_path, h.decryption_key,
                   h.output_file_path, h.operation_date, h.success, 
                   sf.folder_name, sf.is_encrypted, sf.encryption_method
            FROM history h
            LEFT JOIN secure_folders sf ON h.secure_folder_id = sf.id
            WHERE h.user_id = ? AND h.operation = 'decode'
            ORDER BY h.operation_date DESC
            """,
            (user_id,),
        )
        return cur.fetchall()

    def get_history_record(self, user_id, record_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM history WHERE id = ? AND user_id = ?", (record_id, user_id))
        return cur.fetchone()

    # generic fetch (old) ----------------------------------------------
    def get_history(self, user_id, limit=None):
        q = """
            SELECT h.id, h.operation, h.data_type, h.audio_format, h.audio_codec,
                   h.steganography_method, h.input_file_path, h.audio_file_path,
                   h.output_file_path, h.receiver_email, h.decryption_key,
                   h.file_size_mb, h.processing_time_seconds, h.success, h.operation_date,
                   sf.folder_name, sf.is_encrypted, sf.encryption_method
            FROM history h
            LEFT JOIN secure_folders sf ON h.secure_folder_id = sf.id
            WHERE h.user_id = ?
            ORDER BY h.operation_date DESC
        """
        if limit:
            q += f" LIMIT {limit}"
        cur = self.conn.cursor()
        cur.execute(q, (user_id,))
        return cur.fetchall()

    def delete_history(self, record_id, user_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM logs WHERE operation_id = ? AND user_id = ?", (record_id, user_id))
        cur.execute("DELETE FROM history WHERE id = ? AND user_id = ?", (record_id, user_id))
        if cur.rowcount:
            self.conn.commit()
            return True, "Deleted."
        return False, "Record not found."

    # ────────────────────────── EXPORTS ────────────────────────────────
    def export_user_data(self, user_id, fmt="csv", include_logs=False):
        user_data = self.get_user_details(user_id)
        if not user_data:
            return False, "User not found", None
        history = self.get_history(user_id)
        logs = []
        if include_logs:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT operation_id, operation_type, data_type, audio_format,
                       log_level, log_message, log_timestamp
                FROM logs WHERE user_id = ?
                ORDER BY log_timestamp DESC
                """,
                (user_id,),
            )
            logs = cur.fetchall()

        export_dir = "Exports"
        os.makedirs(export_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if fmt == "csv":
            return self._export_to_csv(user_data, history, logs, export_dir, ts)
        elif fmt == "json":
            return self._export_to_json(user_data, history, logs, export_dir, ts)
        else:
            return False, "Unsupported format.", None

    # CSV ----------------------------------------------------------------
    def _export_to_csv(self, user, history, logs, out_dir, ts):
        try:
            # profile csv
            pf = os.path.join(out_dir, f"profile_{ts}.csv")
            with open(pf, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Field", "Value"])
                for k, v in user["user_info"].items():
                    w.writerow([k, v])
                w.writerow([])
                w.writerow(["PREFERENCES"])
                for k, v in user["preferences"].items():
                    w.writerow([k, v])
                w.writerow([])
                w.writerow(["STATISTICS"])
                for k, v in user["statistics"].items():
                    w.writerow([k, v])

            # history csv
            hf = os.path.join(out_dir, f"history_{ts}.csv")
            with open(hf, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(
                    [
                        "ID",
                        "Operation",
                        "Data Type",
                        "Audio Format",
                        "Audio Codec",
                        "Method",
                        "Input",
                        "Audio File",
                        "Output",
                        "Receiver",
                        "Key",
                        "SizeMB",
                        "ProcTime",
                        "Success",
                        "Date",
                        "Secure Folder",
                        "Encrypted",
                        "Encryption Method",
                    ]
                )
                for rec in history:
                    w.writerow(rec)

            files = [pf, hf]
            if logs:
                lf = os.path.join(out_dir, f"logs_{ts}.csv")
                with open(lf, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(
                        [
                            "OpID",
                            "OpType",
                            "DataType",
                            "AudioFmt",
                            "Level",
                            "Message",
                            "Timestamp",
                        ]
                    )
                    for log in logs:
                        w.writerow(log)
                files.append(lf)

            return True, f"CSV export done ({len(files)} files)", files
        except Exception as e:
            return False, f"CSV export failed: {e}", None

    # JSON ---------------------------------------------------------------
    def _export_to_json(self, user, history, logs, out_dir, ts):
        try:
            import json

            blob = {
                "exported": ts,
                "user": user,
                "history": [
                    {
                        "id": r[0],
                        "operation": r[1],
                        "data_type": r[2],
                        "audio_format": r[3],
                        "audio_codec": r[4],
                        "method": r[5],
                        "input": r[6],
                        "audio_file": r[7],
                        "output_file": r[8],
                        "receiver": r[9],
                        "key": r[10],
                        "size_mb": r[11],
                        "proc_time": r[12],
                        "success": bool(r[13]),
                        "date": r[14],
                        "secure_folder": r[15] if len(r) > 15 else None,
                        "encrypted": bool(r[16]) if len(r) > 16 else False,
                        "encryption_method": r[17] if len(r) > 17 else None,
                    }
                    for r in history
                ],
            }
            if logs:
                blob["logs"] = [
                    {
                        "op_id": l[0],
                        "op_type": l[1],
                        "data_type": l[2],
                        "audio_format": l[3],
                        "level": l[4],
                        "msg": l[5],
                        "timestamp": l[6],
                    }
                    for l in logs
                ]

            jf = os.path.join(out_dir, f"data_{ts}.json")
            with open(jf, "w", encoding="utf-8") as f:
                json.dump(blob, f, indent=2, default=str)
            return True, "JSON export done", [jf]
        except Exception as e:
            return False, f"JSON export failed: {e}", None

    # ───────────────────────── SUMMARY / CLEANUP ───────────────────────
    def get_user_details(self, user_id):
        """Return profile + stats (used by export)."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, first_name, last_name, username, email,
                   created_at, last_login, is_active
            FROM users WHERE id = ?
            """,
            (user_id,),
        )
        info = cur.fetchone()
        if not info:
            return None

        cur.execute(
            """
            SELECT preferred_audio_format, default_steganography_method,
                   auto_delete_temp_files, email_notifications,
                   download_history_format, enable_7zip_encryption, 
                   enable_folder_hiding, compression_level, preferences_json, updated_at
            FROM user_preferences WHERE user_id = ?
            """,
            (user_id,),
        )
        prefs = cur.fetchone()

        cur.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END),
                   COUNT(CASE WHEN operation = 'encode' THEN 1 END),
                   COUNT(CASE WHEN operation = 'decode' THEN 1 END)
            FROM history WHERE user_id = ?
            """,
            (user_id,),
        )
        stats_raw = cur.fetchone()

        # Get 7-Zip encryption statistics
        encryption_stats = self.get_encryption_statistics(user_id)

        stats = {
            "total_operations": stats_raw[0] or 0,
            "successful_operations": stats_raw[1] or 0,
            "success_rate": round((stats_raw[1] / stats_raw[0] * 100) if stats_raw[0] else 0, 1),
            "encode_operations": stats_raw[2] or 0,
            "decode_operations": stats_raw[3] or 0,
            "total_secure_folders": encryption_stats[0] if encryption_stats else 0,
            "zip_encrypted_folders": encryption_stats[1] if encryption_stats else 0,
            "hidden_folders": encryption_stats[2] if encryption_stats else 0,
            "ready_for_zip_folders": encryption_stats[3] if encryption_stats else 0,
        }

        return {
            "user_info": {
                "id": info[0],
                "first_name": info[1],
                "last_name": info[2],
                "username": info[3],
                "email": info[4],
                "created_at": info[5],
                "last_login": info[6],
                "is_active": bool(info[7]),
            },
            "preferences": {
                "preferred_audio_format": prefs[0] if prefs else "wav",
                "default_steganography_method": prefs[1] if prefs else "lsb",
                "auto_delete_temp_files": bool(prefs[2]) if prefs else True,
                "email_notifications": bool(prefs[3]) if prefs else True,
                "download_history_format": prefs[4] if prefs else "csv",
                "enable_7zip_encryption": bool(prefs[5]) if prefs else True,
                "enable_folder_hiding": bool(prefs[6]) if prefs else False,
                "compression_level": prefs[7] if prefs else 9,
                "preferences_json": prefs[8] if prefs else None,
                "updated_at": prefs[9] if prefs else None,
            },
            "statistics": stats,
        }

    # -------------------------------------------------------------------
    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
