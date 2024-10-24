# main.py
import tkinter as tk
from gui import EnhancedEmailScraperApp

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedEmailScraperApp(root)
    root.mainloop()