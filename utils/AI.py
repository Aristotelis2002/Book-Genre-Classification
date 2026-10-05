import json
import matplotlib.pyplot as plt

genre = dict()

def increment(elem: str):
    if genre.get(elem) != None:
        genre[elem] += 1
    else:
        genre[elem] = 0

def init_genre(obj):
    if len(json_data[obj]['genres']) == 0:
        increment("None")
    else:
        for genre in json_data[obj]['genres']:
            # print(genre)
            increment(genre)


file = open("data.json", "r", encoding="utf-8")
data: str = file.read()
json_data = json.loads(data)

for obj in json_data:
    init_genre(obj)

labels = list()
sizes  = list()

for key in genre.keys():
    if(genre[key] > 170):
        labels.append(key)
    else:
        labels.append("")
    
    sizes.append(genre[key])

fig, ax = plt.subplots()
ax.pie(sizes, labels=labels)
plt.show()