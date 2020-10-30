import re, sys
import unicodedata
import string
import importlib 

importlib.reload(sys)

class Parser:
    database_object = None
    database_dictionary = None
    language_config_object = None
    thesaurus_object = None

    def __init__(self, database, config):
        self.database_object = database
        self.language_config_object = config
        self.database_dictionary = self.database_object.get_tables_into_dictionary()

    def set_thesaurus(self, thesaurus):
        self.thesaurus_object = thesaurus