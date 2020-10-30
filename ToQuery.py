import os, sys, getopt
import unicodedata
import importlib 

# importlib used for python3
importlib.reload(sys)
# sys.setdefaultencoding not added as it is default in python3

from Database import Database
from LanguageConfig import LanguageConfig
from Parser import Parser
from Thesaurus import Thesaurus

class ToQuery:
    def __init__(self, database_path, input_sentence, language_path, thesaurus_path, json_output_path):
        if language_path is None:
            language_path = "DefaultData/english.csv"
        if thesaurus_path is None:
            thesaurus_path = "DefaultData/english_thesaurus.dat"
        if json_output_path is None:
            json_output_path = "output.json"

        database = Database()
        database.load(database_path)
        # database.print()

        config = LanguageConfig()
        config.load(language_path)
        # config.print()

        parser = Parser(database, config)

        thesaurus = Thesaurus()
        thesaurus.load(thesaurus_path)
        # thesaurus.print()
        
        parser.set_thesaurus(thesaurus)

        # queries = parser.parse_sentence(input_sentence)

def help_message():
    print('Usage:')
    print('\tpython ToQuery.py -d <path> -i <input-sentence> [-l <path>] [-t <path>] [-j <path>]')
    print('Parameters:')
    print('\t-h\t\t\tprint this help message')
    print('\t-d <path>\t\tpath to SQL dump file')
    print('\t-l <path>\t\tpath to language configuration file')
    print('\t-i <input-sentence>\tinput sentence to parse')
    print('\t-j <path>\t\tpath to JSON output file')
    print('\t-t <path>\t\tpath to thesaurus file')

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"d:l:i:t:j:")
        database_path = None
        input_sentence = None

        language_path = None
        thesaurus_path = None
        json_output_path = None
        
        for i in range(0, len(opts)):
            if opts[i][0] == "-d":
                database_path = opts[i][1]
            elif opts[i][0] == "-i":
                input_sentence = opts[i][1]
            elif opts[i][0] == "-l":
                language_path = opts[i][1]
            elif opts[i][0] == "-t":
                thesaurus_path = opts[i][1]
            elif opts[i][0] == "-j":
                json_output_path = opts[i][1]
            else:
                help_message()
                sys.exit()

        if (database_path is None) or (input_sentence is None):
            help_message()
            sys.exit()
        else:
            if language_path is not None:
                language_path = str(language_path)
            if thesaurus_path is not None:
                thesaurus_path = str(thesaurus_path)
            if json_output_path is not None:
                json_output_path = str(json_output_path)

        ToQuery(str(database_path), str(input_sentence), language_path, thesaurus_path, json_output_path)
        
    except getopt.GetoptError:
        help_message()
        sys.exit()

if __name__ == '__main__':
    main(sys.argv[1:])