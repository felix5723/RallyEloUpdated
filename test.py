import json


def grabStats():
    with open('elo.json', encoding='utf-8') as fh:
        data = json.load(fh)

    print(type(data))
    for row in data["driver"]:
        print(data["driver"][row])


grabStats()
