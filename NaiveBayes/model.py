# -*- coding: utf-8 -*-

import pandas as pd
import math
import pickle
import random
from stop_words import get_stop_words
from functools import cmp_to_key
from collections import defaultdict

def add_value_in_dict(m_dict, m_value, m_initial, m_step):
    if m_dict.get(m_value) == None:
        m_dict[m_value] = m_initial
    else:
        m_dict[m_value] += m_step
class CNB:
    def __init__(self):
        # All classes we have.
        # dict: C -> w(c)
        self.classes = dict()

        # All the words we have seen in the entire space.
        self.all_words_count = 0

        # Words count in class.
        # dict::C -> #words in c
        self.words_count_in_class = dict()

        # Count how many times each word is seen.
        # dict::word -> #words in space
        self.all_word_occurances_count = dict()

        # Count how many times we see a word in class
        # dict::C -> (dict:: word -> #occurances in C)
        self.word_occurances_in_class = dict()

        # Remove stopwords or not
        self.remove_stopwords = False

        # Number of classes a word is found in
        # dict::w -> all classes of
        self.classes_of_word = defaultdict(set)
        
    def get_debug_info(self):
        print("Different classes count: {}".format(len(self.classes)))
        print(self.classes)
        print("All words count {}".format(self.all_words_count))
        print("Skip stopwords: {}".format(self.remove_stopwords))

    def save(self, name):
        f = open(name, "wb")
        pickle.dump(self, f)
    
    @classmethod
    def load(cls, name):
        f = open(name, "rb")
        return pickle.load(f)

    def __init_class_probabilities__(self, frame):
        for record in frame:
            for c in record:
                add_value_in_dict(self.classes, c, 1, 1)

        classes_total_count = len(self.classes)

        for c in self.classes:
            try: 
                self.classes[c] = math.log(self.classes[c] / classes_total_count)
            except:
                print(self.classes[c], classes_total_count)
        
    def __tokenize__(self, record_tokens):
        table = str.maketrans("","", ".,_!?“-„:—\t… \n*()><{}[]\xa0123456789/@#%+=")

        record_tokens = list(map(lambda x: str.lower(x.translate(table)), record_tokens))
        record_tokens = list(filter(lambda x: x != "", record_tokens))
        return record_tokens

    def __from_file__(self, record_id):
        record_tokens = open("C:/Users/stoyc/Desktop/AI-project/data/{}/text.txt".format(record_id), 'r', encoding='utf8') \
                        .read()                                                             \
                        .replace('\n', ' ')                                                 \
                        .split(' ')
        
        return self.__tokenize__(record_tokens)

    def __filter_stopwords__(self, record_tokens):
        stop_bg = get_stop_words('bg')
        record_tokens = list(filter(lambda x: x not in stop_bg, record_tokens))
        return record_tokens

    @classmethod
    def remove_stopwords(self, record_tokens):
        stop_bg = get_stop_words('bg')
        return list(filter(lambda x: x not in stop_bg, record_tokens))

    def __process_single_record__(self, record_id, genres):
        record_tokens = self.__from_file__(record_id)

        if self.remove_stopwords:
            record_tokens = self.__filter_stopwords__(record_tokens)

        if self.remove_stopwords:
            record_tokens = CNB.remove_stopwords(record_tokens)
            # stop_bg = get_stop_words('bg')
            # record_tokens = list(filter(lambda x: x not in stop_bg, record_tokens))

        words_count = len(record_tokens)

        # count the words contributing to the classes
        for genre in genres:
            self.classes_of_word[token].add(genre)
            self.all_words_count += words_count
            add_value_in_dict(self.words_count_in_class, genre, words_count, words_count)
        
        # count every word occurance + word occurances in the classes
        for token in record_tokens:
            add_value_in_dict(self.all_word_occurances_count, token, 1, 1)

            for genre in genres:

                if self.word_occurances_in_class.get(genre) == None:
                    self.word_occurances_in_class[genre] = dict()
                
                add_value_in_dict(self.word_occurances_in_class[genre], token, 1, 1)

        print("Finished loading document with id: {}".format(record_id))

    def __init_weights__(self, frame):
        for record in frame:
            self.__process_single_record__(record, frame[record].loc["genres"])

    # Document evaluation utilities:
    def __class_proba__(self, c):
        c_proba = self.classes.get(c)
        if c_proba == None: return 0
        return c_proba

    def __Nc_complement__(self, c):
        class_occurances = 1

        if self.words_count_in_class.get(c) != None:
            class_occurances = self.words_count_in_class[c]

        return self.all_words_count - class_occurances

    def __Nci_complement__(self, c, word):
        word_occurance = 1
        word_occurance_in_class = 1

        if self.all_word_occurances_count.get(word) != None: word_occurance = self.all_word_occurances_count[word]

        if self.word_occurances_in_class.get(c) != None and \
            self.word_occurances_in_class[c].get(word) != None: \
                word_occurance_in_class = self.word_occurances_in_class[c][word]

        return word_occurance - word_occurance_in_class

    def __Nc__(self, c):
        if self.words_count_in_class.get(c) != None:
           return 1
        return self.words_count_in_class[c]

    def __Nci__(self, c, word):
        word_occurance_in_class = 1

        if self.word_occurances_in_class.get(c) != None and \
            self.word_occurances_in_class[c].get(word) != None: \
                word_occurance_in_class = self.word_occurances_in_class[c][word]

        return word_occurance_in_class

    def __deserialize_from_file__(self, path, percentage):
        # parse data to pd.dataframe
        frame = pd.read_json(path)

        # Keep only labeled data
        frame = frame.loc[:, (frame.loc["genres"].str.len() > 0)]

        records_count = frame.shape[1]
        train_size = int(records_count * percentage)

        train = frame.iloc[:, :train_size]
        test  = frame.iloc[:, train_size:]

        self.__init_class_probabilities__(train.loc["genres"])
        self.__init_weights__(train)
        print("Done")
        return test

    def __get_frquencies__(self, tokens, alpha):
        freq = dict()

        for token in tokens:
            add_value_in_dict(freq, token, 1, 1)
        
        for word in freq:
            freq[word] = freq[word] / alpha
        
        return freq

    def fit(self, path, sample_size, remove_stopwords):
        self.remove_stopwords = remove_stopwords
        return self.__deserialize_from_file__(path, sample_size)
    
    def predict_cnb(self, document):
        tokens = self.__tokenize__(document.split(' '))
        classes_weights = dict()
        alpha = len(tokens)
        freq = self.__get_frquencies__(tokens, alpha)

        for c in self.classes.keys():
            weight = self.__class_proba__(c)
                        
            for token in tokens:
                weight -= freq[token] * math.log(
                    (self.__Nci_complement__(c, token) + 1) / (self.__Nc_complement__(c) + alpha)
                )
            classes_weights[c] = weight
        
        return max(classes_weights, key=classes_weights.get)

    def __classes_occurance__(self, word):
        classes = self.classes_of_word[word]
        weight = len(classes)
        return math.log(weight + 1) ** 2

    def predict_cnbs(self, document):
        tokens = self.__tokenize__(document.split(' '))

        if self.remove_stopwords:
            tokens = CNB.remove_stopwords(tokens)

        alpha = len(tokens)
        freq = self.__get_frquencies__(tokens, alpha)
        tokens = set(sorted(tokens, key=cmp_to_key(lambda x, y: self.__classes_occurance__(x) < self.__classes_occurance__(y)), reverse=True)[:400])

        classes_weights = dict()

        for c in self.classes.keys():
            weight = self.__class_proba__(c)

            for token in tokens:
                weight -= freq[token] * math.log(
                    (self.__Nci_complement__(c, token) + 1) / (self.__Nc_complement__(c) + alpha)
                ) * self.__classes_occurance__(token)
            classes_weights[c] = weight
        
        return sorted(classes_weights, key=lambda k: classes_weights[k], reverse=True)[:5]

    def predict_nb(self, document):
        tokens = self.__tokenize__(document.split(' '))
        classes_weights = dict()
        alpha = len(tokens)
        freq = self.__get_frquencies__(tokens, alpha)

        for c in self.classes.keys():
            weight = self.__class_proba__(c)
                        
            for token in tokens:
                weight += freq[token] * math.log(
                    (self.__Nci__(c, token) + 1) / (self.__Nc__(c))
                ) * self.__classes_occurance__(token)
            classes_weights[c] = weight
        
        return sorted(classes_weights, key=lambda k: classes_weights[k], reverse=True)[:4]

