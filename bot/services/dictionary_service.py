import sqlite3
from database import FDataBase

def connect_db():
    return sqlite3.connect('translations.db')

class DictionaryService:
    def __init__(self, db: FDataBase):
        self.db = db

    def get_dictionary_page(self, limit: int = 10, offset: int = 0):
        return self.db.get_dictionary(limit=limit, offset=offset)

    def get_dictionary_count(self):
        return self.db.get_dictionary_count()

    def add_word(self, informal: str, formal: str, explanation: str = "") -> bool:
        return self.db.add_to_dictionary(informal, formal, explanation)

    def delete_word(self, informal_text: str) -> bool:
        return self.db.delete_from_dictionary(informal_text)

    def search_words(self, search_text: str):
        return self.db.search_dictionary(search_text)

    def get_word_by_informal(self, informal_text: str):
        return self.db.get_word_by_informal(informal_text)

    def get_words_by_letter(self, letter: str, limit: int = 50, offset: int = 0):
        return self.db.get_words_by_letter(letter.upper(), limit, offset)

    def get_words_count_by_letter(self, letter: str):
        return self.db.get_words_count_by_letter(letter.upper())

    def get_alphabet_stats(self):
        return self.db.get_alphabet_stats()