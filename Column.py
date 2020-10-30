import sys
import unicodedata
import importlib 

importlib.reload(sys)

class Column:
    name = ''
    type = ''
    primary_key = False
    foreign_key = False

    def __init__(self, name=None, type=None):
        if name is None:
            self.name = ''
        else:
            self.name = name

        if type is None:
            self.type = ''
        else:
            self.type = type

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_type(self):
        return self.type
    
    def set_type(self, type):
        self.type = type

    def is_primary(self):
        return self.primary_key

    def set_as_primary(self):
        self.primary_key = True

    def is_foreign(self):
        return self.foreign_key

    def set_as_foreign(self, references):
        self.foreign_key = references
