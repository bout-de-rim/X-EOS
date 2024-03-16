import tkinter as tk
from tkinter import scrolledtext
import ctypes
import platform
import logging
import threading

class GUIHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.see(tk.END)

# Assurez-vous d'initialiser votre GUI avant d'ajouter le GUIHandler
def run_gui(logger):
    root = tk.Tk()
    root.title("X-EOS GUI")
    log_area = scrolledtext.ScrolledText(root, width=40, height=10)
    log_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Création et ajout du GUIHandler au logger
    gui_handler = GUIHandler(log_area)
    try:
        gui_handler.setFormatter(formatter)  # Utiliser le même formatteur que la console
    except NameError:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        gui_handler.setFormatter(formatter)
    logger.addHandler(gui_handler)

    
    root.mainloop()
