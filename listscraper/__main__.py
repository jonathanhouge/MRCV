from listscraper.cli import cli_arguments
from listscraper.instance_class import ScrapeInstance
from listscraper.scrape_functions import scrape_list, scrape_film
import json
import os
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

    if args.candidates:
        print("Crafting ballots.")

        # load candidates from previous scrape
        with open(args.candidates, "r", encoding="utf-8") as jsonf:
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
            for watcher in watchers:
                if watcher in overall_watchers:
                    continue

                # get the user's scores, sort it, craft it into a ballot
                ranking_list = scrape_list(f"https://letterboxd.com/{watcher}/films/year/{args.category_path}", user_pages, looking_for=movies)
                ranking_list_sorted = sorted(ranking_list, key=lambda f: f['Owner_rating'], reverse=True)
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
        with open(outpath, "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(ballots, indent=2, ensure_ascii=False))

        print("Ballots crafted!")
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
