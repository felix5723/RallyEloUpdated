from flask import Flask, render_template
import json
import time

app = Flask(__name__)


@app.route('/')
def index():
    with open('elo.json', encoding='utf-8') as fh:
        data = json.load(fh)

    elo = [(800, 800, 800)]
    rallyName = ["Start"]

    print(type(data))
    # print(data)
    for name in data["driver"]:
        if name.lower() == "Hugo Sääf".lower():
            print(data["driver"][name])
            for rally in data["driver"][name]["history"]:
                print(data["driver"][name]["history"][rally])
                elo.append((data["driver"][name]["history"]
                           [rally]["elo after rally"]["total"], data["driver"][name]["history"]
                           [rally]["elo after rally"]["kombi"], data["driver"][name]["history"]
                           [rally]["elo after rally"]["klass"]))
                rallyName.append(data["driver"][name]["history"][rally]["Rally name"] +
                                 " " + data["driver"][name]["history"][rally]["klass"])
            continue

    print(elo)
    print(rallyName)

    eloTotal = [row[0] for row in elo]
    eloKombi = [row[1] for row in elo]
    eloKlass = [row[2] for row in elo]
    labels = rallyName
    print("----------")
    print(eloTotal)
    print(eloKombi)
    print(eloKlass)
    print(labels)

    return render_template('index.html', eloTotal=eloTotal, eloKombi=eloKombi, eloKlass=eloKlass, labels=labels)


if __name__ == "__main__":
    app.run(debug=True)
