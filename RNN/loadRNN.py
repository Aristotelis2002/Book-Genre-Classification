import json
import random
from stop_words import get_stop_words
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
 
MODEL_TO_LOAD = "modelK3.h5" 
NUMBER_OF_TEXTS_TO_TEST = 1000
EPSILON = 65 # in percentages
MAX_WORDS = 150_000
MAX_LEN = 10
TRUNCATE_TO = 50000
def read_file(file_path):
    try:
        with open(file_path, 'r', encoding="utf8") as file:
            file_contents = file.read()
        return file_contents
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

 
def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding="utf8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None
 
def get_testing_corpus(key_for_each_text, texts):
    test_keys = []
    try:
        with open("keys.txt", 'r', encoding='utf-8') as file:
            test_keys = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File not found")
    testing_indexes = []
    testing_texts = []
    for i in range(len(texts)):
        if key_for_each_text[i] in test_keys:
            testing_texts.append(texts[i])
            testing_indexes.append(i)
    return testing_texts, testing_indexes

def generate_texts_for_tests(count, texts, total_number_of_texts):
    testing_indexes = []
    testing_texts = []
    i = 0
    while i < count:
        random_int = random.randint(0, total_number_of_texts - 1)
        if random_int not in testing_indexes:
            testing_texts.append(texts[random_int])
            testing_indexes.append(random_int)
            i += 1
    return testing_texts, testing_indexes

# Returns a [[genres]] where each array of genres matches the true genres of indexes
def get_wanted_genres(count, testing_indexes, labels):
    wanted_genres = []
    for i in range(0, count):
        wanted_genres.append(labels[testing_indexes[i]])
    return wanted_genres

def calculate_optimal_threshold(predictions, epsilon, top_many):
    max_prediction = max(predictions)
    epsilon = max_prediction*(epsilon/100)
    viable_top_n = list(filter(lambda x: max_prediction - x < epsilon, predictions))
    return min(viable_top_n) - 0.0000001

def calculate_test_accuracy(predictions, wanted_genres):
    tests = len(predictions)
    correct_guesses = 0
    for i in range(0, len(predictions)):
     for j in range(0, len(p)):
         if predictions[i][j] == 1 and wanted_genres[i][j] == 1:
            correct_guesses += 1
            break
    return correct_guesses/tests 

def remove_stop_words(words):
    stop_bg = get_stop_words('bg')
    refined_words = list(filter(lambda x: x not in stop_bg, words))
    return refined_words

def truncate_string_by_words(input_string, n):
    words = input_string.split()
    words = remove_stop_words(words)
    if len(words) <= n:
        return input_string
    
    truncated_words = words[:n]
    truncated_string = ' '.join(truncated_words)
    return truncated_string

def format_texts(texts):
    translation_table = str.maketrans("","", ".,_!?“-„:—\t… \n*()><{}[]\xa0")
    for i in range(len(texts)):
        texts[i] = str.lower(texts[i])
        texts[i] = texts[i].translate(translation_table)
        texts[i] = truncate_string_by_words(texts[i], TRUNCATE_TO)

file_path = '../data/data.json'
 
json_data = read_json_file(file_path)
 
viable_texts = {} # texts which have genres
for key, value in json_data.items():
    if (value["genres"] != []):
        viable_texts[key] = value

genres_indexes = {} # genres to indexes, this is needed to create the labels for each text
index = 0
for key, value in viable_texts.items():
    for genre in value["genres"]:
        if genre not in genres_indexes.keys():
            genres_indexes[genre] = index
            index += 1

output_file = open('IMPORTANT2.txt', 'w', encoding='utf-8')
for keyche, indeksche in genres_indexes.items():
    print(keyche + "->" + str(indeksche), file=output_file)
output_file.close()

indexes_genres = {}  # reverse from index to the genre , this is needed for labels
for key, value in genres_indexes.items():
    indexes_genres[value] = key

texts_dict = {}
for i in range(1, 10000):
    if str(i) not in viable_texts:
        continue
    texts_dict[str(i)] = read_file("../data/"+str(i)+"/text.txt")
print("Reading done")

