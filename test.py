import json


type_elo = "new"  # new or old

searchName = "Felix Holmsten"

if type_elo.lower() == "new":
    with open('new_elo.json', encoding='utf-8') as fh:
        data = json.load(fh)
    for position in ["driver", "codriver"]:
        for name in data[position]:
            if name[:len(searchName)].lower() == searchName.lower():
                for row in data[position][name]["elo"]["history"]:
                    row["kombi"] = 800
                    row["weighted"] = 800
                    print(row)
        data[position][name]["history"] = data[position][name]["elo"]["history"]
elif type_elo.lower() == "old":
    with open('elo.json', encoding='utf-8') as fh:
        data = json.load(fh)

elo = {"driver": [(800, 800, 800, 800)], "codriver": [
    (800, 800, 800, 800)]}
rallyName = {"driver": ["Start"], "codriver": ["Start"]}

# print(type(data))
# print(data)
if type_elo.lower() == "new":
    for position in ["driver", "codriver"]:
        for name in data[position]:
            if name[:len(searchName)].lower() == searchName.lower():
                for rally in data[position][name]["elo"]["history"]:
                    elo[position].append(
                        (rally["total_elo"], rally["kombi"], rally["klass_elo"], rally["weighted"]))
                    rallyName[position].append(rally["rallyName"] +
                                               " " + rally["klass"])
                continue
elif type_elo.lower() == "old":
    for position in ["driver", "codriver"]:
        for name in data[position]:
            if name[:len(searchName)].lower() == searchName.lower():
                print(data[position][name])
                for rally in data[position][name]["history"]:
                    print("---")
                    print(data[position][name]["history"][rally])
                    print("---")
                    elo[position].append((data[position][name]["history"]
                                          [rally]["elo after rally"]["total"], data[position][name]["history"]
                                          [rally]["elo after rally"]["kombi"], data[position][name]["history"]
                                          [rally]["elo after rally"]["klass"], data[position][name]["history"]
                                          [rally]["elo after rally"]["weighted"]))
                    rallyName[position].append(data[position][name]["history"][rally]["Rally name"] +
                                               " " + data[position][name]["history"][rally]["klass"])
                    print(data[position][name]["history"]
                          [rally]["elo after rally"])
                continue

print(elo["driver"])
print(rallyName)
print(elo)

drivereloTotal = [row[0] for row in elo["driver"]]
drivereloKombi = [row[1] for row in elo["driver"]]
drivereloKlass = [row[2] for row in elo["driver"]]
drivereloWeighted = [row[3] for row in elo["driver"]]
driverlabels = rallyName["driver"]
codrivereloTotal = [row[0] for row in elo["codriver"]]
codrivereloKombi = [row[1] for row in elo["codriver"]]
codrivereloKlass = [row[2] for row in elo["codriver"]]
codrivereloWeighted = [row[3] for row in elo["codriver"]]
codriverlabels = rallyName["codriver"]
print("----------")
print(drivereloTotal)
print(drivereloKombi)
print(drivereloKlass)
print(drivereloWeighted)
print(driverlabels)
