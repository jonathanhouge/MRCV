from listscraper.utility_functions import val2stars, stars2val
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import numpy as np
import re

_domain = "https://letterboxd.com/"


def scrape_list(
    list_url, page_options, quiet=False, concat=False, watched=False, looking_for=[]
):
    """
    Scrapes a Letterboxd list. Takes into account any optional page selection.

    Parameters:
        list_url (str):          The URL link of the first page of the LB list.
        page_options (str/list): Either a "*" to scrape all pages, or a list with specific page integers.
        quiet (bool):            Option to turn-off tqdm (not much increased speed noticed. Default is off.)
        concat (bool):           If set true it will add an extra column with the original list name to the scraped data.

    Returns:
        list_films (list):       A list of dicts where each dict contains information on the films in the LB list.
    """

    list_films = []

    # If all pages should be scraped, go through all available pages
    if (page_options == []) or (page_options == "*"):
        while True:
            page_films, page_soup = scrape_page(
                list_url, list_url, quiet, concat, watched, looking_for
            )
            list_films.extend(page_films)

            # Check if there is another page of ratings and if yes, continue to that page
            next_button = page_soup.find("a", class_="next")
            if next_button is None:
                break
            else:
                list_url = _domain + next_button["href"]

    # If page selection was input, only go to those pages
    else:
        for p in page_options:
            new_link = list_url + f"page/{p}/"
            try:
                page_films, page_soup = scrape_page(
                    new_link, list_url, quiet, concat, watched, looking_for
                )
                list_films.extend(page_films)
            except:
                print(f"        No films on page {p}...")
                continue

    return list_films


def scrape_page(
    list_url, og_list_url, quiet=False, concat=False, watched=False, looking_for=[]
):
    """
    Scrapes the page of a LB list URL, finds all its films and iterates over each film URL
    to find the relevant information.

    Parameters:
        list_url (str):         Link of the LB page that should be scraped.
        og_list_url (str):      The original input list URL (without any "/page/" strings added)
        quiet (bool):           Option to turn-off tqdm.
        concat (bool):          Checks if concat is enabled.

    Returns:
        page_films (list):      List of dicts containing information on each film on the LB page.
        page_soup (str):        The HTML string of the entire LB page.
    """

    page_films = []
    page_response = requests.get(list_url)

    # Check to see page was downloaded correctly
    if page_response.status_code != 200:
        return print("Error: Could not load page.")

    page_soup = BeautifulSoup(page_response.content, "lxml")

    # get watchers
    if watched:
        watchers_table = page_soup.find("table", class_="person-table film-table")
        watchers_soup = watchers_table.find_all("td", class_="table-person")

        for watcher_soup in watchers_soup if quiet else tqdm(watchers_soup):
            user_link = watcher_soup.find("a", class_="name")["href"]
            watcher = user_link.split("/")[1]
            page_films.append(watcher)

    else:
        # Grab the main film grid
        table = page_soup.find("ul", class_="poster-list")
        if table is None:
            return

        films = table.find_all("li")
        if films == []:
            return

        # Iterate through films
        for film in films if quiet else tqdm(films):
            film_dict = scrape_film(film, looking_for)
            if film_dict is not None:
                page_films.append(film_dict)

    return page_films, page_soup


