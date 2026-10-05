import json
import numpy as np
import matplotlib.pyplot as plt


def round_up(number):  # round_up_to_second_decimal
    rounded_number = round(number * 100) / 100
    return rounded_number


def count_words_in_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            words = content.split()
            return len(words)

    except FileNotFoundError:
        # print(f"File not found: {file_path}")
        return None


def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_path}")
        return None


# Replace 'your_file.json' with the actual path to your JSON file
file_path = 'archive/data.json'

# Read data from the JSON file
json_data = read_json_file(file_path)

viable_texts = {}
for key, value in json_data.items():
    if (value["genres"] != []):
        viable_texts[key] = value

# print(len(viable_texts))
# print(len(json_data))
# texts_count = len(json_data)
texts_count = len(viable_texts.keys())
maxwords = 0
sum_of_words = 0
short_texts = 0
medium_short = 0
medium = 0
medium_long = 0
very_long = 0
extremely_long = 0
your_numbers = []
for i in range(1, 10000):
    if str(i) not in viable_texts:
        continue
    word_count = count_words_in_file("archive/"+str(i)+"/text.txt")
    if word_count is not None:
        sum_of_words += word_count
        your_numbers.append(word_count)
        if word_count < 50:
            short_texts += 1
        if word_count >= 50 and word_count < 150:
            medium_short += 1
        if word_count >= 150 and word_count < 1000:
            medium += 1
        if word_count >= 1000 and word_count < 10000:
            medium_long += 1
        if word_count >= 10000 and word_count < 100000:
            very_long += 1
        if word_count >= 100000:
            extremely_long += 1
        if maxwords < word_count:
            maxwords = word_count
print("Max word count is " + str(maxwords))
print("Average word count is " + str(round_up(sum_of_words/texts_count)))
print("(0-50)Extremely short texts are " + str(short_texts) +
      " which is " + str(round_up(100*short_texts/texts_count)) + "% of all texts")
print("(50-150)Medium short texts are " + str(medium_short) +
      " which is " + str(round_up(100*medium_short/texts_count)) + "% of all texts")
print("(150-1000)Medium texts are " + str(medium) +
      " which is " + str(round_up(100*medium/texts_count)) + "% of all texts")
print("Texts which are shorter than 1000 words " + str(medium + medium_short + short_texts) +
      " which is " + str(round_up(100*(medium + medium_short + short_texts)/texts_count)) + "% of all texts")
print("(1000-10_000)Medium long texts are " + str(medium_long) +
      " which is " + str(round_up(100*medium_long/texts_count)) + "% of all texts")
print("(10_000-100_000)Very long texts are " + str(very_long) +
      " which is " + str(round_up(100*very_long/texts_count)) + "% of all texts")
print("(>100_000)Extremely long texts are " + str(extremely_long) +
      " which is " + str(round_up(100*extremely_long/texts_count)) + "% of all texts")

# Data
categories = ['(0-50)Extremely short', '(50-150)Medium short',
              '(150-1000)Medium', '(1000-10_000)Medium long', '(10_000-100_000)Very long', '(>100_000)Extremely long']
counts = [short_texts, medium_short, medium,
          medium_long, very_long, extremely_long]
percentages = [round_up(100*short_texts/texts_count), round_up(100*medium_short/texts_count),
                round_up(100*medium/texts_count), round_up(100*medium_long/texts_count),
                  round_up(100*very_long/texts_count), round_up(100*extremely_long/texts_count)]

# Plotting the pie chart
plt.figure(figsize=(16, 14))
patches, texts, autotexts = plt.pie(
    percentages, labels=categories, autopct='%1.2f%%', startangle=140, colors=plt.cm.Paired.colors)

# Adding legend with counts
legend_labels = [f'{category} count:{count}' for category,
                 count in zip(categories, counts)]
plt.legend(patches, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))

plt.title("Distribution of Text Lengths")
plt.show()
