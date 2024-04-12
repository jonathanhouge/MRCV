from listscraper.cli import cli_arguments
from listscraper.instance_class import ScrapeInstance
from listscraper.scrape_functions import scrape_list, scrape_film
import json
import os
import requests
from bs4 import BeautifulSoup


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

        with open(args.candidates, "r", encoding="utf-8") as jsonf:
            candidates = json.load(jsonf)

        overall_watchers = set()
        for candidate in candidates:
            watch_url = f"{candidate["url"]}members/"
            watchers = scrape_list(watch_url, [1,2], watched=True)
            for watcher in watchers:
                if watcher in overall_watchers:
                    continue

                #scrape_list(f"https://letterboxd.com/{watcher}/films/year/{args.category_path}", args.pages)
            overall_watchers.update(watchers)

        # outpath = os.path.join(args.output_path, args.output_name)
        # with open(outpath, "w", encoding="utf-8") as jsonf:
        #     jsonf.write(json.dumps(watchers, indent=2, ensure_ascii=False))

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

        # # End message
        print(
            f"\nProgram successfully finished! Your CSV(s) can be found in ./{LBscraper.output_path}/."
        )
        print(
            f"    Total run time was {LBscraper.endtime - LBscraper.starttime :.2f} seconds."
        )


if __name__ == "__main__":
    main()
