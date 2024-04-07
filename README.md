# MRCV: Movie Ranked Choice Voting

Creator: Jonathan Houge

Python executable that combines Letterboxd and RCV-Voting, with two features:

1. "What Wouldn't the Academy Pick?"
2. Movie-Ranked-Choice-Voting

Final Project for CSC-496: Computational Challenges in Elections: Ranked Choice Voting and Redistricting.

Makes uses of and expands upon the awesome Letterboxd 'listscraper', created and maintained by Arno Lafontaine.
Find their repo's readme and license within the 'listscraper' folder.
Fun fact: I actually made a contribution to this repo to further functionality! Check their repo out!

https://github.com/L-Dot/Letterboxd-list-scraper

## Usage

Clone the repo:

`git clone https://github.com/jonathanhouge/MRCV.git`

Install requirements:

`pip install -r requirements.txt`

Create an executable:

`python -m PyInstaller main.py --onefile`

## References

- https://github.com/TomSchimansky/CustomTkinter
- https://pyinstaller.org/en/v4.8
