# gui/main_menu.py
import tkinter as tk
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import MainWindow 


class MainMenu(tk.Menu):
    def __init__(self, master, on_open_patient_search):
        super().__init__(master)
        self.on_open_patient_search = on_open_patient_search

        self.file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Файл", menu=self.file_menu)

        self.file_menu.add_command(
            label="Пошук пацієнта", command=self.on_open_patient_search)
        
        self.file_menu.add_separator() 
        
        self.file_menu.add_command(label="Вихід", command=master.on_close)

        self.help_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Допомога", menu=self.help_menu)

        self.help_menu.add_command(label="Про програму", command=self._show_about)

        master.config(menu=self)

    def _show_about(self):

        about_window = tk.Toplevel()
        about_window.title("Про програму")
        WINDOW_WIDTH = 350
        WINDOW_HEIGHT = 180
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        position_top = int(screen_height / 2 - WINDOW_HEIGHT / 2)
        position_right = int(screen_width / 2 - WINDOW_WIDTH / 2)
        about_window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{position_right}+{position_top}')
        about_window.resizable(False, False)         
        tk.Label(about_window, text="Помічник Сімейного Лікаря\nВерсія 1.0").pack(pady=20, padx=20)
        tk.Button(about_window, text="OK", command=about_window.destroy).pack()
        about_window.transient(self.master)
        about_window.grab_set()
        self.master.wait_window(about_window)