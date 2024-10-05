from flask import Flask, render_template
import json
import time

app = Flask(__name__)


@app.route('/')
def index():

    searchName = "Felix Holmsten"

    with open('elo.json', encoding='utf-8') as fh:
        data = json.load(fh)

    elo = {"driver": [(800, 800, 800, 800)], "codriver": [
        (800, 800, 800, 800)]}
    rallyName = {"driver": ["Start"], "codriver": ["Start"]}

    print(type(data))
    # print(data)
    for position in ["driver", "codriver"]:
        for name in data[position]:
            if name.lower() == searchName.lower():
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

    return render_template('index.html', eloTotal=drivereloTotal, eloKombi=drivereloKombi, eloKlass=drivereloKlass, eloWeighted=drivereloWeighted, labels=driverlabels, codrivereloTotal=codrivereloTotal, codrivereloKombi=codrivereloKombi, codrivereloKlass=codrivereloKlass, codrivereloWeighted=codrivereloWeighted, codriverlabels=codriverlabels)


if __name__ == "__main__":
    app.run(debug=True)