indexes_to_keys = {}
i = 0
texts = []
key_for_each_text = [] # if you want to get the key of texts[i] just do key_for_each_text[i]
labels = [] # at index i array of genres of the texts[i] , array of genres is from zeroes and ones 
for key, value in viable_texts.items():
    indexes_to_keys[i] = key
    texts.append(texts_dict[key])
    key_for_each_text.append(key)
    label_current = [0] * len(genres_indexes) 
    for genre in value["genres"]:
        label_current[genres_indexes[genre]] = 1
    labels.append(label_current)
    i += 1
print("Labeling done")

format_texts(texts)
print("Text formatting done")

max_words = MAX_WORDS  # Maximum number of words in the vocabulary
max_len = MAX_LEN  # Maximum length of a sequence

loaded_model = load_model(MODEL_TO_LOAD)
# print(loaded_model.summary())
# loaded_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

number_of_texts_to_test = NUMBER_OF_TEXTS_TO_TEST
testing_texts, testing_indexes = generate_texts_for_tests(number_of_texts_to_test, texts, len(viable_texts))
# testing_texts, testing_indexes = get_testing_corpus(key_for_each_text, texts)
wanted_genres = get_wanted_genres(number_of_texts_to_test, testing_indexes, labels)
# wanted_genres = get_wanted_genres(len(testing_indexes), testing_indexes, labels)

# print(len(testing_texts))

tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(testing_texts)
new_sequence = tokenizer.texts_to_sequences(testing_texts)
new_X = pad_sequences(new_sequence, maxlen=max_len)
prediction = loaded_model.predict(new_X)

# print("Raw Predictions:")
# print(prediction)

# Threshold the prediction
# threshold = 0.3
# final_predictions = (prediction > threshold).astype(int)
final_predictions = []
index = 0
output_file = open('test_output.txt', 'w', encoding='utf-8')
key_to_threshold = {}
for p in prediction:
    threshold = calculate_optimal_threshold(p, EPSILON, 1)
    final_predictions.append((p>threshold).astype(int))
    # print("For key #" + str(key_for_each_text[testing_indexes[index]]) +" THRESHOLD IS -> " + str(threshold), file=output_file)
    key_to_threshold[key_for_each_text[testing_indexes[index]]] = threshold
    index += 1

# print("The keys which we are testing on are")
# for index in testing_indexes:
    # print(key_for_each_text[index])
# Print the final predictions for the new texts
# print("Final Predictions:")
# # print(final_predictions)
# for j in range(0, len(final_predictions) - 950):
#     print(str(j) + "__________")
#     for i in range(0, len(final_predictions[j])):
#         if final_predictions[j][i] == 1 :
#            print(indexes_genres[i])
# print("Wanted genres")
# print(wanted_genres)
succesfull_keys = []
for j in range(0, len(final_predictions)):
    print("#" + key_for_each_text[testing_indexes[j]] + " __________", file=output_file)
    gussed_genres = []
    for i in range(0, len(final_predictions[j])):
        if final_predictions[j][i] == 1 :
           print("--" + indexes_genres[i], file=output_file)
           gussed_genres.append(indexes_genres[i])
    print("Where wanted genres are", file=output_file)
    actual_genres = []
    for i in range(0, len(wanted_genres[j])):
        if wanted_genres[j][i] == 1:
           print(indexes_genres[i], file=output_file)
           actual_genres.append(indexes_genres[i])
    if (set(gussed_genres) & set(actual_genres)):
        print("A HIT!!", file=output_file)
        succesfull_keys.append(key_for_each_text[testing_indexes[j]])
    print("Key -> #"+str(key_for_each_text[testing_indexes[j]])+" with threshold " 
          + str(key_to_threshold[key_for_each_text[testing_indexes[j]]]), file=output_file)
# print(succesfull_keys, file=output_file)
for key in succesfull_keys:
    print("Key -> #"+str(key)+" with threshold " + str(key_to_threshold[key]), file=output_file)
output_file.close()

# for j in range(0, len(wanted_genres)):
#     print(str(j) + "__________")
#     for i in range(0, len(wanted_genres[j])):
#       if wanted_genres[j][i] == 1:
#         print(indexes_genres[i])

print("Overall accuracy is")
print(calculate_test_accuracy(final_predictions, wanted_genres))
# TO DO FIX THE PRINTING GENRES AT END
# TO DO ADD Epsilon AND GET MAX FORM PREDICIONS LOGIC
# output_file = open('output_file.txt', 'w', encoding='utf-8')
# output_file.close()