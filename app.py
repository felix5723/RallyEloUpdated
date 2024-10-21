from flask import Flask, render_template, send_from_directory, request, jsonify
from Olika_hemsidor.alla import main as rallygrabber
from elo_database import main as elograbber
from Olika_hemsidor.database import datebase_start as datebase_start
# from apscheduler.schedulers.background import BackgroundScheduler
import json
import time
import sqlite3
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from datetime import datetime, timedelta

MAX_RALLYS = 20
CHOICE = "go"  # go / refresh

app = Flask(__name__)


# Skapa en schemaläggare
# scheduler = BackgroundScheduler()

# Definiera en uppgift som ska köras


def scheduled_update():
    print("Schemalagd uppdatering körs!")
    # Din funktion för att hämta resultat


def rally_updater():
    cursor, conn = database_connect()
    cursor.execute(
        'SELECT * FROM rallys ORDER BY rallyDate DESC')
    rallys = cursor.fetchall()
    if len(rallys) > 0:
        print(rallys)
        newest_index = len(rallys)
        date = rallys[0][-1]
        date = datetime.strptime(date, "%Y-%m-%d")
    else:
        date = None
    rallygrabber(MAX_RALLYS, CHOICE)

    if date != None:
        cursor.execute(
            'SELECT * FROM rallys ORDER BY rallyDate DESC')
        rallys = cursor.fetchall()
        for x in range(newest_index, len(rallys)-1):
            print(f'ID: {x+1} av {len(rallys)}')
            test_date = rallys[x][-1]
            # Convert strings to datetime objects
            test_date = datetime.strptime(test_date, "%Y-%m-%d")
            print(f'{date} > {test_date}')
            if date > test_date:
                print("We need to redo elo")
                elograbber(redo=True)
                return
        elograbber(redo=False)
    else:
        elograbber(redo=True)
    return


# Lägg till en uppgift som körs var 12:e timme
# scheduler.add_job(func=scheduled_update, trigger="interval", hours=12)
# Lägg till ett cron-jobb som körs varje söndag kl. 10:00
# scheduler.add_job(func=rally_updater, trigger='cron',
#                  day_of_week='sun', hour=20, minute=00, max_instances=1)


# Starta schemaläggaren
# scheduler.start()


def database_connect():
    # Connect to the database (it will create the file if it doesn't exist)
    # You can change the name as needed
    conn = sqlite3.connect('my_database.db')

    cursor = conn.cursor()
    return cursor, conn


@app.route('/')
def homepage():
    # rally_updater()
    return render_template('homepage.html')


@app.route('/update')
def homepage2():
    rallygrabber()
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


@app.route('/profil/<id>/<name>/<klubb>/<placement>')
def profil(id, name, klubb, placement):
    if placement == 'placement':
        cursor, conn = database_connect()
        cursor.execute(
            'SELECT * FROM userStats WHERE user_id = ? ORDER BY rallyDate', (id,))
        user_stats = cursor.fetchall()
        # Define labels
        labels = []
        klass = []
        klass_of = []
        total = []
        total_of = []
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

        return render_template('profil.html', id=id, name=name, placement=placement, klubb=klubb, labels=labels, klass=klass, klass_of=klass_of, total=total, total_of=total_of)
    else:
        print("yippie")
        cursor, conn = database_connect()
        cursor.execute('SELECT * FROM userselo WHERE user_id = ?', (id,))
        user_stats = cursor.fetchall()
        print(user_stats)
        # Define labels
        labels = []
        klass_elo = []
        total_elo = []
        for stat in user_stats:
            print(stat)
            labels.append(stat[3] + " " + stat[4])
            klass_elo.append(stat[-1])
            total_elo.append(stat[-2])

        return render_template('profil.html', id=id, name=name, placement=placement, klubb=klubb, labels=labels, klass_elo=klass_elo, total_elo=total_elo)


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
# if __name__ == "__main__":
#    try:
#        datebase_start()
#        app.run(debug=True, use_reloader=False)
#    except (KeyboardInterrupt, SystemExit):
#        scheduler.shutdown()
