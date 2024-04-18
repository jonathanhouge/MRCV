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
YEARS = [
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
]

CATEGORIES = [
    "animated",
    "animated-short",
    "docs",
    "docs-short",
    "international",
    "picture",
    "short",
]


SCHEME = SCHEMES[6]
YEAR = YEARS[10]
CATEGORY = CATEGORIES[5]
WINNER = "winner here"


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

    pick_scheme_dropdown(WWTAP)
    pick_academy_year_dropdown(WWTAP)
    pick_academy_category_dropdown(WWTAP)
    run_election_button(WWTAP)


def pick_scheme_dropdown(app):
    global SCHEMES
    choice = ctk.StringVar(value=SCHEMES[6])  # initial value is "irv"

    def combobox_callback(choice):
        global SCHEME
        SCHEME = choice

    scheme = ctk.CTkComboBox(
        master=app, values=SCHEMES, variable=choice, command=combobox_callback
    )
    scheme.pack(padx=20, pady=10)
    scheme.place(relx=0.2, rely=0.5, anchor=ctk.CENTER)


def pick_academy_year_dropdown(app):
    global YEARS
    choice = ctk.StringVar(value=YEARS[10])  # initial value is "2023"

    def pick_academy_year(choice):
        global YEAR
        YEAR = choice

    scheme = ctk.CTkComboBox(
        master=app, values=YEARS, variable=choice, command=pick_academy_year
    )
    scheme.pack(padx=20, pady=10)
    scheme.place(relx=0.2, rely=0.7, anchor=ctk.CENTER)


def pick_academy_category_dropdown(app):
    global CATEGORIES
    choice = ctk.StringVar(value=CATEGORIES[5])  # initial value is "picture"

    def pick_academy_category(choice):
        global CATEGORY
        CATEGORY = choice

    scheme = ctk.CTkComboBox(
        master=app, values=CATEGORIES, variable=choice, command=pick_academy_category
    )
    scheme.pack(padx=20, pady=10)
    scheme.place(relx=0.2, rely=0.6, anchor=ctk.CENTER)


def run_election_button(app):
    global WINNER

    def run_election():
        global SCHEME
        global YEAR
        global CATEGORY
        global WINNER

        command = f"python schemes/{SCHEME}.py --election academy-ballots/{CATEGORY}/{YEAR}-{CATEGORY}-ballots.json"
        result = subprocess.check_output(command, shell=True, text=True)
        WINNER.configure(text=result)
        print(f"{SCHEME} Result: {result}")

    button = ctk.CTkButton(master=app, text="Run", command=run_election)
    button.place(relx=0.2, rely=0.8, anchor=ctk.CENTER)

    WINNER = ctk.CTkLabel(app, text=WINNER, fg_color="transparent")
    WINNER.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)


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
