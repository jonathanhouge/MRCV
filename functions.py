import customtkinter as ctk
import threading
import subprocess


MODE = True
APP = ""
MRCV = False
WWTAP = False
ERRORS = []

SCHEMES = [
    "baldwin",
    "black",
    "borda",
    "bucklin",
    "coombs",
    "copeland",
    "irv",
    "minimax",
    "nanson",
    "river",
    "rouse",
    "schulze",
    "smith_irv",
    "tideman",
    "topmost_median_rank",
]


def create_start_menu(app):
    global APP
    APP = app

    button = ctk.CTkButton(
        master=app, text="What Wouldn't the Academy Pick?", command=start_wwtap
    )
    button.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
    button = ctk.CTkButton(master=app, text="MRCV Game", command=start_mrcv)
    button.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

    button = ctk.CTkButton(
        master=app, text="Light / Dark Mode", command=change_app_appearance
    )
    button.place(relx=0.2, rely=0.9, anchor=ctk.CENTER)


def change_app_appearance():
    global MODE
    if MODE:
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")
    MODE = not MODE


def start_mrcv():
    global MRCV
    global APP

    if MRCV and MRCV.winfo_exists():
        error_window("Already open.")
        threading.Timer(2.0, destroyError).start()
        return

    if WWTAP and WWTAP.winfo_exists():
        error_window("Other window open.")
        threading.Timer(2.0, destroyError).start()
        return

    MRCV = ctk.CTkToplevel(APP)
    MRCV.title("Movie-Ranked-Choice-Voting Game")
    MRCV.geometry("500x500")
    MRCV.resizable(False, False)
    MRCV.attributes("-topmost", True)


def start_wwtap():
    global WWTAP
    global APP

    if WWTAP and WWTAP.winfo_exists():
        error_window("Already open.")
        threading.Timer(2.0, destroyError).start()
        return

    if MRCV and MRCV.winfo_exists():
        error_window("Other window open.")
        threading.Timer(2.0, destroyError).start()
        return

    WWTAP = ctk.CTkToplevel(APP)
    WWTAP.title("What Wouldn't The Academy Pick?")
    WWTAP.geometry("500x500")
    WWTAP.resizable(False, False)
    WWTAP.attributes("-topmost", True)

    global SCHEMES

    chosen_scheme = ctk.StringVar(value=SCHEMES[6])  # set initial value

    combobox = ctk.CTkComboBox(
        master=WWTAP,
        values=SCHEMES,
        variable=chosen_scheme,
    )
    combobox.pack(padx=20, pady=10)

    # reminder to make 'copeland' {chosen_scheme} and to make 'rcv-schemes' -> 'schemes' and add brackets in ballots
    command = f"py schemes/copeland.py --elections academy-ballots/animated-short/2013-animated-short-ballots.json"
    result = subprocess.check_output(command, shell=True, text=True)
    print(result)


def error_window(message):
    global APP
    global ERRORS

    error = ctk.CTkToplevel(APP)
    error.title("ERROR WINDOW")
    error.geometry("200x100")
    error.resizable(False, False)
    error.attributes("-topmost", True)

    label = ctk.CTkLabel(error, text=message, fg_color="transparent")
    label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    ERRORS.append(error)


def destroyError():
    global ERRORS

    ERRORS[0].destroy()
    ERRORS.pop(0)
