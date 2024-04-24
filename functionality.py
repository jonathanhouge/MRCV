import customtkinter as ctk
import threading
import subprocess
from PIL import Image
from bs4 import BeautifulSoup
import requests
import json
import webbrowser
import random
import pyperclip
import os
from datetime import datetime


MODE = True
APP = ""
MRCV = False
WWTAP = False
ERRORS = []

SCHEMES = [
    "baldwin",
    "black",
    "borda",
    "btr_irv",
    "bucklin",
    "coombs",
    "copeland",
    "irv",
    "kemeny_young",
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

GAME_URL = ""
GAME_RESULT = False
GAME_SCHEME = ""
GAME_WINNER = "game winner here"
GAME_WINNER_URL = "https://letterboxd.com/film/404-1/"
GAME_CHOICES_AREA = "game candidates here"
GAME_PREDICTED_WINNER = ""
POSSIBLE_WINNERS_DROPDOWN = ""
RUN_GAME_ELECTION_BUTTON = ""
GAME_SCHEME_DROPDOWN = ""

WINNER = "winner here"
WWTAP_WINNER_URL = "https://letterboxd.com/film/404-1/"
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
        "MRCV Game: A chance to test your RCV and movie knowledge! Input\na valid Letterboxd URL ('list', 'films', 'role'), we'll scrape random\nfilms from it and create ballots, then you choose which candidate\nyou think will win given the films and a random RCV scheme.\nHow many can you get right!?"
    )

    label = ctk.CTkTextbox(tutorial, width=400, height=200, corner_radius=0)
    label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
    label.insert("0.0", tutorial_text)
    label.configure(state="disabled")


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
    MRCV.geometry("700x500")
    MRCV.resizable(False, False)
    MRCV.attributes("-topmost", True)

    # backdrops
    actions_frame = ctk.CTkFrame(master=MRCV, width=320, height=200)
    actions_frame.place(relx=0.25, rely=0.65, anchor=ctk.CENTER)

    game_choices_frame = ctk.CTkFrame(master=MRCV, width=320, height=200)
    game_choices_frame.place(relx=0.75, rely=0.65, anchor=ctk.CENTER)

    # set up other buttons / functionality
    pick_url_dropdown(MRCV)
    copy_game_stats_button(MRCV)
    generate_election_button(MRCV)
    game_choices_section(MRCV)


def pick_url_dropdown(app):
    global GAME_URL

    note = ctk.CTkTextbox(
        app,
        width=300,
        height=5,
        font=("", 10),
        fg_color=("#e8e4e4", "#212121"),
        bg_color=("#e8e4e4", "#212121"),
    )
    note.insert("0.0", "note: this is the path after 'https://letterboxd.com/'")
    note.place(relx=0.25, rely=0.54, anchor=ctk.CENTER)
    note.configure(state="disabled")

    GAME_URL = ctk.CTkTextbox(app, width=300, height=25)
    GAME_URL.insert("0.0", "actor/nicolas-cage/")
    GAME_URL.place(relx=0.25, rely=0.5, anchor=ctk.CENTER)

def copy_game_stats_button(app):
    def copy_stats():
        try:
            with open("game-files/stats.json", "r", encoding="utf-8") as jsonf:
                profile = json.load(jsonf)
        except:
            pyperclip.copy("You don't have any stats!")
            return
        
        game_history = ""
        for game in profile["completed_games"]:
            game_result = "won" if game["won?"] else "lost"
            game_history += f"{game["game_url"]}, {game["scheme"]}, {game["date"]}: {game_result}\n"

        stats = f"Streak: {profile["streak"]}\nBest Streak: {profile["best_streak"]}\nGame History:\n{game_history}"
        pyperclip.copy(stats)

    generate_button = ctk.CTkButton(
        master=app, text="Copy Lifetime Stats", command=copy_stats
    )
    generate_button.place(relx=0.12, rely=0.94, anchor=ctk.CENTER)


