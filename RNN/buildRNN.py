import json
import random
import numpy as np
from stop_words import get_stop_words
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
 
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
 
def get_all_genres(viable_texts):
    genres = []
    for key, val in viable_texts.items():
        for genre in val["genres"]:
            if genre not in genres:
                genres.append(genre)
    return genres

def calculate_average_amount(genres_to_keys): # it calculates the average amount of texts in each genre
    sum_of_texts = 0
    for key, val in genres_to_keys.items():
        sum_of_texts += len(val)
    print("Average amount is -> " + str(int(sum_of_texts/(len(genres_to_keys)))))
    return int(10*sum_of_texts/(len(genres_to_keys)))


def save_keys_to_file(keys, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for key in keys:
            file.write(key + '\n')

def remove_and_save_random_keys(my_dict):
    keys_to_remove = list(my_dict.keys())
    random.shuffle(keys_to_remove)
    keys_to_remove = keys_to_remove[:200]
    save_keys_to_file(keys_to_remove, 'keys.txt')
    removed_elements = {key: my_dict.pop(key) for key in keys_to_remove}

    # return removed_elements


def generate_dict_for_testing(viable_texts):
    remove_and_save_random_keys(viable_texts)
    return viable_texts
    genres_to_keys = {}
    viable_texts = dict(sorted(viable_texts.items(), key=lambda item: len(item[1]["genres"])))
    for key, val in viable_texts.items():
        for genre in val["genres"]:
            if genre in genres_to_keys:
                genres_to_keys[genre].append(key)
            else:
                genres_to_keys[genre] = [key]
    avg = calculate_average_amount(genres_to_keys)
    sampled_keys = []
    for key, val in genres_to_keys.items():
        selected_elements = random.sample(val, avg) if len(val) >= avg else val
        sampled_keys.extend(selected_elements)
    sampled_keys = list(dict.fromkeys(sampled_keys)) # removes duplicates
    filtered_dict = {key: value for key, value in viable_texts.items() if key in sampled_keys}
    return filtered_dict

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

indexes_genres = {}  # reverse from index to the genre , this is needed for labels
for key, value in genres_indexes.items():
    indexes_genres[value] = key

texts_dict = {}
for i in range(1, 10000):
    if str(i) not in viable_texts:
        continue
    texts_dict[str(i)] = read_file("../data/"+str(i)+"/text.txt")
print("Reading done")

viable_texts = generate_dict_for_testing(viable_texts)
print(len(viable_texts))

output_file = open('IMPORTANT.txt', 'w', encoding='utf-8')
for keyche, indeksche in genres_indexes.items():
    print(keyche + "->" + str(indeksche), file=output_file)
output_file.close()

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

output_file = open('output_file.txt', 'w', encoding='utf-8')
for key, val in viable_texts.items():
    print("Key is -> " + str(key), file=output_file)
    for x in val["genres"]:
        print(x, file=output_file)
output_file.close()

# for i in range(0, len(labels)):
#     for j in range(0, len(labels[i])):
#         if labels[i][j] == 1:
#             print(indexes_genres[j])
# labels = np.array(labels)
# total_samples = len(labels)
# class_frequencies = [np.sum(labels[:, i]) for i in range(len(labels[0]))]
# class_weights = {i: total_samples / (len(labels) * freq) for i, freq in enumerate(class_frequencies)}
# print(class_weights)
# for key,val in class_weights.items():
#     print(str(indexes_genres[key]) + "->" + str(val))
 
# Tokenize and pad sequences
max_words = MAX_WORDS  # Maximum number of words in the vocabulary
max_len = MAX_LEN  # Maximum length of a sequence
 
tokenizer = Tokenizer(num_words=max_words)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
X = pad_sequences(sequences, maxlen=max_len)

print("Tokenizing and sequencing done")


embedding_dim = 50  # Dimension of word embeddings
model = Sequential()
model.add(Embedding(input_dim=max_words, output_dim=embedding_dim, input_length=max_len))
model.add(LSTM(10)) 
model.add(Dense(len(labels[0]), activation='sigmoid'))
 
print("RNN building done")

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
 
X = np.array(X)
labels = np.array(labels)

epochs = 230
batch_size = 10
model.fit(X, labels, epochs=epochs, batch_size=batch_size, validation_split=0.2)
# model.fit(X, labels, epochs=epochs, batch_size=batch_size, validation_split=0.2)
# model.fit(X, labels, epochs=epochs, batch_size=batch_size, validation_split=0.2, class_weight=class_weights)
print("Training of model done")

model.save('modelK3.h5')
print("Model saved")

# Now, you can use the trained model to predict the classes for new texts
number_of_texts_to_test = 30
testing_texts, testing_indexes = generate_texts_for_tests(number_of_texts_to_test, texts, len(viable_texts))
wanted_genres = get_wanted_genres(number_of_texts_to_test, testing_indexes, labels)
new_sequences = tokenizer.texts_to_sequences(testing_texts)
new_X = pad_sequences(new_sequences, maxlen=max_len)
predictions = model.predict(new_X)
 
# You can then threshold the predictions to obtain the final classes
threshold = 0.3
final_predictions = (predictions > threshold).astype(int)
 
print("The keys which we are testing on are")
for index in testing_indexes:
    print(key_for_each_text[index])
# Print the final predictions for the new texts
print("Final Predictions:")
# print(final_predictions)
for j in range(0, len(final_predictions)):
    print(str(j) + "__________")
    for i in range(0, len(final_predictions[j])):
        if final_predictions[j][i] == 1 :
           print(indexes_genres[i])
# raise Exception("Custom message")
print("Wanted genres")
# print(wanted_genres)
for j in range(0, len(wanted_genres)):
    print(str(j) + "__________")
    for i in range(0, len(wanted_genres[j])):
      if wanted_genres[j][i] == 1:
        print(indexes_genres[i])
        
def save_training_keys(viable_texts):
    output_file = open('keys.txt', 'w', encoding='utf-8')
    for key, _ in viable_texts.items():
        print(key, file=output_file)
    output_file.close()

# save_training_keys(viable_texts)