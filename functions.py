import customtkinter as ctk
import threading
import subprocess
from PIL import Image
from bs4 import BeautifulSoup
import requests
import json
import webbrowser


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
WINNER_URL = "https://letterboxd.com/film/404-1/"
ACTUAL_WINNER = "actual winner here"
ACTUAL_NOMINEES = "actual nominees here"


# main menu
def create_start_menu(app):
    global APP
    APP = app

    title = ctk.CTkLabel(
        app,
        text="MRCV",
        font=("", 50, "bold"),
    )
    title.place(relx=0.5, rely=0.15, anchor=ctk.CENTER)

    wwtap = ctk.CTkButton(
        master=app, text="What Wouldn't the Academy Pick?", command=start_wwtap
    )
    wwtap.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
    mrcv_game = ctk.CTkButton(master=app, text="MRCV Game", command=start_mrcv)
    mrcv_game.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

    light_dark_mode = ctk.CTkButton(
        master=app, text="Light / Dark Mode", command=change_app_appearance
    )
    light_dark_mode.place(relx=0.2, rely=0.9, anchor=ctk.CENTER)

    tutorial = ctk.CTkButton(master=app, text="Tutorial", command=tutorial_dialogue)
    tutorial.place(relx=0.8, rely=0.9, anchor=ctk.CENTER)


# dark / light mode button command
def change_app_appearance():
    global MODE
    if MODE:
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")
    MODE = not MODE


# tutorial button command
def tutorial_dialogue():
    global APP

    tutorial = ctk.CTkToplevel(APP)
    tutorial.title("Tutorial")
    tutorial.geometry("400x200")
    tutorial.resizable(False, False)
    tutorial.attributes("-topmost", True)

    tutorial_text = (
        "Welcome to MRCV! Developed by Jonathan Houge for CSC 496.\n\n"
        "WWTAP: A chance for Letterboxd users to vote for the oscars! Data\nhas been gathered for seven categories over a decade. Pick a RCV\nscheme and see which movie would've won compared to what did.\n\n"
        "MRCV Game: A chance to test your RCV and movie knowledge! Input\na valid Letterboxd URL or pick one of our suggested, we'll scrape\nrandom films from it and create ballots, then you choose which\ncandidate you think will win given the films and a random RCV\nscheme. How many can you get right!?"
    )

    label = ctk.CTkTextbox(tutorial, width=400, height=200, corner_radius=0)
    label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
    label.insert("0.0", tutorial_text)


## MRCV GAME RELATED FUNCTIONS ##


# main functionality for mrcv game
def start_mrcv():
    global MRCV
    global APP

    # ensure only one window is open at a time
    if MRCV and MRCV.winfo_exists():
        error_window("Already open.", APP)
        threading.Timer(2.0, destroyError).start()
        return

    if WWTAP and WWTAP.winfo_exists():
        error_window("Other window open.", APP)
        threading.Timer(2.0, destroyError).start()
        return

    MRCV = ctk.CTkToplevel(APP)
    MRCV.title("Movie-Ranked-Choice-Voting Game")
    MRCV.geometry("500x500")
    MRCV.resizable(False, False)
    MRCV.attributes("-topmost", True)


## WWTAP RELATED FUNCTIONS ##


# main functionality for wwtap
def start_wwtap():
    global WWTAP
    global APP

    # ensure only one window is open at a time
    if WWTAP and WWTAP.winfo_exists():
        error_window("Already open.", APP)
        threading.Timer(2.0, destroyError).start()
        return

    if MRCV and MRCV.winfo_exists():
        error_window("Other window open.", APP)
        threading.Timer(2.0, destroyError).start()
        return

    WWTAP = ctk.CTkToplevel(APP)
    WWTAP.title("What Wouldn't The Academy Pick?")
    WWTAP.geometry("600x500")
    WWTAP.resizable(False, False)
    WWTAP.attributes("-topmost", True)

    # backdrops
    actions_frame = ctk.CTkFrame(master=WWTAP, width=200, height=200)
    actions_frame.place(relx=0.2, rely=0.65, anchor=ctk.CENTER)

    academy_frame = ctk.CTkFrame(master=WWTAP, width=320, height=200)
    academy_frame.place(relx=0.7, rely=0.65, anchor=ctk.CENTER)

    # set up other buttons / functionality
    pick_scheme_dropdown(WWTAP)
    pick_academy_year_dropdown(WWTAP)
    pick_academy_category_dropdown(WWTAP)
    run_election_button(WWTAP)
    academy_results_text(WWTAP)


# rcv scheme dropdown & associated command
def pick_scheme_dropdown(app):
    global SCHEMES
    choice = ctk.StringVar(value=SCHEMES[6])  # initial value is "irv"

    def combobox_callback(choice):
        global SCHEME
        SCHEME = choice

    scheme = ctk.CTkComboBox(
        master=app,
        values=SCHEMES,
        variable=choice,
        command=combobox_callback,
    )
    scheme.pack(padx=20, pady=10)
    scheme.place(relx=0.2, rely=0.5, anchor=ctk.CENTER)


# year dropdown & associated command
def pick_academy_year_dropdown(app):
    global YEARS
    choice = ctk.StringVar(value=YEARS[10])  # initial value is "2023"

    def pick_academy_year(choice):
        global YEAR
        YEAR = choice

    year = ctk.CTkComboBox(
        master=app,
        values=YEARS,
        variable=choice,
        command=pick_academy_year,
    )
    year.pack(padx=20, pady=10)
    year.place(relx=0.2, rely=0.7, anchor=ctk.CENTER)


