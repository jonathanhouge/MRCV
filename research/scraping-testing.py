# trying to scrape a cast / crew member's page, rather than a 'list'
# almost entirely Arno Lafontaine's code here

from bs4 import BeautifulSoup
import requests
import re
import numpy as np

_domain = "https://letterboxd.com/"


def scrape_film(film_html):
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

    # Try to find release year, if missing or 0 insert nan
    release_year = int(
        str(film_soup.find_all("script"))
        .split("releaseYear: ")[1]
        .split(",")[0]
        .strip('"')
    )
    if release_year == 0:
        release_year = "nan"
    film_dict["Release_year"] = release_year

    # Try to find director, if missing insert nan
    director = film_soup.find("meta", attrs={"name": "twitter:data1"}).attrs["content"]
    if director == "":
        director = "nan"
    film_dict["Director"] = director

    # Finding the cast, if not found insert a nan
    try:
        cast = [
            line.contents[0]
            for line in film_soup.find("div", attrs={"id": "tab-cast"}).find_all("a")
        ]

        # remove all the 'Show All...' tags if they are present
        film_dict["Cast"] = [i for i in cast if i != "Show All…"]
    except:
        film_dict["Cast"] = "nan"

    # Finding average rating, if not found insert a nan
    try:
        film_dict["Average_rating"] = float(
            film_soup.find("meta", attrs={"name": "twitter:data2"}).attrs["content"][:4]
        )
    except:
        film_dict["Average_rating"] = "nan"

    # Try to find the list owner's rating of a film if possible and converting to float
    try:
        stringval = film_html.attrs["data-owner-rating"]
        if stringval != "0":
            film_dict["Owner_rating"] = float(int(stringval) / 2)
        else:
            film_dict["Owner_rating"] = "nan"
    except:
        # Extra clause for type 'film' lists
        try:
            starval = film_html.find_all("span")[-1].text
            film_dict["Owner_rating"] = starval
        except:
            film_dict["Owner_rating"] = "nan"

    # Finding film's genres, if not found insert nan
    try:
        genres = film_soup.find("div", {"class": "text-sluglist capitalize"})
        film_dict["Genres"] = [
            genres.text for genres in genres.find_all("a", {"class": "text-slug"})
        ]
    except:
        film_dict["Genres"] = "nan"

    # Get movie runtime by searching for first sequence of digits in the p element with the runtime, if not found insert nan
    try:
        film_dict["Runtime"] = int(
            re.search(
                r"\d+", film_soup.find("p", {"class": "text-link text-footer"}).text
            ).group()
        )
    except:
        film_dict["Runtime"] = "nan"

    # Finding countries
    try:
        film_dict["Countries"] = [
            line.contents[0]
            for line in film_soup.find("div", attrs={"id": "tab-details"}).find_all(
                "a", href=re.compile(r"country")
            )
        ]
        if film_dict["Countries"] == []:
            film_dict["Countries"] = "nan"
    except:
        film_dict["Countries"] = "nan"

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
        film_dict["Spoken_languages"] = list(
            sorted(set(languages), key=languages.index)
        )  # all unique spoken languages
    except:
        film_dict["Original_language"] = "nan"
        film_dict["Spoken_languages"] = "nan"

    # !! Currently not working with films that have a comma in their title
    # # Finding alternative titles
    # try:
    #     alternative_titles = film_soup.find('div', attrs={'id':'tab-details'}).find('div', class_="text-indentedlist").text.strip().split(", ")
    # except:
    #     alternative_titles = "nan"

    # Finding studios
    try:
        film_dict["Studios"] = [
            line.contents[0]
            for line in film_soup.find("div", attrs={"id": "tab-details"}).find_all(
                "a", href=re.compile(r"studio")
            )
        ]
        if film_dict["Studios"] == []:
            film_dict["Studios"] = "nan"
    except:
        film_dict["Studios"] = "nan"

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

    # Thumbnail URL?

    # Banner URL?

    # Save the film URL as an extra column
    film_dict["Film_URL"] = film_url

    return film_dict


page_response = requests.get("https://letterboxd.com/executive-producer/andre-holland/")

# Check to see page was downloaded correctly
if page_response.status_code != 200:
    print("Error: Could not load page.")

page_soup = BeautifulSoup(page_response.content, "lxml")

# Grab the main film grid
table = page_soup.find("ul", class_="poster-list")

films = table.find_all("li")

# Iterate through films
for film in films:
    print(scrape_film(film))
