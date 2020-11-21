import re, sys
import unicodedata
import string
import importlib 
import functools
from threading import Thread
from ParsingException import ParsingException
from Query import *
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer 
nltk.download('wordnet')

importlib.reload(sys)



class SelectParser(Thread):

    def __init__(self, columns_of_select, tables_of_from, phrase, count_keywords, sum_keywords, average_keywords, max_keywords, min_keywords, database_dictionary):
        Thread.__init__(self)
        self.select_objects = []
        self.columns_of_select = columns_of_select
        self.tables_of_from = tables_of_from
        self.phrase = phrase
        self.count_keywords = count_keywords
        self.sum_keywords = sum_keywords
        self.average_keywords = average_keywords
        self.max_keywords = max_keywords
        self.min_keywords = min_keywords
        self.database_dictionary = database_dictionary

    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.database_dictionary:
            if column in self.database_dictionary[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        one_table_of_column = self.get_tables_of_column(column)[0]
        tables_of_column = self.get_tables_of_column(column)
        if table_of_from in tables_of_column:
            return str(table_of_from) + '.' + str(column)
        else:
            return str(one_table_of_column) + '.' + str(column)

    def run(self):
        for table_of_from in self.tables_of_from:
            self.select_object = Select()
            is_count = False
            number_of_select_column = len(self.columns_of_select)

            if number_of_select_column == 0:
                for count_keyword in self.count_keywords:
                    # if count_keyword in (word.lower() for word in self.phrase):
                    # so that matches multiple words rather than just single word for COUNT
                    # (e.g. -> "how many city there are in which the employe name is aman ?" )
                    lower_self_phrase = ' '.join(word.lower() for word in self.phrase)
                    if count_keyword in lower_self_phrase:
                        is_count = True

                if is_count:
                    self.select_object.add_column(None, 'COUNT')
                else:
                    self.select_object.add_column(None, None)
            else:
                select_phrases = []
                previous_index = 0
                for i in range(0, len(self.phrase)):
                    if self.phrase[i] in self.columns_of_select:
                        select_phrases.append(
                            self.phrase[previous_index:i + 1])
                        previous_index = i + 1

                select_phrases.append(self.phrase[previous_index:])

                for i in range(0, len(select_phrases)):
                    select_type = None

                    # phrase = [word.lower() for word in select_phrases[i]]
                    # so that matches multiple words rather than just single word in select type of phrases
                    # (e.g. -> "how many name there are in emp in which the cityId is more than 3" )

                    lower_select_phrase = ' '.join(word.lower() for word in select_phrases[i])

                    for keyword in self.average_keywords:
                        if keyword in lower_select_phrase:
                            select_type = 'AVG'
                    for keyword in self.count_keywords:
                        if keyword in lower_select_phrase:
                            select_type = 'COUNT'
                    for keyword in self.max_keywords:
                        if keyword in lower_select_phrase:
                            select_type = 'MAX'
                    for keyword in self.min_keywords:
                        if keyword in lower_select_phrase:
                            select_type = 'MIN'
                    for keyword in self.sum_keywords:
                        if keyword in lower_select_phrase:
                            select_type = 'SUM'

                    if (i != len(select_phrases) - 1) or (select_type is not None):
                        if i >= len(self.columns_of_select):
                            column = None
                        else:
                            column = self.get_column_name_with_alias_table(
                                self.columns_of_select[i], table_of_from)
                        self.select_object.add_column(column, select_type)

            self.select_objects.append(self.select_object)

    def join(self):
        Thread.join(self)
        return self.select_objects


class FromParser(Thread):

    def __init__(self, tables_of_from, columns_of_select, columns_of_where, database_object):
        Thread.__init__(self)
        self.queries = []
        self.tables_of_from = tables_of_from
        self.columns_of_select = columns_of_select
        self.columns_of_where = columns_of_where

        self.database_object = database_object
        self.database_dictionary = self.database_object.get_tables_into_dictionary()

    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.database_dictionary:
            if column in self.database_dictionary[table]:
                tmp_table.append(table)
        return tmp_table

    def intersect(self, a, b):
        return list(set(a) & set(b))

    def difference(self, a, b):
        differences = []
        for _list in a:
            if _list not in b:
                differences.append(_list)
        return differences

    def is_direct_join_is_possible(self, table_src, table_trg):
        fk_column_of_src_table = self.database_object.get_foreign_keys_of_table(table_src)
        fk_column_of_trg_table = self.database_object.get_foreign_keys_of_table(table_trg)

        for column in fk_column_of_src_table:
            if column.is_foreign()['foreign_table'] == table_trg:
                return [(table_src, column.get_name()), (table_trg, column.is_foreign()['foreign_column'])]

        for column in fk_column_of_trg_table:
            if column.is_foreign()['foreign_table'] == table_src:
                return [(table_src, column.is_foreign()['foreign_column']), (table_trg, column.get_name())]

        """ @todo Restore the following lines for implicit inner join on same id columns. """

        # pk_table_src = self.database_object.get_primary_key_names_of_table(table_src)
        # pk_table_trg = self.database_object.get_primary_key_names_of_table(table_trg)
        # match_pk_table_src_with_table_trg = self.intersect(pk_table_src, self.database_dictionary[table_trg])
        # match_pk_table_trg_with_table_src = self.intersect(pk_table_trg, self.database_dictionary[table_src])

        # if len(match_pk_table_src_with_table_trg) >= 1:
        #     return [(table_trg, match_pk_table_src_with_table_trg[0]), (table_src, match_pk_table_src_with_table_trg[0])]
        # elif len(match_pk_table_trg_with_table_src) >= 1:
        # return [(table_trg, match_pk_table_trg_with_table_src[0]),
        # (table_src, match_pk_table_trg_with_table_src[0])]

    def get_all_direct_linked_tables_of_a_table(self, table_src):
        links = []
        for table_trg in self.database_dictionary:
            if table_trg != table_src:
                link = self.is_direct_join_is_possible(table_src, table_trg)
                if link is not None:
                    links.append(link)
        return links

    def is_join(self, historic, table_src, table_trg):
        historic = historic
        links = self.get_all_direct_linked_tables_of_a_table(table_src)

        differences = []
        for join in links:
            if join[0][0] not in historic:
                differences.append(join)
        links = differences

        for join in links:
            if join[1][0] == table_trg:
                return [0, join]

        path = []
        historic.append(table_src)

        for join in links:
            result = [1, self.is_join(historic, join[1][0], table_trg)]
            if result[1] != []:
                if result[0] == 0:
                    path.append(result[1])
                    path.append(join)
                else:
                    path = result[1]
                    path.append(join)
        return path

    def get_link(self, table_src, table_trg):
        path = self.is_join([], table_src, table_trg)
        if len(path) > 0:
            path.pop(0)
            path.reverse()
        return path

    def unique(self, _list):
        return [list(x) for x in set(tuple(x) for x in _list)]

    def unique_ordered(self, _list):
        frequency = []
        for element in _list:
            if element not in frequency:
                frequency.append(element)
        return frequency

    def run(self):
        self.queries = []

        for table_of_from in self.tables_of_from:
            links = []
            query = Query()
            query.set_from(From(table_of_from))
            join_object = Join()

            for column in self.columns_of_select:
                if column not in self.database_dictionary[table_of_from]:
                    foreign_table = self.get_tables_of_column(column)[0]
                    join_object.add_table(foreign_table)
                    link = self.get_link(table_of_from, foreign_table)
                    links.extend(link)
            for column in self.columns_of_where:
                if column not in self.database_dictionary[table_of_from]:
                    foreign_table = self.get_tables_of_column(column)[0]
                    join_object.add_table(foreign_table)
                    link = self.get_link(table_of_from, foreign_table)
                    links.extend(link)
            join_object.set_links(self.unique_ordered(links))
            query.set_join(join_object)
            self.queries.append(query)
            if len(join_object.get_tables()) > len(join_object.get_links()):
                self.queries = None

    def join(self):
        Thread.join(self)
        return self.queries


class WhereParser(Thread):

    def __init__(self, phrases, tables_of_from, columns_of_values_of_where, count_keywords, sum_keywords, average_keywords, max_keywords, min_keywords, greater_keywords, less_keywords, between_keywords, negation_keywords, junction_keywords, disjunction_keywords, database_dictionary, like_keywords):
        Thread.__init__(self)
        self.where_objects = []
        self.phrases = phrases
        self.tables_of_from = tables_of_from
        self.columns_of_values_of_where = columns_of_values_of_where
        self.count_keywords = count_keywords
        self.sum_keywords = sum_keywords
        self.average_keywords = average_keywords
        self.max_keywords = max_keywords
        self.min_keywords = min_keywords
        self.greater_keywords = greater_keywords
        self.less_keywords = less_keywords
        self.between_keywords = between_keywords
        self.negation_keywords = negation_keywords
        self.junction_keywords = junction_keywords
        self.disjunction_keywords = disjunction_keywords
        self.database_dictionary = database_dictionary
        self.columns_of_values_of_where = columns_of_values_of_where
        self.like_keywords = like_keywords

    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.database_dictionary:
            if column in self.database_dictionary[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        one_table_of_column = self.get_tables_of_column(column)[0]
        tables_of_column = self.get_tables_of_column(column)
        if table_of_from in tables_of_column:
            return str(table_of_from) + '.' + str(column)
        else:
            return str(one_table_of_column) + '.' + str(column)

    def intersect(self, a, b):
        return list(set(a) & set(b))

    def predict_operation_type(self, previous_column_offset, current_column_offset):
        interval_offset = range(previous_column_offset, current_column_offset)
        if(len(self.intersect(interval_offset, self.count_keyword_offset)) >= 1):
            return 'COUNT'
        elif(len(self.intersect(interval_offset, self.sum_keyword_offset)) >= 1):
            return 'SUM'
        elif(len(self.intersect(interval_offset, self.average_keyword_offset)) >= 1):
            return 'AVG'
        elif(len(self.intersect(interval_offset, self.max_keyword_offset)) >= 1):
            return 'MAX'
        elif(len(self.intersect(interval_offset, self.min_keyword_offset)) >= 1):
            return 'MIN'
        else:
            return None

    def predict_operator(self, current_column_offset, next_column_offset):
        interval_offset = range(current_column_offset, next_column_offset)

        if(len(self.intersect(interval_offset, self.negation_keyword_offset)) >= 1) and (len(self.intersect(interval_offset, self.greater_keyword_offset)) >= 1):
            return '<'
        elif(len(self.intersect(interval_offset, self.negation_keyword_offset)) >= 1) and (len(self.intersect(interval_offset, self.less_keyword_offset)) >= 1):
            return '>'
        if(len(self.intersect(interval_offset, self.less_keyword_offset)) >= 1):
            return '<'
        elif(len(self.intersect(interval_offset, self.greater_keyword_offset)) >= 1):
            return '>'
        elif(len(self.intersect(interval_offset, self.between_keyword_offset)) >= 1):
            return 'BETWEEN'
        elif(len(self.intersect(interval_offset, self.negation_keyword_offset)) >= 1):
            return '!='
        elif(len(self.intersect(interval_offset, self.like_keyword_offset)) >= 1):
            return 'LIKE'
        else:
            return '='

    def predict_junction(self, previous_column_offset, current_column_offset):
        interval_offset = range(previous_column_offset, current_column_offset)
        junction = 'AND'
        if(len(self.intersect(interval_offset, self.disjunction_keyword_offset)) >= 1):
            return 'OR'
        elif(len(self.intersect(interval_offset, self.junction_keyword_offset)) >= 1):
            return 'AND'

        first_encountered_junction_offset = -1
        first_encountered_disjunction_offset = -1

        for offset in self.junction_keyword_offset:
            if offset >= current_column_offset:
                first_encountered_junction_offset = offset
                break

        for offset in self.disjunction_keyword_offset:
            if offset >= current_column_offset:
                first_encountered_disjunction_offset = offset
                break

        if first_encountered_junction_offset >= first_encountered_disjunction_offset:
            return 'AND'
        else:
            return 'OR'

    def run(self):
        number_of_where_columns = 0
        columns_of_where = []
        offset_of = {}
        column_offset = []
        self.count_keyword_offset = []
        self.sum_keyword_offset = []
        self.average_keyword_offset = []
        self.max_keyword_offset = []
        self.min_keyword_offset = []
        self.greater_keyword_offset = []
        self.less_keyword_offset = []
        self.between_keyword_offset = []
        self.junction_keyword_offset = []
        self.disjunction_keyword_offset = []
        self.negation_keyword_offset = []
        self.like_keyword_offset = []


        for phrase in self.phrases:
            phrase_offset_string = ''
            for i in range(0, len(phrase)):
                for table in self.database_dictionary:
                    if phrase[i] in self.database_dictionary[table]:
                        number_of_where_columns += 1
                        columns_of_where.append(phrase[i])
                        offset_of[phrase[i]] = i
                        column_offset.append(i)
                        break

                phrase_keyword = str(phrase[i]).lower()  # for robust keyword matching
                phrase_offset_string += phrase_keyword + " "


                for keyword in self.count_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.count_keyword_offset.append(i)

                for keyword in self.sum_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.sum_keyword_offset.append(i)

                for keyword in self.average_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.average_keyword_offset.append(i)

                for keyword in self.max_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.max_keyword_offset.append(i)

                for keyword in self.min_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.min_keyword_offset.append(i)

                for keyword in self.greater_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.greater_keyword_offset.append(i)

                for keyword in self.less_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.less_keyword_offset.append(i)

                for keyword in self.between_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.between_keyword_offset.append(i)

                for keyword in self.junction_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.junction_keyword_offset.append(i)

                for keyword in self.disjunction_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.disjunction_keyword_offset.append(i)

                for keyword in self.negation_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.negation_keyword_offset.append(i)

                for keyword in self.like_keywords:
                    if keyword in phrase_offset_string :
                        if (phrase_offset_string.find(" " + keyword + " ") + len(keyword) + 2 == len(phrase_offset_string) ) :
                            self.like_keyword_offset.append(i)


        for table_of_from in self.tables_of_from:
            where_object = Where()
            for i in range(0, len(column_offset)):
                current = column_offset[i]

                if i == 0:
                    previous = 0
                else:
                    previous = column_offset[i - 1]

                if i == (len(column_offset) - 1):
                    _next = 999
                else:
                    _next = column_offset[i + 1]

                junction = self.predict_junction(previous, current)
                column = self.get_column_name_with_alias_table(columns_of_where[i], table_of_from)
                operation_type = self.predict_operation_type(previous, current)

                if len(self.columns_of_values_of_where) > i:
                    value = self.columns_of_values_of_where[i]
                else:
                    value = 'OOV'  # Out Of Vocabulary: default value

                operator = self.predict_operator(current, _next)
                where_object.add_condition(junction, Condition(column, operation_type, operator, value))
            self.where_objects.append(where_object)

    def join(self):
        Thread.join(self)
        return self.where_objects


class GroupByParser(Thread):

    def __init__(self, phrases, tables_of_from, database_dictionary):
        Thread.__init__(self)
        self.group_by_objects = []
        self.phrases = phrases
        self.tables_of_from = tables_of_from
        self.database_dictionary = database_dictionary

    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.database_dictionary:
            if column in self.database_dictionary[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        one_table_of_column = self.get_tables_of_column(column)[0]
        tables_of_column = self.get_tables_of_column(column)
        if table_of_from in tables_of_column:
            return str(table_of_from) + '.' + str(column)
        else:
            return str(one_table_of_column) + '.' + str(column)

    def run(self):
        for table_of_from in self.tables_of_from:
            group_by_object = GroupBy()
            for phrase in self.phrases:
                for i in range(0, len(phrase)):
                    for table in self.database_dictionary:
                        if phrase[i] in self.database_dictionary[table]:
                            column = self.get_column_name_with_alias_table(
                                phrase[i], table_of_from)
                            group_by_object.set_column(column)
            self.group_by_objects.append(group_by_object)

    def join(self):
        Thread.join(self)
        return self.group_by_objects


class OrderByParser(Thread):

    def __init__(self, phrases, tables_of_from, asc_keywords, desc_keywords, database_dictionary):
        Thread.__init__(self)
        self.order_by_objects = []
        self.phrases = phrases
        self.tables_of_from = tables_of_from
        self.asc_keywords = asc_keywords
        self.desc_keywords = desc_keywords
        self.database_dictionary = database_dictionary

    def get_tables_of_column(self, column):
        tmp_table = []
        for table in self.database_dictionary:
            if column in self.database_dictionary[table]:
                tmp_table.append(table)
        return tmp_table

    def get_column_name_with_alias_table(self, column, table_of_from):
        one_table_of_column = self.get_tables_of_column(column)[0]
        tables_of_column = self.get_tables_of_column(column)
        if table_of_from in tables_of_column:
            return str(table_of_from) + '.' + str(column)
        else:
            return str(one_table_of_column) + '.' + str(column)

    def intersect(self, a, b):
        return list(set(a) & set(b))

    def predict_order(self, phrase):
        if(len(self.intersect(phrase, self.desc_keywords)) >= 1):
            return 'DESC'
        else:
            return 'ASC'

    def run(self):
        for table_of_from in self.tables_of_from:
            order_by_object = OrderBy()
            for phrase in self.phrases:
                for i in range(0, len(phrase)):
                    for table in self.database_dictionary:
                        if phrase[i] in self.database_dictionary[table]:
                            column = self.get_column_name_with_alias_table(phrase[i], table_of_from)
                            order_by_object.add_column(column, self.predict_order(phrase))
            self.order_by_objects.append(order_by_object)

    def join(self):
        Thread.join(self)
        return self.order_by_objects

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


    def uniq(self, seq):
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if x not in seen and not seen_add(x)]

    def createWordSynonyms(self, word):
        synsets = wordnet.synsets(word)
        synonyms = [word]

        for s in synsets:
            for l in s.lemmas():
                synonyms.append(l.name())

        # if there are no synonyms, put the original word in
        synonyms.append(word)
        return self.uniq(synonyms)

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
       
        sentence = ""
        lemmatizer = WordNetLemmatizer() 
        for token in input_word_list:
            token_lem = lemmatizer.lemmatize(token)
            added = 0
            for table in self.database_dictionary:
                if token_lem == lemmatizer.lemmatize(table) or token == table:
                    sentence+=table+" "
                    added = 1
                    break
            if added == 0:
                sentence+=token+" "
        sentence.rstrip()
        input_for_finding_value = sentence.rstrip(string.punctuation.replace('"','').replace("'",""))
        input_word_list = input_for_finding_value.split()
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
            assignment_list.append('>')
            
            assignment_list = _transformationSortAlgo(assignment_list) 
            # Algorithmic logic for best substitution for extraction of values with the help of assigners.


            #print("assignment_list: ",assignment_list)
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

            #print("interm text after assigner: ", interm_text)

            for i in re.findall("(['\"].*?['\"])", interm_text):
                interm_text = interm_text.replace(i, i.replace(' ', '<_>').replace("'", '').replace('"','')) 

            interm_text_list = interm_text.split()

            #print("int text list after split: ", interm_text_list)


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
            if(len(columns_of_values_of_where) == 0):
                for i in range(len(interm_text_list)-1):
                    word = interm_text_list[i]
                    synonyms = self.createWordSynonyms(word)
                    for w in synonyms:
                        for table in self.database_dictionary:
                            if w in self.database_dictionary[table]:
                                columns_of_values_of_where.append(interm_text_list[i+1])

            #if(len(columns_of_values_of_where) == 0):

            print("values : ",columns_of_values_of_where)

            
        tables_of_from = []
        select_phrase = ''
        from_phrase = ''
        where_phrase = ''

        words = re.findall(r"[\w><=!]+", self.remove_accents(sentence.encode().decode('utf-8')))

        # print("Printing synonyms")
        # for i in list(range(len(words))):
        #     synonyms = self.createWordSynonyms(words[i])
        #     print(synonyms)

        for i in list(range(len(words))):
            synonyms = self.createWordSynonyms(words[i])
            for word in synonyms:
                if word in self.database_dictionary:
                    if number_of_table == 0:
                        select_phrase = words[:i]
                    tables_of_from.append(word)
                    words[i] = word
                    number_of_table += 1
                    last_table_position = i
                    break
            flag=False
            for table in self.database_dictionary:
                if flag: break
                for word in synonyms:
                    if word in self.database_dictionary[table]:
                        flag = True
                        words[i] = word
                        if number_of_table == 0:
                            columns_of_select.append(word)
                            number_of_select_column += 1
                        else:
                            if number_of_where_column == 0:
                                from_phrase = words[
                                    len(select_phrase):last_table_position + 1]
                            columns_of_where.append(word)
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

        #  print("database_dictionary :", self.database_dictionary)
        
        ##Todo: subdivision of where phrase and making queries
        if len(tables_of_from) > 0:
            temp_from_phrases = []
            prev_index = 0
            for i in range(0, len(from_phrase)):
                if from_phrase[i] in tables_of_from:
                    temp_from_phrases.append(from_phrase[prev_index:i + 1])
                    prev_index = i+1

            previous_junction_index = -1

            for i in range(0, len(temp_from_phrases)):
                number_of_junction_words = 0
                number_of_disjunction_words = 0


                for word in temp_from_phrases[i]:
                    if word in self.language_config_object.get_junction_keywords():
                        number_of_junction_words += 1
                    if word in self.language_config_object.get_disjunction_keywords():
                        number_of_disjunction_words += 1

                if (number_of_junction_words + number_of_disjunction_words) > 0:
                    previous_junction_index = i

            if previous_junction_index == -1:
                from_phrase = sum(temp_from_phrases[:1], [])
                where_phrase = sum(temp_from_phrases[1:], []) + where_phrase
            else:
                from_phrase = sum(temp_from_phrases[:previous_junction_index + 1], [])
                where_phrase = sum(temp_from_phrases[previous_junction_index + 1:], []) + where_phrase

        tables_of_from_final = []

        for word in from_phrase:
            if word in tables_of_from:
                tables_of_from_final.append(word)
        tables_of_from = tables_of_from_final

        if len(tables_of_from) == 0:
            raise ParsingException("No table name found in sentence!")

        group_by_phrase = []
        order_by_phrase = []
        new_where_phrase = []
        previous_index = 0
        previous_phrase_type = 0
        yet_where = 0

        for i in range(0, len(where_phrase)):
            if where_phrase[i] in self.language_config_object.get_order_by_keywords():
                if yet_where > 0:
                    if previous_phrase_type == 1:
                        order_by_phrase.append(where_phrase[previous_index:i])
                    elif previous_phrase_type == 2:
                        group_by_phrase.append(where_phrase[previous_index:i])
                else:
                    new_where_phrase.append(where_phrase[previous_index:i])
                previous_index = i
                previous_phrase_type = 1
                yet_where += 1
            if where_phrase[i] in self.language_config_object.get_group_by_keywords():
                if yet_where > 0:
                    if previous_phrase_type == 1:
                        order_by_phrase.append(where_phrase[previous_index:i])
                    elif previous_phrase_type == 2:
                        group_by_phrase.append(where_phrase[previous_index:i])
                else:
                    new_where_phrase.append(where_phrase[previous_index:i])
                previous_index = i
                previous_phrase_type = 2
                yet_where += 1

        if previous_phrase_type == 1:
            order_by_phrase.append(where_phrase[previous_index:])
        elif previous_phrase_type == 2:
            group_by_phrase.append(where_phrase[previous_index:])
        else:
            new_where_phrase.append(where_phrase)

        select_parser = SelectParser(columns_of_select, tables_of_from, select_phrase, self.language_config_object.get_count_keywords(), self.language_config_object.get_sum_keywords(), self.language_config_object.get_avg_keywords(), self.language_config_object.get_max_keywords(), self.language_config_object.get_min_keywords(), self.database_dictionary)
        from_parser = FromParser(tables_of_from, columns_of_select, columns_of_where, self.database_object)
        where_parser = WhereParser(new_where_phrase, tables_of_from, columns_of_values_of_where, self.language_config_object.get_count_keywords(), self.language_config_object.get_sum_keywords(), self.language_config_object.get_avg_keywords(), self.language_config_object.get_max_keywords(), self.language_config_object.get_min_keywords(), self.language_config_object.get_greater_keywords(), self.language_config_object.get_less_keywords(), self.language_config_object.get_between_keywords(), self.language_config_object.get_negation_keywords(), self.language_config_object.get_junction_keywords(), self.language_config_object.get_disjunction_keywords(), self.database_dictionary, self.language_config_object.get_like_keywords())
        group_by_parser = GroupByParser(group_by_phrase, tables_of_from, self.database_dictionary)
        order_by_parser = OrderByParser(order_by_phrase, tables_of_from, self.language_config_object.get_asc_keywords(), self.language_config_object.get_desc_keywords(), self.database_dictionary)

        select_parser.start()
        from_parser.start()
        where_parser.start()
        group_by_parser.start()
        order_by_parser.start()

        queries = from_parser.join()

        if queries is None:
            raise ParsingException("There is at least one unattainable column from the table of FROM!")

        select_objects = select_parser.join()
        where_objects = where_parser.join()
        group_by_objects = group_by_parser.join()
        order_by_objects = order_by_parser.join()

        for i in range(0, len(queries)):
            query = queries[i]
            query.set_select(select_objects[i])
            query.set_where(where_objects[i])
            query.set_group_by(group_by_objects[i])
            query.set_order_by(order_by_objects[i])

        return queries
