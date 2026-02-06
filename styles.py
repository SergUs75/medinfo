# styles.py
from tkinter import ttk

PAD_XS = 0
PAD_SM = 2
PAD_MD = 4

PAD_Y_XS = 0
PAD_Y_SM = 2
PAD_Y_MD = 4

def apply_app_styles():
    style = ttk.Style()
    style.configure("DataNorm.TLabel", foreground="blue")
    style.configure("ErorrNorm.TLabel", foreground="red")
    style.configure("DataBig.TLabel", foreground="blue", font=(None, 9))
    style.configure("DataNorm.TEntry", foreground="blue")
    style.configure("TLabelframe.Label", font=("Arial", 8, "bold"), foreground="black")
    style.configure("Treeview.Heading", background="amber", foreground="black", relief="solid", borderwidth=1, font=("Arial", 8, "bold"))
    style.configure("Api.Ok.TButton")
    style.configure("Api.Error.TButton")
    style.configure("Api.Neutral.TButton")
