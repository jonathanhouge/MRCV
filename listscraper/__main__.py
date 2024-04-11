from listscraper.cli import cli_arguments
from listscraper.instance_class import ScrapeInstance
from listscraper.scrape_functions import scrape_list
import json
import os


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
    if args.review:
        reviewers = scrape_list(args.listURL[0], args.pages, reviews=True)
        outpath = os.path.join(args.output_path, args.output_name)

        with open(outpath, "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(reviewers, indent=2, ensure_ascii=False))
        print("Done!")
    else:
        LBscraper = ScrapeInstance(args.listURL, args.pages, args.output_name, args.output_path, args.file, args.concat, args.quiet, args.threads)

        # # End message
        print(f"\nProgram successfully finished! Your CSV(s) can be found in ./{LBscraper.output_path}/.")
        print(f"    Total run time was {LBscraper.endtime - LBscraper.starttime :.2f} seconds.")


if __name__ == "__main__":
    main()