import csv
import random
import genanki
from pathlib import Path

MODEL_ID = 1260270622

my_model = genanki.Model(
    MODEL_ID,
    'Simple Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        },
    ])


def main():

    my_decks = []

    pathlist = sorted(Path('./results/by_chapter/').glob('Chapter*.csv'))
    for path in pathlist:
        # because path is object not string
        path_in_str = str(path)
        print(path_in_str)

        with open(path_in_str, 'r') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            chapter_title = path.stem
            my_decks.append(create_chapter_deck(chapter_title, csv_reader))

    if my_decks:
        genanki.Package(my_decks).write_to_file('AEMT.apkg')


def create_chapter_deck(chapter, chapter_rows):

    my_deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        f'JBLearning AEMT::{chapter}')

    first = True
    for row in chapter_rows:
        if first:
            first = False
            continue

        my_note = genanki.Note(
            model=my_model,
            fields=[row[0], row[1]])

        my_note.tags.append(chapter.replace(' ', '-'))

        my_deck.add_note(my_note)

    return my_deck

if __name__ == '__main__':
    main()
