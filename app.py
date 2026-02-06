# main_assistant_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from db.db_initializer import initialize_db
from gui.main_menu import MainMenu
from gui.patient.patient_view import PatientView
from gui.patient_search_view import PatientSearchView
from gui.status_bar import GuiStatusUpdater
from config.config_loader import settings
from api.health24.patient_client import PatientClient
from auth_manager import get_access_token

class MainWindow(tk.Tk):
    def __init__(self, db_conn: Optional[object]):
        super().__init__()
        self.db_conn = db_conn
        #self.status_bar_component: Optional[StatusBarView] = None
        self.status_manager: Optional[GuiStatusUpdater] = None

        if self.db_conn is None:
            messagebox.showerror(
                "Критична помилка",
                "Неможливо підключитися до бази даних"
            )
            self.destroy()
            return

        token = get_access_token()
        if not token:
            messagebox.showerror(
                "Критична помилка",
                "Неможливо отримати access token для роботи з API"
            )
            self.destroy()
            return

        self.patient_api_client = PatientClient()

        self.title("Помічник Сімейного Лікаря")
        self.state("zoomed")

        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True)

        #self.status_bar_component = StatusBarView(self)
        #db_label, api_button = self.status_bar_component.get_widgets()
        #self.status_manager = GuiStatusUpdater(db_label, api_button)
        #self.status_manager.set_db_connected()
        #self.status_manager.set_api_not_checked()

        menu = MainMenu(self, on_open_patient_search=self.open_patient_search)
        self.config(menu=menu)

        self.update_idletasks()

    def on_close(self):
        if self.db_conn:
            self.db_conn.close()
        self.destroy()

    def _clear_content(self):
        for child in self.content_frame.winfo_children():
            child.destroy()

    def open_patient_search(self):
        self._clear_content()
        view = PatientSearchView(
            master=self.content_frame,
            db_conn=self.db_conn
        )
        view.pack(fill="both", expand=True)

    def open_patient_view(self, health24_id: int):
        self._clear_content()
        view = PatientView(
            master=self.content_frame,
            db_conn=self.db_conn,
            health24_id=health24_id
        )
        view.pack(fill="both", expand=True)


def main():
    connection = initialize_db()
    app = MainWindow(connection)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
