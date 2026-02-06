# gui/patient/patient_view.py
import tkinter as tk
from tkinter import ttk
import json
from styles import apply_app_styles, PAD_XS, PAD_SM, PAD_Y_XS, PAD_Y_SM
from config.config_loader import settings
from services.patient.patient_sync_service import PatientSyncService
from services.patient.patient_header_service import PatientHeaderService
from repositories.json.patient_json_repository import get_latest_patient_json
from repositories.patient.patient_declaration_repository import get_latest_declaration
from repositories.patient.patient_phone_repository import get_phones
from repositories.patient.patient_address_repository import get_active_address
from repositories.patient.patient_document_repository import get_active_documents
from lib.utils import format_date, format_address


class PatientView(ttk.Frame):
    def __init__(self, master, db_conn, health24_id):
        super().__init__(master)
        self.health24_id = health24_id
        self.db_conn = db_conn

        json_str = get_latest_patient_json(self.db_conn, self.health24_id)
        self.patient = json.loads(json_str) if json_str else None
        self.header_data = PatientHeaderService.build_header(self.patient) if self.patient else None

        apply_app_styles()
        self._create_layout()

    def _format_age(self, header):
        return f"{header['age_years']} р {header['age_months']} міс {header['age_days']} дн"

    def _clear_content_info(self):
        for w in self.content_info.winfo_children():
            w.destroy()

    def _render_inline_pairs(self, parent, row, pairs):
        col = 0
        for label, value in pairs:
            ttk.Label(parent, text=f"{label}:").grid(row=row, column=col, sticky="w", padx=PAD_XS, pady=PAD_Y_XS)
            col += 1
            ttk.Label(parent, text=str(value), style="DataNorm.TLabel").grid(row=row, column=col, sticky="w", padx=PAD_XS, pady=PAD_Y_XS)
            col += 1

    def _render_empty(self, parent, text):
        ttk.Label(parent, text=text, style="ErorrNorm.TLabel").grid(row=0, column=0, sticky="w", padx=PAD_XS, pady=PAD_Y_XS)

    def _create_layout(self):
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, weight=1, minsize=600)
        self.columnconfigure(2, minsize=500)
        self.rowconfigure(0, weight=1)

        self.sidebar = ttk.Labelframe(self, text="Панель навігації", padding=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=PAD_XS, pady=PAD_Y_XS)

        buttons = [
            ("Персональні дані", self.open_personal),
            ("Візити", self.open_visits),
            ("Щеплення", self.open_vaccinations),
        ]

        for text, cmd in buttons:
            ttk.Button(self.sidebar, text=text, command=cmd, style="Accent.TButton").pack(fill="x", padx=PAD_XS, pady=PAD_Y_XS)

        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        self.header = ttk.Labelframe(self.content, text="Паспортні дані", padding=0)
        self.header.grid(row=0, column=0, sticky="ew", padx=PAD_SM, pady=PAD_Y_SM)

        header_row = ttk.Frame(self.header)
        header_row.pack(fill="x", padx=PAD_XS, pady=PAD_Y_XS)

        if self.header_data:
            ttk.Label(header_row, text="Пацієнт:").pack(side="left", padx=PAD_XS)
            ttk.Label(header_row, text=self.header_data["full_name"], style="DataBig.TLabel").pack(side="left", padx=PAD_SM)

            ttk.Label(header_row, text="Дата народження:").pack(side="left", padx=PAD_XS)
            ttk.Label(header_row, text=self.header_data["birth_date"], style="DataNorm.TLabel").pack(side="left", padx=PAD_XS)

            ttk.Label(header_row, text="Стать:").pack(side="left", padx=PAD_XS)
            ttk.Label(header_row, text=self.header_data["gender"], style="DataNorm.TLabel").pack(side="left", padx=PAD_XS)

            ttk.Label(header_row, text="Вік:").pack(side="left", padx=PAD_XS)
            ttk.Label(header_row, text=self._format_age(self.header_data), style="DataNorm.TLabel").pack(side="left", padx=PAD_XS)

        self.content_info = ttk.Labelframe(self.content, text="Інформація", padding=0)
        self.content_info.grid(row=1, column=0, sticky="nsew", padx=PAD_XS, pady=PAD_Y_XS)

    def open_personal(self):
        self._clear_content_info()
        self.content_info.config(text="Персональні дані")
        declaration = get_latest_declaration(self.db_conn, self.health24_id)
        phones = get_phones(self.db_conn, self.health24_id)
        address = get_active_address(self.db_conn, self.health24_id)
        documents = get_active_documents(self.db_conn, self.health24_id)

        print(address)

        block_decl = ttk.Labelframe(self.content_info, text="Декларація", padding=0)
        block_decl.grid(row=0, column=0, sticky="ew", padx=PAD_XS, pady=PAD_Y_XS)

        current_employee_id = settings.EMPLOYEE_ID

        status_text = "Декларація відсутня"
        status_style = "ErorrNorm.TLabel"

        if declaration:
            if declaration["is_active"]:
                if current_employee_id and declaration["employee_id"] != current_employee_id:
                    status_text = "Активна (інший лікар)"
                    status_style = "ErorrNorm.TLabel"
                else:
                    status_text = "Активна"
                    status_style = "DataNorm.TLabel"
            else:
                status_text = "Завершена"
                status_style = "DataNorm.TLabel"

        ttk.Label(block_decl, text= "статус:").grid(row=0, column=0, sticky="w", padx=PAD_XS, pady=PAD_Y_XS)
        ttk.Label(block_decl, text=status_text, style=status_style).grid(row=0, column=1, sticky="w", padx=PAD_XS, pady=PAD_Y_XS)

        if declaration:
            pairs = [
                ("номер", declaration["number"] or "-"),
                ("початок", format_date(declaration["start_date"])),
                ("завершення", format_date(declaration["end_date"])),
                ("лікар", declaration["employee_name"] or "-"),
                ("підрозділ", declaration["division_name"] or "-"),
            ]
            self._render_inline_pairs(block_decl, 1, pairs)



        block_phone = ttk.Labelframe(self.content_info, text="Контакти", padding=0)
        block_phone.grid(row=1, column=0, sticky="ew", padx=PAD_XS, pady=PAD_Y_XS)

        if phones:
            pairs = [(p["type"] or "телефон", p["phone"]) for p in phones]
            self._render_inline_pairs(block_phone, 0, pairs)
        else:
            self._render_empty(block_phone, "Телефони відсутні")

        block_addr = ttk.Labelframe(self.content_info, text="Адреси", padding=0)
        block_addr.grid(row=2, column=0, sticky="ew", padx=PAD_XS, pady=PAD_Y_XS)

        value = format_address(address)

        self._render_inline_pairs(
            block_addr,
            0,
            [("адреса", value)]
        )

        block_doc = ttk.Labelframe(self.content_info, text="Документи", padding=0)
        block_doc.grid(row=3, column=0, sticky="ew", padx=PAD_XS, pady=PAD_Y_XS)

        if documents:
            for i, d in enumerate(documents):
                pairs = [
                    ("тип", d["type"] or "-"),
                    ("номер", d["number"] or "-"),
                    ("видано", format_date(d["issued_at"])),
                    ("дійсний до", format_date(d["expiration_date"])),
                    ("ким", d["issued_by"] or "-"),
                ]
                self._render_inline_pairs(block_doc, i, pairs)
        else:
            self._render_empty(block_doc, "Документи відсутні")

    def open_vaccinations(self):
        self._clear_content_info()
        self.content_info.config(text="Щеплення")

    def open_visits(self):
        self._clear_content_info()
        self.content_info.config(text="Візити")
