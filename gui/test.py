# test_decode_gui.py
import tkinter as tk
from decode_gui import decode_dialog

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    print("Creating decode dialog...")
    decode_dialog(user_id=1)  # Use a test user_id
    
    print("Starting mainloop...")
    root.mainloop()
