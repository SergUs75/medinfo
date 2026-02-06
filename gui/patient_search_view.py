# gui/patient_search_view.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading

from services.patient.patient_load_service import (
    PatientLoadService,
    PatientApiUnavailable,
    PatientLoadError,
)
from styles import apply_app_styles
from repositories.patient.patient_repository import search_patients
from gui.patient.patient_presenter import PatientPresenter
from services.patient.patient_sync_service import PatientSyncService
from lib.logger import setup_logger

logger = setup_logger("patient_search_view")

CURRENT_EMPLOYEE_ID = 69436
SORT_UP = " ▲"
SORT_DOWN = " ▼"


class PatientSearchView(ttk.Frame):
    def __init__(self, master, db_conn):
        super().__init__(master)
        self.db_conn = db_conn

        self.sort_column = "last_name"
        self.sort_direction = "ASC"
        self.column_titles = {}

        apply_app_styles()
        self._create_widgets()

        if self.db_conn:
            self.load_patients_to_table()

    # ================= UI =================

    def _create_widgets(self):
        self.check_var = tk.BooleanVar(value=True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # --- Паспортні дані ---
        info = ttk.Labelframe(self, text="Персональні дані", padding=0)
        info.grid(row=0, column=0, sticky="ew", padx=2, pady=2)

        ttk.Label(info, text="ПІБ").pack(side=tk.LEFT, padx=2)
        self.status_name = ttk.Label(info, style="DataBig.TLabel")
        self.status_name.pack(side=tk.LEFT)

        ttk.Label(info, text="Стать").pack(side=tk.LEFT, padx=2)
        self.status_gender = ttk.Label(info, style="DataNorm.TLabel")
        self.status_gender.pack(side=tk.LEFT)

        ttk.Label(info, text="Дата народження").pack(side=tk.LEFT, padx=2)
        self.status_birth = ttk.Label(info, style="DataNorm.TLabel")
        self.status_birth.pack(side=tk.LEFT)

        ttk.Label(info, text="Вік").pack(side=tk.LEFT, padx=2)
        self.status_age = ttk.Label(info, style="DataNorm.TLabel")
        self.status_age.pack(side=tk.LEFT)

        # --- Фільтри ---
        filters = ttk.Labelframe(self, text="Фільтри", padding=0)
        filters.grid(row=1, column=0, sticky="ew", padx=2, pady=2)

        left = ttk.Frame(filters)
        left.grid(row=0, column=0, sticky="nw", padx=2)

        ttk.Checkbutton(
            left,
            text="Активна\nдекларація",
            variable=self.check_var,
            command=self.load_patients_to_table
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(left, text="Очистити", command=self.reset_filters).grid(
            row=1, column=0, sticky="ew", pady=2
        )

        right = ttk.Frame(filters)
        right.grid(row=0, column=1, sticky="nw", padx=2)

        self.last_name = self._filter_entry(right, "Прізвище", 0)
        self.first_name = self._filter_entry(right, "Ім'я", 1)
        self.second_name = self._filter_entry(right, "По батькові", 2)

        # --- Кнопки ---
        ctrl = ttk.Labelframe(self, text="Дії", padding=0)
        ctrl.grid(row=2, column=0, sticky="ew", padx=2, pady=2)

        ttk.Button(ctrl, text="Обрати", command=self.open_selected_patient).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Label(ctrl, text="Знайдено:").pack(side=tk.LEFT, padx=2)
        self.total_label = ttk.Label(ctrl, style="DataNorm.TLabel")
        self.total_label.pack(side=tk.LEFT)

        ttk.Button(
            ctrl,
            text="Оновити з H24",
            command=self.refresh_from_api
        ).pack(side=tk.RIGHT, padx=2)

        # --- Таблиця ---
        table_frame = ttk.Frame(self)
        table_frame.grid(row=3, column=0, sticky="nsew", padx=2, pady=2)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = (
            "health24_id",
            "last_name",
            "first_name",
            "second_name",
            "birth_date",
            "gender",
            "age_y",
            "age_m",
            "age_d",
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.table["displaycolumns"] = (
            "health24_id",
            "last_name",
            "first_name",
            "second_name",
            "birth_date",
            "gender",
        )

        headings = {
            "health24_id": "ID",
            "last_name": "Прізвище",
            "first_name": "Ім'я",
            "second_name": "По батькові",
            "birth_date": "Дата нар.",
            "gender": "Стать",
        }

        for col, title in headings.items():
            self.table.heading(
                col,
                text=title,
                command=lambda c=col: self.on_sort_column(c)
            )
            self.column_titles[col] = title

        self.table.column("health24_id", width=90, anchor="center", stretch=tk.NO)
        self.table.column("last_name", width=140, stretch=tk.NO)
        self.table.column("first_name", width=140, stretch=tk.NO)
        self.table.column("second_name", width=160, stretch=tk.NO)
        self.table.column("birth_date", width=110, anchor="center", stretch=tk.NO)
        self.table.column("gender", width=80, anchor="center", stretch=tk.NO)

        self.table.grid(row=0, column=0, sticky="nsew")
        self.table.bind("<<TreeviewSelect>>", self.on_select)

    def _filter_entry(self, parent, label, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(parent, style="DataNorm.TEntry")
        entry.grid(row=row, column=1)
        entry.bind("<KeyRelease>", self.on_filter_change)
        return entry

    # ================= ЛОГІКА =================

    def load_patients_to_table(self):
        self.table.delete(*self.table.get_children())

        patients = search_patients(
            self.db_conn,
            last_name=self.last_name.get(),
            first_name=self.first_name.get(),
            second_name=self.second_name.get(),
            employee_id=CURRENT_EMPLOYEE_ID if self.check_var.get() else None,
            order_by=self.sort_column,
            direction=self.sort_direction,
        )

        for p in patients:
            v = PatientPresenter.prepare_for_viem(p)
            self.table.insert(
                "",
                tk.END,
                values=(
                    v["health24_id"],
                    v["last_name"],
                    v["first_name"],
                    v["second_name"] or "",
                    v["birth_date_view"],
                    v["gender_view"],
                    v["age_years"],
                    v["age_months"],
                    v["age_days"],
                ),
            )

        self.total_label.config(text=str(len(patients)))

    def on_sort_column(self, column):
        if self.sort_column == column:
            self.sort_direction = "DESC" if self.sort_direction == "ASC" else "ASC"
        else:
            self.sort_column = column
            self.sort_direction = "ASC"

        logger.debug(
            "Сортування: %s %s", self.sort_column, self.sort_direction
        )

        self.update_sort_indicators()
        self.load_patients_to_table()

    def update_sort_indicators(self):
        for col, title in self.column_titles.items():
            self.table.heading(col, text=title)

        arrow = SORT_UP if self.sort_direction == "ASC" else SORT_DOWN
        self.table.heading(
            self.sort_column,
            text=self.column_titles[self.sort_column] + arrow
        )

    def on_filter_change(self, *_):
        if hasattr(self, "_after"):
            self.after_cancel(self._after)
        self._after = self.after(300, self.load_patients_to_table)

    def reset_filters(self):
        self.last_name.delete(0, tk.END)
        self.first_name.delete(0, tk.END)
        self.second_name.delete(0, tk.END)
        self.check_var.set(True)
        self.load_patients_to_table()

    def refresh_from_api(self):
        logger.info("Синхронізація з H24")
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            api_client = self.winfo_toplevel().patient_api_client
            sync_service = PatientSyncService(self.db_conn, api_client)
            
            count = sync_service.sync_patient_list(str(CURRENT_EMPLOYEE_ID))
            
            self.load_patients_to_table()
            messagebox.showinfo(
                "Синхронізація завершена",
                f"Успішно оновлено {count} пацієнтів."
            )
        except Exception as e:
            logger.error(f"Помилка синхронізації: {e}")
            messagebox.showerror(
                "Помилка",
                f"Не вдалося оновити дані: {e}"
            )
        finally:
            self.configure(cursor="")

    def on_select(self, _):
        sel = self.table.selection()
        if not sel:
            return
        v = self.table.item(sel[0])["values"]
        self.status_name.config(text=f"{v[1]} {v[2]} {v[3]}")
        self.status_gender.config(text=v[5])
        self.status_birth.config(text=v[4])
        self.status_age.config(text=f"{v[6]} р {v[7]} м {v[8]} д")

    def open_selected_patient(self):
        sel = self.table.selection()
        if not sel:
            return

        health24_id = self.table.item(sel[0])["values"][0]

        logger.info(
            "Ініціація відкриття пацієнта (health24_id=%s)",
            health24_id,
        )

        try:
            PatientLoadService(
                self.db_conn,
                self.winfo_toplevel().patient_api_client
            ).load_patient(health24_id)

        except PatientApiUnavailable as e:
            messagebox.showwarning(
                "Офлайн режим",
                str(e),
            )
            return

        except PatientLoadError as e:
            messagebox.showerror(
                "Помилка завантаження пацієнта",
                str(e),
            )
            return

        logger.info(
            "Відкриття форми пацієнта (health24_id=%s)",
            health24_id,
        )

        self.winfo_toplevel().open_patient_view(health24_id)