def generate_election_button(app):
    global GAME_WINNER

    # run election button and command
    def generate_election():
        global GAME_SCHEME
        global GAME_WINNER_URL
        global POSSIBLE_WINNERS_DROPDOWN
        global RUN_GAME_ELECTION_BUTTON
        global GAME_SCHEME_DROPDOWN
        global GAME_PREDICTED_WINNER

        url = GAME_URL.get("0.0", "end")  # scrape candidates
        command = f"python -m listscraper https://letterboxd.com/{url}"

        # if the command fails, we have a runtime error - simply report it and move on
        try:
            subprocess.check_output(command, shell=True, text=True)
        except Exception as e:
            print(f"Error: f{e}")
            error_window("Runtime Error. :(", app)
            threading.Timer(2.0, destroyError).start()

        # update academy's results
        with open(
            f"game-files/game-candidates.json",
            "r",
            encoding="utf-8",
        ) as jsonf:
            candidates = json.load(jsonf)

            game_choices_list = [candidate["Film_title"] for candidate in candidates]

            game_choices = "Game Choices:\n"
            for game_choice in game_choices_list:
                game_choices += game_choice + "\n"

        GAME_CHOICES_AREA.configure(text=game_choices)

        # build ballots
        command = f"python -m listscraper null"
        try:
            subprocess.check_output(command, shell=True, text=True)
        except Exception as e:
            print(f"Error: f{e}")
            error_window("Runtime Error. :(", app)
            threading.Timer(2.0, destroyError).start()

        GAME_PREDICTED_WINNER = game_choices_list[0]
        choice = ctk.StringVar(value=game_choices_list[0])

        def combobox_callback(choice):
            global GAME_PREDICTED_WINNER
            GAME_PREDICTED_WINNER = choice

        game_choices_list.append("<AMBIGUOUS>")
        POSSIBLE_WINNERS_DROPDOWN = ctk.CTkComboBox(
            master=app,
            values=game_choices_list,
            variable=choice,
            command=combobox_callback,
        )
        POSSIBLE_WINNERS_DROPDOWN.pack(padx=20, pady=10)
        POSSIBLE_WINNERS_DROPDOWN.place(relx=0.135, rely=0.7, anchor=ctk.CENTER)

        GAME_SCHEME = SCHEMES[random.randint(0, len(SCHEMES) - 1)]
        GAME_SCHEME_DROPDOWN = ctk.CTkLabel(
            app,
            text=f"scheme: {GAME_SCHEME[:14]}",
            text_color=("black", "white"),
            fg_color=("#e8e4e4", "#212121"),
        )
        GAME_SCHEME_DROPDOWN.place(relx=0.36, rely=0.7, anchor=ctk.CENTER)

        def run_game_election():
            global GAME_WINNER_URL
            global GAME_PREDICTED_WINNER
            global GAME_SCHEME
            global GAME_RESULT
            global GAME_URL

            command = f"python schemes/{GAME_SCHEME}.py --election game-files/game-ballots.json"
            winner = "<ERROR>"
            winner_poster = "posters/AMBIGUOUS.jpg"
            GAME_WINNER_URL = "https://letterboxd.com/film/404-1/"

            # if the command fails, we have a runtime error - simply report it and move on
            try:
                result = subprocess.check_output(command, shell=True, text=True)
                winner = result.strip()  # trailing whitespace for some reason?
                GAME_RESULT = winner == GAME_PREDICTED_WINNER

                # go and get the winning movie's poster
                if winner != "<AMBIGUOUS>":
                    with open(
                        f"game-files/game-candidates.json",
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
                    GAME_WINNER_URL = film_url
            except Exception as e:
                print(f"Error: f{e}")
                error_window("Runtime Error. :(", app)
                threading.Timer(2.0, destroyError).start()

            # update winner, either someone won or 'ambiguous' was returned
            winner_image = ctk.CTkImage(
                Image.open(f"{winner_poster}"),
                size=(100, 150),
            )

            GAME_WINNER.configure(text=winner, image=winner_image)

            result_window = ctk.CTkToplevel(app)
            result_window.title("Game Result")
            result_window.geometry("300x100")
            result_window.resizable(False, False)
            result_window.attributes("-topmost", True)
            result_window.focus()

            try:
                with open("game-files/stats.json", "r", encoding="utf-8") as jsonf:
                    profile = json.load(jsonf)
            except:
                profile = {"streak": 0, "best_streak": 0, "completed_games": [] }

            url = GAME_URL.get("0.0", "end").strip()
            today_date = str(datetime.today().date())

            round_stats = {
                "date": today_date,
                "game_url": url,
                "scheme": GAME_SCHEME,
                "won?": GAME_RESULT,
            }
            profile["completed_games"].append(round_stats)

            if GAME_RESULT:
                profile["streak"] += 1
                if profile["streak"] > profile["best_streak"]:
                    profile["best_streak"] = profile["streak"]

                message = "Correct! Your stats have been\ncopied to your clipboard."
                clip_text = f"I correctly guessed the winner of {url} using {GAME_SCHEME}.\nMy streak is now at {profile["streak"]}! Beat that!\nhttps://github.com/jonathanhouge/MRCV"
            else:
                message = "Aw, incorrect!\nChallenge a friend!\nThis round has been copied to your clipboard."
                clip_text = f"{url} using {GAME_SCHEME} ended my streak of {profile["streak"]}.\nCan you do better?\nhttps://github.com/jonathanhouge/MRCV"
            pyperclip.copy(clip_text)

            outpath = os.path.join("game-files", "stats.json")
            with open(outpath, "w", encoding="utf-8") as jsonf:
                jsonf.write(json.dumps(profile, indent=2, ensure_ascii=False))

            label = ctk.CTkLabel(result_window, text=message, fg_color="transparent")
            label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

            POSSIBLE_WINNERS_DROPDOWN.destroy()
            RUN_GAME_ELECTION_BUTTON.destroy()
            GAME_SCHEME_DROPDOWN.destroy()
            GAME_CHOICES_AREA.configure(text="game candidates here")

        RUN_GAME_ELECTION_BUTTON = ctk.CTkButton(
            master=app, text="Predict Winner", command=run_game_election
        )
        RUN_GAME_ELECTION_BUTTON.place(relx=0.25, rely=0.8, anchor=ctk.CENTER)

    generate_button = ctk.CTkButton(
        master=app, text="Generate Results", command=generate_election
    )
    generate_button.place(relx=0.25, rely=0.6, anchor=ctk.CENTER)

    # set up our winner button - start as AMBIGUOUS, assign to global so we can update it later
    # button allows us to go to the letterboxd page for the winner
    def winner_button():
        global GAME_WINNER_URL
        webbrowser.open(GAME_WINNER_URL)

    button_image = ctk.CTkImage(
        Image.open("posters/AMBIGUOUS.jpg"),
        size=(100, 150),
    )

    GAME_WINNER = ctk.CTkButton(
        master=app,
        text="game winner here",
        image=button_image,
        command=winner_button,
    )
    GAME_WINNER.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)


