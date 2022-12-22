"""
Currently contains spellings, pronunciations, and syllables.
TODO: What other data can I include?
- definitions
- thesarus (WordNet?)
"""

from pathlib import Path
import json
import sqlite3
from itertools import chain
from syllabify import Pronunciation
from contextlib import closing

with open('en_US.json', encoding="utf-8") as f:
	words: dict[str, str] = json.load(f)['en_US'][0]

create_table = """CREATE TABLE words (
	spelling TEXT,
	pronunciation TEXT,
	syllables JSON
);

-- https://www.sqlite.org/fts5.html
-- https://stackoverflow.com/a/68832958

CREATE VIRTUAL TABLE words_index USING fts5(spelling, pronunciation, content='words', content_rowid='rowid');

-- Since this datababse is immutable, we don't need to be concerned with
-- updates or deletes.
CREATE TRIGGER words_index_insert AFTER INSERT ON words
    BEGIN
        INSERT INTO words_index (rowid, spelling, pronunciation)
        VALUES (new.rowid, new.spelling, new.pronunciation);
    END;
"""

insert_word = """INSERT INTO words (spelling, pronunciation, syllables) VALUES (?, ?, ?);"""

db_path = Path('linguistics.db')
db_path.unlink(missing_ok=True)
with sqlite3.Connection(db_path) as conn:
	with closing(conn.cursor()) as cursor:
		cursor.executescript(create_table)

		words_and_pronunciaitons = chain.from_iterable(
			# Words with multiple pronunciations are broken up with ", "
			((word, Pronunciation(pronunciation)) for pronunciation in ipa.split(", "))
			for word, ipa in words.items() 
		)

		cursor.executemany(insert_word, ((word, pronunciation.pronunciation, json.dumps(pronunciation.syllables)) for word, pronunciation in words_and_pronunciaitons))
	conn.commit()
