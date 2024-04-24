from listscraper.cli import cli_arguments
from listscraper.instance_class import ScrapeInstance
from listscraper.scrape_functions import scrape_list
import json
import os
import time
from math import ceil


def main():
    """
    Starts the program and prints some text when finished.
    """

    # Welcome message
    print("=============================================")
    print("           Letterboxd-List-Scraper           ")
    print("=============================================")

    # Importing command line arguments and create a scrape instance
    args = cli_arguments()

    # making ballots - either via game or command line (academy-ballots)
    if args.candidates or args.listURL == ["null"]:
        print("Crafting ballots.")
        start = time.time()

        # load candidates (command line or game)
        try:
            with open(args.candidates, "r", encoding="utf-8") as jsonf:
                candidates = json.load(jsonf)
        except:
            with open("game-files/game-candidates.json", "r", encoding="utf-8") as jsonf:
                candidates = json.load(jsonf)

        # list of wanted movie titles and look at enough pages to cover every possible movie
        movies = [movie["Film_title"] for movie in candidates]
        user_pages = list(range(1, ceil(len(movies) / 72) + 1))
        overall_watchers = set()
        count = 1

        ballots = {"ballots": []}
        for candidate in candidates:
            print(f"Movie #{count} / {len(movies)}")

            watch_url = f"{candidate["url"]}members/"
            watchers = scrape_list(watch_url, [1], watched=True) # 25 watchers per film

            # reduce # watchers if presented with loads of candidates or it's the game
            if (len(movies) > 100) or args.listURL == ["null"]:
                watchers = watchers[:10]

            for watcher in watchers:
                if watcher in overall_watchers:
                    continue

                # get the user's scores, sort it, craft it into a ballot
                if args.category_path:
                    ranking_list = scrape_list(f"https://letterboxd.com/{watcher}/films/year/{args.category_path}", user_pages, looking_for=movies)
                else:
                    years = set([movie["Release_year"] for movie in candidates]) # check each watcher for each film's year
                    ranking_list = []
                    for year in years:
                        ranking_list.extend(scrape_list(f"https://letterboxd.com/{watcher}/films/year/{year}/", user_pages, looking_for=movies))
                ranking_list_sorted = sorted(ranking_list, key=lambda f: (f['Owner_rating'], f['Average_rating']), reverse=True) # asked gpt how to specify a second criteria
                ranking = [f['Film_title'] for f in ranking_list_sorted]
                ballot = {"count": 1, "ranking": ranking}

                # if the rating exists, find it and increment the count. if not, we have a new, unique ballot
                try:
                    rankings = [b['ranking'] for b in ballots["ballots"]]
                    index = rankings.index(ballot["ranking"])
                    ballots["ballots"][index]["count"] += 1
                except:
                    ballots["ballots"].append(ballot)
            count += 1

            overall_watchers.update(watchers) # avoid repeats

        # write the ballots to a json
        outpath = os.path.join(args.output_path, args.output_name)
        if args.listURL == ["null"]:
            outpath = os.path.join("game-files", "game-ballots.json")

        with open(outpath, "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(ballots, indent=2, ensure_ascii=False))
        
        end = time.time()
        print(f"Ballots crafted! Run time: {end - start :.2f}")
    else:
        LBscraper = ScrapeInstance(
            args.listURL,
            args.pages,
            args.output_name,
            args.output_path,
            args.file,
            args.concat,
            args.quiet,
            args.threads,
        )

        # End message
        print(
            f"\nProgram successfully finished! Your CSV(s) can be found in ./{LBscraper.output_path}/."
        )
        print(
            f"    Total run time was {LBscraper.endtime - LBscraper.starttime :.2f} seconds."
        )


if __name__ == "__main__":
    main()