# category dropdown & associated command
def pick_academy_category_dropdown(app):
    global CATEGORIES
    choice = ctk.StringVar(value=CATEGORIES[5])  # initial value is "picture"

    def pick_academy_category(choice):
        global CATEGORY
        CATEGORY = choice

    category = ctk.CTkComboBox(
        master=app,
        values=CATEGORIES,
        variable=choice,
        command=pick_academy_category,
    )
    category.pack(padx=20, pady=10)
    category.place(relx=0.2, rely=0.6, anchor=ctk.CENTER)


# run election button & associated buttons / functionality
def run_election_button(app):
    global WINNER

    # run election button and command
    def run_election():
        global SCHEME
        global YEAR
        global CATEGORY
        global WINNER
        global WINNER_URL
        global ACTUAL_WINNER

        command = f"python schemes/{SCHEME}.py --election academy-ballots/{CATEGORY}/{YEAR}-{CATEGORY}-ballots.json"
        winner = "<ERROR>"
        winner_poster = "posters/AMBIGUOUS.jpg"
        WINNER_URL = "https://letterboxd.com/film/404-1/"

        # if the command fails, we have a runtime error - simply report it and move on
        try:
            result = subprocess.check_output(command, shell=True, text=True)
            winner = result.strip()  # trailing whitespace for some reason?

            # go and get the winning movie's poster
            if winner != "<AMBIGUOUS>":
                with open(
                    f"academy-scraping/{CATEGORY}/{YEAR}-{CATEGORY}.json",
                    "r",
                    encoding="utf-8",
                ) as jsonf:
                    candidates = json.load(jsonf)
                    film_url = next(
                        (
                            film["url"]
                            for film in candidates
                            if film["Film_title"] == winner
                        )
                    )

                # https://stackoverflow.com/questions/73803684/trying-to-scrape-posters-from-letterboxd-python
                filmget = requests.get(film_url)
                film_soup = BeautifulSoup(filmget.text, "html.parser")
                script_w_data = film_soup.select_one(
                    'script[type="application/ld+json"]'
                )
                json_obj = json.loads(
                    script_w_data.text.split(" */")[1].split("/* ]]>")[0]
                )

                posterget = requests.get(json_obj["image"]).content
                f = open("posters/winner.jpg", "wb")
                f.write(posterget)
                f.close()

                winner_poster = "posters/winner.jpg"
                WINNER_URL = film_url

        except Exception as e:
            print(f"Error: f{e}")
            error_window("Runtime Error. :(", app)
            threading.Timer(2.0, destroyError).start()

        # update winner, either someone won or 'ambiguous' was returned
        winner_image = ctk.CTkImage(
            Image.open(f"{winner_poster}"),
            size=(100, 150),
        )

        WINNER.configure(text=winner, image=winner_image)

        # update academy's results
        with open(
            f"academy-scraping/{CATEGORY}/oscar-winners-{CATEGORY}.json",
            "r",
            encoding="utf-8",
        ) as jsonf:
            ceremonies = json.load(jsonf)
            actual_winner = next(
                (
                    ceremony["winner"]
                    for ceremony in ceremonies
                    if str(ceremony["year"]) == YEAR
                )
            )

            actual_nominees_list = next(
                (
                    ceremony["nominees"]
                    for ceremony in ceremonies
                    if str(ceremony["year"]) == YEAR
                )
            )

            actual_nominees = "Actual Nominees:\n"
            for actual_nominee in actual_nominees_list:
                actual_nominees += actual_nominee + "\n"

        ACTUAL_WINNER.configure(text=f"Actual Winner: \n{actual_winner}")
        ACTUAL_NOMINEES.configure(text=actual_nominees)

    run_button = ctk.CTkButton(master=app, text="Run", command=run_election)
    run_button.place(relx=0.2, rely=0.8, anchor=ctk.CENTER)

    # set up our winner button - start as AMBIGUOUS, assign to global so we can update it later
    # button allows us to go to the letterboxd page for the winner
    def winner_button():
        global WINNER_URL
        webbrowser.open(WINNER_URL)

    button_image = ctk.CTkImage(
        Image.open("posters/AMBIGUOUS.jpg"),
        size=(100, 150),
    )

    WINNER = ctk.CTkButton(
        master=app,
        text=f"{WINNER}",
        image=button_image,
        command=winner_button,
    )
    WINNER.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)


# academy results (are updated in 'run_election')
def academy_results_text(app):
    global ACTUAL_WINNER
    global ACTUAL_NOMINEES

    ACTUAL_WINNER = ctk.CTkLabel(
        app,
        text="actual winner here",
        text_color=("black", "white"),
        fg_color=("#e8e4e4", "#212121"),
    )
    ACTUAL_WINNER.place(relx=0.7, rely=0.5, anchor=ctk.CENTER)

    ACTUAL_NOMINEES = ctk.CTkLabel(
        app,
        text="actual nominees here",
        text_color=("black", "white"),
        fg_color=("#e8e4e4", "#212121"),
    )
    ACTUAL_NOMINEES.place(relx=0.7, rely=0.7, anchor=ctk.CENTER)


## ERROR FUNCTIONS ##


# create an error window
def error_window(message, app):
    global ERRORS

    error = ctk.CTkToplevel(app)
    error.title("ERROR WINDOW")
    error.geometry("200x100")
    error.resizable(False, False)
    error.attributes("-topmost", True)
    error.focus()

    label = ctk.CTkLabel(error, text=message, fg_color="transparent")
    label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    ERRORS.append(error)


# called after two seconds - destroys error window
def destroyError():
    global ERRORS

    ERRORS[0].destroy()
    ERRORS.pop(0)
