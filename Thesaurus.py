import sys
import unicodedata
import importlib 

importlib.reload(sys)

class Thesaurus:

    def __init__(self):
        self.dictionary = {}

    def add_entry(self, word, synonyms):
        self.dictionary[word] = synonyms

    def remove_accents(self, string):
        nkfd_form = unicodedata.normalize('NFKD', str(string))
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

    def load(self, path):
        with open(path) as f:
            content = f.readlines()
            
            for line_id in range(1,len(content)):
                if '(' not in content[line_id]:
                    line = content[line_id].split("|")
                    word = self.remove_accents(line[0])
                    synonyms = self.remove_accents(content[line_id + 1]).split("|")
                    synonyms.pop(0)
                    self.add_entry(word, synonyms)

    def print(self):
        for keys,values in self.dictionary.items():
            print(keys)
            print(values)