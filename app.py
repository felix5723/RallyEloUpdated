from flask import Flask, render_template, send_from_directory, request, jsonify
import json
import time
import sqlite3
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

app = Flask(__name__)


def database_connect():
    # Connect to the database (it will create the file if it doesn't exist)
    # You can change the name as needed
    conn = sqlite3.connect('my_database.db')

    cursor = conn.cursor()
    return cursor, conn


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/css/<path:filename>')
def send_css(filename):
    return send_from_directory('css', filename)


@app.route('/drivers/<seat>')
def drivers(seat):
    cursor, conn = database_connect()
    driversList = []
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    for row in rows:
        if row[1] == seat or seat == 'all':
            driversList.append(row)
    return render_template('drivers_search.html', rows=driversList)


def create_graph_1():
    # Example data for the first graph
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.figure()
    plt.plot(x, y, label='Sine Wave')
    plt.title('Graph 1: Sine Wave')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()

    # Save to a PNG in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()  # Close the figure to avoid display issues
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def create_graph_2():
    # Example data for the second graph
    x = np.linspace(0, 10, 100)
    y = np.cos(x)

    plt.figure()
    plt.plot(x, y, label='Cosine Wave', color='orange')
    plt.title('Graph 2: Cosine Wave')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()

    # Save to a PNG in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()  # Close the figure to avoid display issues
    return base64.b64encode(buf.getvalue()).decode('utf-8')


@app.route('/profil/<id>/<name>/<klubb>')
def profil(id, name, klubb):
    cursor, conn = database_connect()
    cursor.execute('SELECT * FROM userStats WHERE user_id = ?', (id,))
    # Define labels
    labels = []
    klass = []
    klass_of = []
    total = []
    total_of = []
    user_stats = cursor.fetchall()
    for stat in user_stats:
        print(stat)
        labels.append(stat[2] + " " + stat[3])
        klass.append(stat[-1])
        total.append(stat[-2])

        cursor.execute('SELECT * FROM userStats WHERE rallyName = ? AND rallyDate = ? AND driver = ? AND klass = ?',
                       (stat[2], stat[3], stat[4], stat[7]))
        hold = cursor.fetchall()
        klass_of.append(len(hold))

        cursor.execute(
            'SELECT * FROM userStats WHERE rallyName = ? AND rallyDate = ? AND driver = ?', (stat[2], stat[3], stat[4]))
        hold = cursor.fetchall()
        total_of.append(len(hold))

    return render_template('profil.html', name=name, klubb=klubb, labels=labels, klass=klass, klass_of=klass_of, total=total, total_of=total_of)


@app.route('/elo')
def index():
    type_elo = "new"  # new or old

    searchName = "Patrik Flodin"

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

    return render_template('index.html', eloTotal=drivereloTotal, eloKombi=drivereloKombi, eloKlass=drivereloKlass, eloWeighted=drivereloWeighted, labels=driverlabels, codrivereloTotal=codrivereloTotal, codrivereloKombi=codrivereloKombi, codrivereloKlass=codrivereloKlass, codrivereloWeighted=codrivereloWeighted, codriverlabels=codriverlabels)


if __name__ == "__main__":
    app.run(debug=True)