def scrape_film(film_html, looking_for=[]):
    """
    Scrapes all available information regarding a film.
    The function makes multiple request calls to relevant Letterboxd film URLs and gets their raw HTML code.
    Using manual text extraction, the wanted information is found and stored in a dictionary.

    Parameters:
        film_html (str):    The raw <li> HTML string of the film object obtained from the list page HTML.

    Returns:
        film_dict (dict):   A dictionary containing all the film's information.
    """

    film_dict = {}

    # Obtaining release year, director and average rating of the movie
    film_card = film_html.find("div").get("data-target-link")[1:]
    film_url = _domain + film_card
    filmget = requests.get(film_url)
    film_soup = BeautifulSoup(filmget.content, "html.parser")

    # Finding the film name
    film_dict["Film_title"] = film_soup.find("div", {"class": "col-17"}).find("h1").text
    film_dict["url"] = film_url

    # if we're making ballots, stop if the movie isn't a candidate
    if len(looking_for) != 0 and film_dict["Film_title"] not in looking_for:
        return None

    # Finding average rating, if not found insert a nan
    try:
        film_dict["Average_rating"] = float(
            film_soup.find("meta", attrs={"name": "twitter:data2"}).attrs["content"][:4]
        )
    except:
        film_dict["Average_rating"] = None

    # Try to find the list owner's rating of a film if possible and converting to float
    try:
        stringval = film_html.attrs["data-owner-rating"]
        if stringval != "0":
            film_dict["Owner_rating"] = float(int(stringval) / 2)
        else:
            film_dict["Owner_rating"] = 0
    except:
        # Extra clause for type 'film' lists
        try:
            starval = film_html.find_all("span")[-1].text
            film_dict["Owner_rating"] = stars2val(starval)
        except:
            film_dict["Owner_rating"] = 0

    # if we're making ballots, grab the movie
    if len(looking_for) != 0 and film_dict["Film_title"] in looking_for:
        del film_dict["Average_rating"]
        return film_dict

    # Get movie runtime by searching for first sequence of digits in the p element with the runtime, if not found insert nan
    try:
        film_dict["Runtime"] = int(
            re.search(
                r"\d+", film_soup.find("p", {"class": "text-link text-footer"}).text
            ).group()
        )
    except:
        film_dict["Runtime"] = None

    # CATEGORY SPECIFIC running time
    # for docs and live action shorts: film_dict["Runtime"] > 40 or film_dict["Runtime"] < 7
    # for animated shorts: film_dict["Runtime"] > 40 or film_dict["Runtime"] < 3
    # for feature films: film_dict["Runtime"] < 60 or film_dict["Runtime"] > 240
    if (
        film_dict["Runtime"] is None
        or film_dict["Runtime"] > 40
        or film_dict["Runtime"] < 7
    ):
        return None

    # Finding countries
    try:
        film_dict["Countries"] = [
            line.contents[0]
            for line in film_soup.find("div", attrs={"id": "tab-details"}).find_all(
                "a", href=re.compile(r"country")
            )
        ]
        if film_dict["Countries"] == []:
            film_dict["Countries"] = None
    except:
        film_dict["Countries"] = None

    # Finding spoken and original languages
    try:
        # Replace non-breaking spaces (\xa0) by a normal space
        languages = [
            line.contents[0].replace("\xa0", " ")
            for line in film_soup.find("div", attrs={"id": "tab-details"}).find_all(
                "a", href=re.compile(r"language")
            )
        ]
        film_dict["Original_language"] = languages[
            0
        ]  # original language (always first)
    except:
        film_dict["Original_language"] = None

    # CATEGORY SPECIFIC language (international only)
    # if (
    #     film_dict["Original_language"] is None
    #     or film_dict["Original_language"] == "English"
    # ):
    #     return None

    # Finding genres
    try:
        film_dict["Genres"] = [
            line.contents[0]
            for line in film_soup.find("div", attrs={"id": "tab-genres"}).find_all(
                "a", href=re.compile(r"genre")
            )
        ]
        if film_dict["Genres"] == []:
            film_dict["Genres"] = None
    except:
        film_dict["Genres"] = None

    # CATEGORY SPECIFIC genre
    # for best picture, international, and live action shorts
    if (
        film_dict["Genres"] is None
        or "Documentary" in film_dict["Genres"]
        or "Animation" in film_dict["Genres"]
    ):
        return None

    # Getting number of watches, appearances in lists and number of likes (requires new link) ##
    movie = film_url.split("/")[-2]  # Movie title in URL
    r = requests.get(
        f"https://letterboxd.com/csi/film/{movie}/stats/"
    )  # Stats page of said movie
    stats_soup = BeautifulSoup(r.content, "lxml")

    # Get number of people that have watched the movie
    watches = stats_soup.find("a", {"class": "has-icon icon-watched icon-16 tooltip"})[
        "title"
    ]
    watches = re.findall(r"\d+", watches)  # Find the number from string
    film_dict["Watches"] = int("".join(watches))  # Filter out commas from large numbers

    # CATEGORY SPECIFIC for number of watchers
    # 1000 for shorts (all kinds)
    # 2500 for docs
    # 3500 for animated
    # 5000 for international
    if film_dict["Watches"] is None or film_dict["Watches"] < 1000:
        return None

    # Get number of film appearances in lists
    list_appearances = stats_soup.find(
        "a", {"class": "has-icon icon-list icon-16 tooltip"}
    )["title"]
    list_appearances = re.findall(r"\d+", list_appearances)
    film_dict["List_appearances"] = int("".join(list_appearances))

    # Get number of people that have liked the movie
    likes = stats_soup.find(
        "a", {"class": "has-icon icon-like icon-liked icon-16 tooltip"}
    )["title"]
    likes = re.findall(r"\d+", likes)
    film_dict["Likes"] = int("".join(likes))

    # Getting info on rating histogram (requires new link)
    r = requests.get(
        f"https://letterboxd.com/csi/film/{movie}/rating-histogram/"
    )  # Rating histogram page of said movie
    hist_soup = BeautifulSoup(r.content, "lxml")

    # Get number of fans. Amount is given in 'K' notation, so if relevant rounded off to full thousands
    try:
        fans = hist_soup.find("a", {"class": "all-link more-link"}).text
        fans = re.findall(r"\d+.\d+K?|\d+K?", fans)[0]
        if "." and "K" in fans:
            fans = int(float(fans[:-1]) * 1000)
        elif "K" in fans:
            fans = int(fans[-1]) * 1000
        else:
            fans = int(fans)
    except:
        fans = 0
    film_dict["Fans"] = fans

    # Get rating histogram (i.e. how many star ratings were given) and total ratings (sum of rating histogram)
    ratings = hist_soup.find_all("li", {"class": "rating-histogram-bar"})
    tot_ratings = 0
    for i, r in enumerate(ratings):
        string = r.text.strip(" ")
        stars = (i + 1) / 2
        if string == "":
            film_dict[f"{stars}"] = 0
        else:
            Nratings = re.findall(r"\d+", string)[:-1]
            Nratings = int("".join(Nratings))
            film_dict[f"{stars}"] = Nratings
            tot_ratings += Nratings

    film_dict["Total_ratings"] = tot_ratings

    return film_dict
