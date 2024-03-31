import customtkinter as ctk
from functions import *

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.geometry("400x240")
app.title("MRCV - Start Menu")
app.resizable(False, False)

create_start_menu(app)

app.mainloop()
