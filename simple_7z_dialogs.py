# simple_7z_dialogs.py
import tkinter as tk
from tkinter import messagebox, filedialog
import os

# Simple theme variables - sync with main app
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

def set_theme_mode(dark_mode):
    """Set theme mode from parent application"""
    global DARK_MODE
    DARK_MODE = dark_mode

# ✅ KEY FIX: Lazy database import to prevent circular dependencies
def get_database():
    """Lazy import to avoid circular dependencies and import timing issues"""
    try:
        from database import DatabaseManager
        return DatabaseManager()
    except Exception as e:
        print(f"Database import error: {e}")
        return None

def simple_7z_folder_dialog(user_id, data_type, parent=None):
    """Main simple dialog with 3 buttons as requested"""
    dialog = tk.Toplevel(parent) if parent else tk.Toplevel()
    dialog.title("🔒 Choose Folder Option")
    dialog.geometry("500x450")  # Slightly taller for better spacing
    dialog.grab_set()
    dialog.configure(bg=get_bg_color())
    
    # Center the window
    dialog.transient(parent)
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"folder_id": None, "use_security": False, "cancelled": True, "temp_path": None, "folder_path": None}
    
    # Header
    tk.Label(dialog, text="🔒 Choose Folder Option", 
             font=("Arial", 16, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)
    
    tk.Label(dialog, text=f"Where would you like to save your decoded {data_type}?", 
             font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color()).pack(pady=10)
    
    # ✅ FIX: Use lazy database import
    db = get_database()
    if not db:
        messagebox.showerror("Database Error", "Could not connect to database", parent=dialog)
        result["cancelled"] = True
        dialog.destroy()
        return result
    
    # Check 7-Zip availability with error handling
    try:
        zip_available, zip_msg = db.check_7zip_available()
        if zip_available:
            encryption_info = "🛡️ 7-Zip AES-256 encryption available"
            encryption_color = "green"
        else:
            encryption_info = f"⚠️ 7-Zip encryption unavailable: {zip_msg}"
            encryption_color = "orange"
    except Exception as e:
        encryption_info = f"⚠️ 7-Zip check failed: {str(e)}"
        encryption_color = "red"
        zip_available = False
    
    tk.Label(dialog, text=encryption_info, 
             font=("Arial", 10), fg=encryption_color, bg=get_bg_color()).pack(pady=5)
    
    # 3 Main Buttons as requested
    buttons_frame = tk.Frame(dialog, bg=get_bg_color())
    buttons_frame.pack(pady=30, padx=20, fill="x")
    
    # Button 1: Create New 7z Folder
    def create_new_7z_folder():
        try:
            folder_id = create_new_7z_folder_dialog(dialog, user_id)
            if folder_id:
                result["folder_id"] = folder_id
                result["use_security"] = True
                result["cancelled"] = False
                dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create 7z folder: {str(e)}", parent=dialog)
    
    tk.Button(buttons_frame, text="➕ Create New 7z Folder", 
              command=create_new_7z_folder,
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
              width=25, height=2).pack(pady=10)
    tk.Label(buttons_frame, text="Create new password-protected 7z encrypted folder", 
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Button 2: Use Previous 7z Folders
    def use_previous_7z_folders():
        try:
            folder_id, temp_path = select_previous_7z_folder_dialog(dialog, user_id)
            if folder_id:
                result["folder_id"] = folder_id
                result["temp_path"] = temp_path
                result["use_security"] = True
                result["cancelled"] = False
                dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to access 7z folder: {str(e)}", parent=dialog)
    
    # Check if user has previous 7z folders with error handling
    try:
        user_7z_folders = db.get_user_7z_folders(user_id)
    except Exception as e:
        print(f"Error getting 7z folders: {e}")
        user_7z_folders = []
    
    if user_7z_folders:
        tk.Button(buttons_frame, text="📦 Use Previous 7z Folders", 
                  command=use_previous_7z_folders,
                  bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                  width=25, height=2).pack(pady=10)
        tk.Label(buttons_frame, text=f"Choose from {len(user_7z_folders)} existing 7z encrypted folders", 
                 font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    else:
        # Disabled button if no previous folders
        disabled_btn = tk.Button(buttons_frame, text="📦 Use Previous 7z Folders", 
                                state="disabled",
                                bg="gray", fg="white", font=("Arial", 12, "bold"),
                                width=25, height=2)
        disabled_btn.pack(pady=10)
        tk.Label(buttons_frame, text="No previous 7z folders found", 
                 font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Button 3: Save Without Security
    def save_without_security():
        try:
            regular_path = select_regular_folder_dialog(dialog)
            if regular_path:
                result["folder_path"] = regular_path
                result["use_security"] = False
                result["cancelled"] = False
                dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select folder: {str(e)}", parent=dialog)
    
    tk.Button(buttons_frame, text="📁 Save Without Security", 
              command=save_without_security,
              bg="#FF9800", fg="white", font=("Arial", 12, "bold"),
              width=25, height=2).pack(pady=10)
    tk.Label(buttons_frame, text="Save to regular folder without encryption", 
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Cancel button
    def cancel_dialog():
        result["cancelled"] = True
        dialog.destroy()
    
    tk.Button(dialog, text="❌ Cancel", 
              command=cancel_dialog,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=20)
    
    dialog.wait_window()
    return result

def create_new_7z_folder_dialog(parent, user_id):
    """Dialog to create new 7z encrypted folder"""
    dialog = tk.Toplevel(parent)
    dialog.title("➕ Create New 7z Folder")
    dialog.geometry("600x500")
    dialog.grab_set()
    dialog.configure(bg=get_bg_color())
    
    # Center the window
    dialog.transient(parent)
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"folder_id": None}
    
    # Header
    tk.Label(dialog, text="➕ Create New 7z Encrypted Folder", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
    
    # Folder name
    tk.Label(dialog, text="Folder Name:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(15,5), padx=20)
    name_entry = tk.Entry(dialog, width=50, font=("Arial", 11),
                         bg="white" if not DARK_MODE else get_bg_color(),
                         fg="black" if not DARK_MODE else get_fg_color())
    name_entry.pack(anchor="w", pady=5, padx=20)
    
    # Folder path
    tk.Label(dialog, text="Folder Location:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(15,5), padx=20)
    
    path_frame = tk.Frame(dialog, bg=get_bg_color())
    path_frame.pack(anchor="w", pady=5, fill="x", padx=20)
    
    path_var = tk.StringVar()
    path_entry = tk.Entry(path_frame, textvariable=path_var, width=40, font=("Arial", 11),
                         bg="white" if not DARK_MODE else get_bg_color(),
                         fg="black" if not DARK_MODE else get_fg_color())
    path_entry.pack(side=tk.LEFT, padx=(0,10))
    
    def browse_path():
        try:
            path = filedialog.askdirectory(title="Select Folder Location", parent=dialog)
            if path:
                path_var.set(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to browse folder: {str(e)}", parent=dialog)
    
    tk.Button(path_frame, text="📁 Browse", command=browse_path,
              bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    # Password
    tk.Label(dialog, text="Folder Password:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(15,5), padx=20)
    
    password_var = tk.StringVar()
    password_entry = tk.Entry(dialog, width=30, show="*", textvariable=password_var, font=("Arial", 11),
                             bg="white" if not DARK_MODE else get_bg_color(),
                             fg="black" if not DARK_MODE else get_fg_color())
    password_entry.pack(anchor="w", pady=5, padx=20)
    
    # Status label
    status_label = tk.Label(dialog, text="", font=("Arial", 10), bg=get_bg_color())
    status_label.pack(pady=10)
    
    def create_folder():
        folder_name = name_entry.get().strip()
        folder_path = path_var.get().strip()
        password = password_var.get()
        
        if not folder_name:
            status_label.config(text="❌ Please enter a folder name", fg="red")
            name_entry.focus_set()
            return
        if not folder_path:
            status_label.config(text="❌ Please select a folder path", fg="red")
            return
        if not password:
            status_label.config(text="❌ Please enter a password", fg="red")
            password_entry.focus_set()
            return
        
        # Create full folder path
        full_path = os.path.join(folder_path, folder_name)
        
        status_label.config(text="🔄 Creating 7z encrypted folder...", fg="blue")
        dialog.update()
        
        try:
            # ✅ FIX: Use lazy database import
            db = get_database()
            if not db:
                status_label.config(text="❌ Database connection failed", fg="red")
                return
                
            success, message, folder_id = db.create_simple_7z_folder(user_id, folder_name, full_path, password)
            
            if success:
                status_label.config(text="✅ 7z folder created successfully!", fg="green")
                result["folder_id"] = folder_id
                messagebox.showinfo("✅ Success", message, parent=dialog)
                dialog.destroy()
            else:
                status_label.config(text=f"❌ {message}", fg="red")
        except Exception as e:
            status_label.config(text=f"❌ Error: {str(e)}", fg="red")
    
    # Buttons
    button_frame = tk.Frame(dialog, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="🛡️ Create 7z Folder", command=create_folder,
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    # Focus on name entry
    dialog.after(100, lambda: name_entry.focus_set())
    
    dialog.wait_window()
    return result["folder_id"]

def select_previous_7z_folder_dialog(parent, user_id):
    """Dialog to select from existing 7z folders"""
    dialog = tk.Toplevel(parent)
    dialog.title("📦 Select 7z Folder")
    dialog.geometry("650x450")
    dialog.grab_set()
    dialog.configure(bg=get_bg_color())
    
    # Center the window
    dialog.transient(parent)
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"folder_id": None, "temp_path": None}
    
    tk.Label(dialog, text="📦 Select 7z Encrypted Folder", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
    
    # ✅ FIX: Use lazy database import with error handling
    db = get_database()
    if not db:
        messagebox.showerror("Database Error", "Could not connect to database", parent=dialog)
        dialog.destroy()
        return None, None
    
    try:
        user_7z_folders = db.get_user_7z_folders(user_id)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get 7z folders: {str(e)}", parent=dialog)
        dialog.destroy()
        return None, None
    
    if not user_7z_folders:
        tk.Label(dialog, text="No 7z folders found.", 
                font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color()).pack(expand=True)
        tk.Button(dialog, text="❌ Close", command=dialog.destroy,
                  bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=20)
        dialog.wait_window()
        return None, None
    
    # Folders list
    tk.Label(dialog, text=f"Choose from {len(user_7z_folders)} encrypted folders:", 
             font=("Arial", 11), bg=get_bg_color(), fg=get_fg_color()).pack(pady=10)
    
    # Listbox with scrollbar
    list_frame = tk.Frame(dialog, bg=get_bg_color())
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    listbox = tk.Listbox(list_frame, height=10, font=("Arial", 10),
                        bg="white" if not DARK_MODE else get_bg_color(),
                        fg="black" if not DARK_MODE else get_fg_color())
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Populate listbox
    for folder in user_7z_folders:
        folder_name = folder[1]
        created_date = folder[4][:10] if len(folder) > 4 and folder[4] else "Unknown"
        last_used = folder[5][:10] if len(folder) > 5 and folder[5] else "Never"
        
        display_text = f"🛡️ {folder_name} | Created: {created_date} | Last used: {last_used}"
        listbox.insert(tk.END, display_text)
    
    def select_folder():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a folder.", parent=dialog)
            return
        
        try:
            selected_folder = user_7z_folders[selection[0]]
            folder_id = selected_folder[0]
            folder_name = selected_folder[1]
            
            # Ask for password
            password = ask_7z_password(dialog, folder_name)
            if not password:
                return
            
            # Verify access and extract
            success, message, verified_archive_path = db.verify_7z_folder_access(folder_id, password, user_id)
            if not success:
                messagebox.showerror("Access Denied", message, parent=dialog)
                return
            
            # Extract to temp directory
            extract_success, extract_message, temp_path = db.extract_7z_for_decoding(folder_id, password, user_id)
            if extract_success:
                result["folder_id"] = folder_id
                result["temp_path"] = temp_path
                messagebox.showinfo("✅ Success", f"7z folder accessed successfully!\n{extract_message}", parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Extraction Failed", extract_message, parent=dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select folder: {str(e)}", parent=dialog)
    
    # Buttons
    button_frame = tk.Frame(dialog, bg=get_bg_color())
    button_frame.pack(pady=15)
    
    tk.Button(button_frame, text="✅ Select Folder", command=select_folder,
              bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
    
    dialog.wait_window()
    return result["folder_id"], result["temp_path"]

def ask_7z_password(parent, folder_name):
    """Simple password dialog for 7z access"""
    dialog = tk.Toplevel(parent)
    dialog.title("🔐 Enter Password")
    dialog.geometry("400x200")
    dialog.grab_set()
    dialog.configure(bg=get_bg_color())
    
    # Center the window
    dialog.transient(parent)
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"password": None}
    
    tk.Label(dialog, text=f"🔐 Enter Password", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=15)
    
    tk.Label(dialog, text=f"For 7z folder: {folder_name}", 
             font=("Arial", 10), bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
    password_var = tk.StringVar()
    password_entry = tk.Entry(dialog, width=30, show="*", textvariable=password_var, font=("Arial", 11))
    password_entry.pack(pady=15)
    
    def submit_password():
        if password_var.get().strip():
            result["password"] = password_var.get()
            dialog.destroy()
        else:
            messagebox.showwarning("Empty Password", "Please enter a password.", parent=dialog)
    
    password_entry.bind('<Return>', lambda e: submit_password())
    password_entry.focus_set()
    
    # Buttons
    button_frame = tk.Frame(dialog, bg=get_bg_color())
    button_frame.pack(pady=15)
    
    tk.Button(button_frame, text="🔓 Unlock", command=submit_password,
              bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
    
    dialog.wait_window()
    return result["password"]

def select_regular_folder_dialog(parent):
    """Simple folder selection for non-secure saving"""
    try:
        path = filedialog.askdirectory(title="Select Folder to Save Files", parent=parent)
        return path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to select folder: {str(e)}", parent=parent)
        return None

# ✅ ADDITION: Helper function for old GUI compatibility
def get_simple_folder_options():
    """Return available folder options for integration"""
    return {
        "create_new": "Create New 7z Folder",
        "use_previous": "Use Previous 7z Folders", 
        "no_security": "Save Without Security"
    }
