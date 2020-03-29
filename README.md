# JBL Flashcard Scraper

Scrape flashcards from the Jones-Bartlett Learning platform using Selenium.

## Usage:

The program has no real user interface. As of now it is just a script with
hard-coded values.

To use the script, fill in the cookies and course_block_url variables with 
cookies from your own navigate2 session and the course's navigate2 homepage,
respectively.

When you run the script, `python JBLScraper.py`, it *should* produce the
the following files:
    results.csv : CSV formatted file with all Question,Answer for all chapters
    results.json : JSON array of {question : <str>, answer: <str>} objects
    Chapter*.csv : CSV file for each chapter available with the flashcards for
    that chapter

This script will use Selenium to iterate through all of the chapters and scrape
out the questions, then use the requests library to find the answers to each
question.

Once you have the csv files, you can use the ankiconvert script to parse the raw
Question,Answer data into Anki decks / an Anki package. Again - this script
is hardcoded and you need to replace the variables with what you want.

# Dependencies / Environment:

I recommend using the virtualenv package to automatically install all dependencies in the [requirements.txt](/requirements.txt)

You will also need `geckodriver` in your $PATH (ie. you need to be able to run `geckodriver` from your shell)

`virtualenv --python=python3 environment`

`source environment/bin/activate`

`pip install -r requirements.txt`
