# sample command:
# python3 csv-to-json.py --csv-path "scraper_outputs/csv/sample.csv" --json-path "scraper_outputs/json/default.json"

import json
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--csv-path", type=str, default="scraper_outputs/csv/sample.csv")
parser.add_argument(
    "--json-path", type=str, default="scraper_outputs/json/default.json"
)
args = parser.parse_args()


# modified from 'https://www.geeksforgeeks.org/convert-csv-to-json-using-python/'
def main(args):
    data = {}
    with open(args.csv_path, encoding="utf-8") as csvf:
        csvReader = csv.DictReader(csvf)

        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
            # Assuming a column named 'No' to
            # be the primary key
            key = rows["Film_title"]
            data[key] = rows

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(args.json_path, "w", encoding="utf-8") as jsonf:
        jsonf.write(json.dumps(data, indent=4))


main(args)
