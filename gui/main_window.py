# gui/api_settings_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import (
    save_manual_token,
    get_token_info
)

class ApiSettingsView(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self._create_layout()

    def _create_layout(self):
        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text="Access token (DEV MODE)",
            style="DataBig.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.token_text = tk.Text(self, height=6)
        self.token_text.grid(row=1, column=0, sticky="nsew", padx=5)

        self.info_label = ttk.Label(self, text="Статус: —")
        self.info_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, sticky="e", padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="Перевірити",
            command=self.check_token
        ).pack(side="left", padx=5)

        ttk.Button(
            btn_frame,
            text="Зберегти",
            command=self.save_token
        ).pack(side="left")

    def check_token(self):
        token = self.token_text.get("1.0", "end").strip()
        info = get_token_info(token)

        if not info["valid"]:
            self.info_label.config(
                text=f"Статус: некоректний ({info['reason']})"
            )
            return

        self.info_label.config(
            text=f"Дійсний до: {info['expires_at']} ({info['remaining']})"
        )

    def save_token(self):
        token = self.token_text.get("1.0", "end").strip()
        info = get_token_info(token)

        if not info["valid"]:
            messagebox.showerror(
                "Помилка",
                f"Токен некоректний: {info['reason']}"
            )
            return

        save_manual_token(token)
        messagebox.showinfo(
            "Збережено",
            "Access token збережено"
        )
