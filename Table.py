import sys
import unicodedata
import importlib 

importlib.reload(sys)

from Column import Column

class Table:
    name = ''
    columns = []
    
    def __init__(self, name = None, columns = None):
        if name is None:
            self.name = ''
        else:
            self.name = name

        if columns is None:
            self.columns = []
        else:
            self.columns = columns

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def add_column(self, column_name, column_type):
        self.columns.append(Column(column_name, column_type))

    def get_number_of_columns(self):
        return len(self.columns)
    
    def get_columns(self):
        return self.columns

    def get_column_by_name(self, column_name):
        for column in self.columns:
            if column.get_name() == column_name:
                return column

    def add_primary_key(self, primary_key_column):
        for column in self.columns:
            if column.get_name() == primary_key_column:
                column.set_as_primary()

    def add_foreign_key(self, column_name, foreign_table, foreign_column):
        for column in self.columns:
            if column.get_name() == column_name:
                column.set_as_foreign({'foreign_table':foreign_table,'foreign_column':foreign_column})