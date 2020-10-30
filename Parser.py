import re, sys
import unicodedata
import string
import importlib 
import functools

importlib.reload(sys)



# --------------------------------PART OF ALGORITHM FOR VALUE EXTRACTION STRARTS
def _myCmp(s1,s2):
    # if len(s1.split()) == 1 and len(s2.split()) == 1:
    if len(s1.split()) == len(s2.split()) :
        if len(s1) >= len(s2) :
            return 1
        else:
            return -1
    else:
        if len(s1.split()) >= len(s2.split()):
            return 1
        else:
            return -1

def _transformationSortAlgo(transitionalList):
    return sorted(transitionalList, key=functools.cmp_to_key(_myCmp),reverse=True)
# -----------------------------------PART OF ALGORITHM FOR VALUE EXTRACTION ENDS


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

    def remove_accents(self, string):
        nkfd_form = unicodedata.normalize('NFKD', str(string))
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

    def parse_sentence(self, sentence):
        number_of_table = 0 
        number_of_select_column = 0
        number_of_where_column = 0
        last_table_position = 0
        columns_of_select = []
        columns_of_where = []
        columns_of_values_of_where = []
        filter_list = [",", "!"]
        temp_queries = []

        input_for_finding_value = sentence.rstrip(string.punctuation.replace('"','').replace("'",""))
        
        for filter_element in filter_list:
            input_for_finding_value = input_for_finding_value.replace(filter_element, " ")

        input_word_list = input_for_finding_value.split()

        # tokenization done

        #some temporary vars
        start_phase = ''
        mid_phase = ''
        end_phase = ''
        temp_where_cols = 0
        temp_table_number = 0
        temp_last_position_in_table = 0


        for i in range(0, len(input_word_list)):
            if input_word_list[i] in self.database_dictionary:
                if temp_table_number==0:
                    start_phase = input_word_list[:i]
                temp_table_number += 1
                temp_last_position_in_table = i
            for table in self.database_dictionary:
                if input_word_list[i] in self.database_dictionary[table]:
                    if temp_where_cols == 0:
                        mid_phase = input_word_list[len(start_phase):temp_last_position_in_table + 1]
                    temp_where_cols += 1
                    break
                else:
                    if (temp_table_number != 0) and (temp_where_cols== 0) and (i == (len(input_word_list) - 1)):
                        mid_phase = input_word_list[len(start_phase):]

        end_phase = input_word_list[len(start_phase) + len(mid_phase):]

        interm_text = ' '.join(end_phase)
        if interm_text:
            interm_text = interm_text.lower()

            for filter_element in filter_list:
                interm_text = interm_text.replace(filter_element, " ")

            ##keywords used for assignment
            assignment_list = self.language_config_object.get_equal_keywords() + self.language_config_object.get_like_keywords() + self.language_config_object.get_greater_keywords() + self.language_config_object.get_less_keywords() + self.language_config_object.get_negation_keywords()

            #operators used for assignment
            assignment_list.append(':')
            assignment_list.append('=')
            
            assignment_list = _transformationSortAlgo(assignment_list) 
            # Algorithmic logic for best substitution for extraction of values with the help of assigners.


            #some markers to mark different kinds of assignment
            general_assigner = "*##gen@7>>"
            like_assigner = "*##like@7>>"

            for idx, assigner in enumerate(assignment_list):
                if assigner in self.language_config_object.get_like_keywords():
                    assigner = str(" " + assigner + " ")
                    interm_text = interm_text.replace(assigner, str(" " + like_assigner + " ")) #mark like keyword
                else:
                    assigner = str(" " + assigner + " ")
                    interm_text = interm_text.replace(assigner, str(" " + general_assigner + " "))


            for i in re.findall("(['\"].*?['\"])", interm_text):
                interm_text = interm_text.replace(i, i.replace(' ', '<_>').replace("'", '').replace('"','')) 

            interm_text_list = interm_text.split()

            for idx, x in enumerate(interm_text_list):
                index = idx + 1
                if x == like_assigner:
                    if index < len(interm_text_list) and interm_text_list[index] != like_assigner and interm_text_list[index] != general_assigner:
                        # replace back <_> to spaces from the values assigned
                        columns_of_values_of_where.append(str("'%" + str(interm_text_list[index]).replace('<_>', ' ') + "%'"))

                if x == general_assigner:
                    if index < len(interm_text_list) and interm_text_list[index] != like_assigner and interm_text_list[index] != general_assigner:
                        # replace back <_> to spaces from the values assigned
                        columns_of_values_of_where.append(str("'" + str(interm_text_list[index]).replace('<_>', ' ') + "'"))
            print("columns_of_values_of_where : ",columns_of_values_of_where)

            
        tables_of_from = []
        select_phrase = ''
        from_phrase = ''
        where_phrase = ''

        words = re.findall(r"[\w]+", self.remove_accents(sentence.encode().decode('utf-8')))

        for i in list(range(len(words))):
            if words[i] in self.database_dictionary:
                if number_of_table == 0:
                    select_phrase = words[:i]
                tables_of_from.append(words[i])
                number_of_table += 1
                last_table_position = i
            for table in self.database_dictionary:
                if words[i] in self.database_dictionary[table]:
                    if number_of_table == 0:
                        columns_of_select.append(words[i])
                        number_of_select_column += 1
                    else:
                        if number_of_where_column == 0:
                            from_phrase = words[
                                len(select_phrase):last_table_position + 1]
                        columns_of_where.append(words[i])
                        number_of_where_column += 1
                    break
                else:
                    if (number_of_table != 0) and (number_of_where_column == 0) and (i == (len(words) - 1)):
                        from_phrase = words[len(select_phrase):]

        where_phrase = words[len(select_phrase) + len(from_phrase):]

        if (number_of_select_column + number_of_table + number_of_where_column) == 0:
            raise ParsingException("No keyword found in sentence!")


        print("Select phrase = ", select_phrase)
        print("From phrase = ", from_phrase)
        print("Where phrase = ", where_phrase)

        
        ##Todo: subdivision of where phrase and making queries