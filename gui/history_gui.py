import tkinter as tk
from tkinter import messagebox, ttk
import os
import time
import shutil
import zipfile
from datetime import datetime
import tkinter.filedialog as fd
from database import DatabaseManager
from gui.email_gui import export_user_data_dialog

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
                # Leave other colored buttons (like #f44336, etc.) unchanged
            elif widget_class == 'Text':
                if DARK_MODE:
                    widget.configure(bg=bg, fg=fg, insertbackground=fg)
                else:
                    widget.configure(bg="white", fg="black", insertbackground="black")
            
            # Recursively apply to children
            for child in widget.winfo_children():
                update_widget(child)
                
        except Exception:
            pass
    
    update_widget(window)


def history_dialog(user_id):
    """Enhanced history dialog with separate encoded/decoded sections, download options, and simple theme management"""
    db = DatabaseManager()
    history_window = tk.Toplevel()
    history_window.title("Operation History")
    history_window.geometry("1200x600")
    history_window.grab_set()
    history_window.configure(bg=get_bg_color())
    
    # Create simple theme menu
    menubar = tk.Menu(history_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", history_window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", history_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    history_window.config(menu=menubar)
    
    tk.Label(history_window, text="📚 Your Audio Steganography History", 
             font=("Arial", 16, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=10)
    
    # Create notebook for tabs
    notebook = ttk.Notebook(history_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Create a style for ttk widgets to match theme
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TNotebook', background=get_bg_color(), borderwidth=0)
    style.configure('TNotebook.Tab', background=get_bg_color(), foreground=get_fg_color(), 
                   padding=[10, 5], focuscolor='none')
    style.map('TNotebook.Tab', background=[('selected', get_highlight_color())])
    
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
    button_frame = tk.Frame(history_window, bg=get_bg_color())
    button_frame.pack(pady=10)
    
    def refresh_all_views():
        # Refresh both tabs
        for widget in encoded_frame.winfo_children():
            widget.destroy()
        for widget in decoded_frame.winfo_children():
            widget.destroy()
        
        create_encoded_view(encoded_frame, user_id, db)
        create_decoded_view(decoded_frame, user_id, db)
    
    tk.Button(button_frame, text="🔄 Refresh All", 
              command=refresh_all_views,
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="📊 Export All Data", 
              command=lambda: export_user_data_dialog(user_id),
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame, text="❌ Close", 
              command=history_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)


def create_encoded_view(parent_frame, user_id, db):
    """Create the encoded data view with theme support"""
    tk.Label(parent_frame, text="📤 Encoded Data Records", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
    # Create treeview for encoded data
    columns = ("ID", "Data Type", "Audio Format", "Input File", "Audio Used", 
               "Output File", "Recipient Email", "Date", "Size (MB)")
    
    # Configure treeview style
    style = ttk.Style()
    style.configure("Treeview", background=get_bg_color(), foreground=get_fg_color(), 
                   fieldbackground=get_bg_color(), borderwidth=0)
    style.configure("Treeview.Heading", background=get_button_bg(), 
                   foreground=get_button_fg(), relief="flat")
    style.map("Treeview", background=[('selected', get_highlight_color())])
    
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
    """Create the decoded data view with theme support"""
    tk.Label(parent_frame, text="📥 Decoded Data Records", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
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
    """Show context menu for encoded records with theme support"""
    try:
        item = tree.selection()[0]
        values = tree.item(item, "values")
        record_id = values[0]
        
        context_menu = tk.Menu(tree, tearoff=0, bg=get_bg_color(), fg=get_fg_color(),
                              activebackground=get_highlight_color(), activeforeground="white")
        
        context_menu.add_command(
            label="📄 Show Details",
            command=lambda: show_record_details(record_id, user_id, db)
        )
        
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
    """Show context menu for decoded records with theme support"""
    try:
        item = tree.selection()[0]
        values = tree.item(item, "values")
        record_id = values[0]
        
        context_menu = tk.Menu(tree, tearoff=0, bg=get_bg_color(), fg=get_fg_color(),
                              activebackground=get_highlight_color(), activeforeground="white")
        
        context_menu.add_command(
            label="📄 Show Details",
            command=lambda: show_record_details(record_id, user_id, db)
        )
        
        context_menu.add_separator()
        
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
        save_path = fd.asksaveasfilename(
            title="Save Complete Record",
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialname=f"{record_type}_record_{record_id}_{record[2]}_{int(time.time())}.zip"
        )
        
        if not save_path:
            return
        
        # Create ZIP file with all available files
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
    """Show detailed information about a record with simple theme management"""
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
        details_window.configure(bg=get_bg_color())
        
        # Create simple theme menu
        menubar = tk.Menu(details_window)
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="☀️ Light Mode", 
                              command=lambda: switch_theme("light", details_window))
        theme_menu.add_command(label="🌙 Dark Mode", 
                              command=lambda: switch_theme("dark", details_window))
        menubar.add_cascade(label="Theme", menu=theme_menu)
        details_window.config(menu=menubar)
        
        # Create scrollable text widget
        text_frame = tk.Frame(details_window, bg=get_bg_color())
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Courier", 10),
                             bg="white" if not DARK_MODE else get_bg_color(), 
                             fg="black" if not DARK_MODE else get_fg_color(), 
                             insertbackground="black" if not DARK_MODE else get_fg_color())
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
    """Delete a record with confirmation dialog"""
    try:
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this {record_type} record?\n\n"
            f"Record ID: {record_id}\n"
            f"This action cannot be undone."
        )
        
        if result:
            success, message = db.delete_history(record_id, user_id)
            if success:
                messagebox.showinfo("Success", message)
                # Refresh the tree view
                if record_type == "encoded":
                    load_encoded_data(tree, user_id, db)
                else:
                    load_decoded_data(tree, user_id, db)
            else:
                messagebox.showerror("Error", message)
                
    except Exception as e:
        messagebox.showerror("Error", f"Delete failed: {str(e)}")
