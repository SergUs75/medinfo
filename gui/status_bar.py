# gui_status_updater.py

from tkinter import ttk
from typing import Optional


class GuiStatusUpdater:
    def __init__(
        self,
        db_label: Optional[ttk.Label],
        api_button: Optional[ttk.Button]
    ):
        self.db_label = db_label
        self.api_button = api_button

    # ===== DB =====

    def set_db_connected(self, db_name: str = "medinfo.db"):
        if not self.db_label:
            return

        self.db_label.config(
            text=f"БД: {db_name}",
            foreground="green"
        )

    def set_db_error(self, message: str):
        if not self.db_label:
            return

        self.db_label.config(
            text=f"БД: помилка ({message})",
            foreground="red"
        )

    # ===== API =====

    def set_api_not_checked(self):
        if not self.api_button:
            return

        self.api_button.config(
            text="API: не перевірено",
            style="Api.Neutral.TButton"
        )

    def set_api_token_valid(self, exp_str: str, left_str: str):
        if not self.api_button:
            return

        self.api_button.config(
            text=f"API: до {exp_str} ({left_str})",
            style="Api.Ok.TButton"
        )

    def set_api_error(self, message: str):
        if not self.api_button:
            return

        self.api_button.config(
            text=f"API: помилка ({message})",
            style="Api.Error.TButton"
        )
