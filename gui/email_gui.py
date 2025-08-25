import tkinter as tk
from tkinter import messagebox, ttk
from database import DatabaseManager
from email_utils import send_email, test_smtp_connection, show_password_info, validate_email_address

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