def game_choices_section(app):
    global GAME_CHOICES_AREA

    GAME_CHOICES_AREA = ctk.CTkLabel(
        app,
        text="game candidates here",
        text_color=("black", "white"),
        fg_color=("#e8e4e4", "#212121"),
    )
    GAME_CHOICES_AREA.place(relx=0.75, rely=0.65, anchor=ctk.CENTER)


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

    academy_frame = ctk.CTkFrame(master=WWTAP, width=320, height=240)
    academy_frame.place(relx=0.7, rely=0.69, anchor=ctk.CENTER)

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
        global WWTAP_WINNER_URL
        global ACTUAL_WINNER

        command = f"python schemes/{SCHEME}.py --election academy-ballots/{CATEGORY}/{YEAR}-{CATEGORY}-ballots.json"
        winner = "<ERROR>"
        winner_poster = "posters/AMBIGUOUS.jpg"
        WWTAP_WINNER_URL = "https://letterboxd.com/film/404-1/"

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
                WWTAP_WINNER_URL = film_url

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
        global WWTAP_WINNER_URL
        webbrowser.open(WWTAP_WINNER_URL)

    button_image = ctk.CTkImage(
        Image.open("posters/AMBIGUOUS.jpg"),
        size=(100, 150),
    )

    WINNER = ctk.CTkButton(
        master=app,
        text="wwtap winner here",
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
    ACTUAL_NOMINEES.place(relx=0.7, rely=0.75, anchor=ctk.CENTER)


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