def from_file(id):
    try:
        f = open("C:/Users/stoyc/Desktop/AI-project/data/{}/text.txt".format(id), 'r', encoding='utf8')
        return f.read()
    except FileNotFoundError:
        return ""

def run_tests(cnb):
    random_values = [random.randint(6000, 10000) for _ in range(3000)]
    frame = pd.read_json("C:\\Users\\stoyc\\Desktop\\AI-project\\utils\\data.json")
    frame = frame.loc[:, (frame.loc["genres"].str.len() > 0)]

    hit = 0
    miss = 0

    guessed = set()

    for idx in random_values:
        if idx not in frame.columns: continue
        document = from_file(idx)

        genres = frame[idx]["genres"]

        prediction = cnb.predict_cnbs(document)

        found = False
        for p in prediction:
            if p in genres: 
                hit += 1
                found = True
                guessed.add(p)
                print("Good {}, {}: ".format(genres, prediction))
                break
        
        if found == False: 
            miss += 1
            print("Wrong: {}, {}".format(genres, prediction))

    print("Hits {} Miss {} avg {}".format(hit, miss, hit / (hit + miss)))
    print(guessed)

cnb = CNB()    
cnb = CNB.load("C:\\Users\\stoyc\\Desktop\\AI-project\\NaiveBayes\\with_classes_count.plk")
run_tests(cnb)