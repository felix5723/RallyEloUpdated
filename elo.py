from os import listdir
import csv
import json

elo = {"driver": {}, "codriver": {}}
STARTINGELO = 800
K_VALUE = 32
VALUETOWARDSTOTAL = 0.75  # Antal lutning mot totalen i decimal form


def main():
    path = "raceconsult/"
    # grab rally from folder
    rallys = find_csv_filenames(path)

    # gå igenom varje rally
    for rally in rallys:
        print(rally)
        with open(path + rally, newline='', encoding="utf-8") as csvfile:
            date = rally.split(" ")[0]
            rallyName = rally.split(" ")[1].split(".")[0] + " " + date
            rally = csv.DictReader(csvfile)
            eloMaker(rally, date, rallyName)
    with open("elo.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(elo, ensure_ascii=False, indent=2))


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def eloMaker(rally, date, rallyName):
    eloHolderTotal = {"driver": {"elo": 0, "People count": 0},
                      "codriver": {"elo": 0, "People count": 0}}
    eloHolderKlass = {}
    eloHolderViktad = {"A": {}, "B": {}, "C": {}}

    csv_data = []
    for row in rally:
        csv_data.append(row)
    rally = csv_data

    if len(rally) > 0:
        for people in rally:
            elo = eloChecker(people["name"], people["driver"])

            # Add up all elo total
            eloHolderTotal[people["driver"]]["elo"] += elo["total"]
            eloHolderTotal[people["driver"]]["People count"] += 1

            # Add up all elo klass
            if people["klass"] not in eloHolderKlass:
                eloHolderKlass[people["klass"]] = {}
            if people["driver"] not in eloHolderKlass[people["klass"]]:
                eloHolderKlass[people["klass"]][people["driver"]] = {
                    "elo": 0, "People count": 0}
            eloHolderKlass[people["klass"]
                           ][people["driver"]]["elo"] += elo["klass"]
            eloHolderKlass[people["klass"]
                           ][people["driver"]]["People count"] += 1

            # Viktad Elo
            if people["total_place"].lower() != "brutit":
                if people and people["driver"] == "driver":
                    # if people["klass"][:8].lower() == "a-förare" or people["klass"][:8].lower() == "b-förare" or people["klass"][:8].lower() == "c-förare":
                    #    klass = people["klass"].split(" ", 1)[-1]
                    # else:
                    #    klass = people["klass"]

                    klass = people["klass"]
                    if klass == "Grupp E":
                        print(klass)
                    driverKlass = people["driverklass"]

                    hold = 0
                    time = people["time"]
                    time = time.split(",")
                    if len(time) == 2:
                        hold += int(time[1]) / 10 / 3600
                    time = time[0].split(":")
                    if len(time) == 3:
                        hold += int(time[0])
                    hold += int(time[-2]) / 60
                    hold += int(time[-1]) / 3600
                    time = hold

                    if people["klass_place"] == "1" or people["klass"] not in eloHolderViktad[driverKlass]:
                        if len(eloHolderViktad[driverKlass]) > 0:
                            weight = next(
                                iter(eloHolderViktad[driverKlass].items()))[-1]["newTime"]
                            weight = weight / time
                        else:
                            weight = 1

                        if klass not in eloHolderViktad[driverKlass]:
                            eloHolderViktad[driverKlass][klass] = {
                                "orgTime": people["time"], "newTime": time, "weight": weight}
                        else:
                            if eloHolderViktad[driverKlass][klass]["newTime"] < time:
                                eloHolderViktad[driverKlass][klass] = {
                                    "orgTime": people["time"], "newTime": time, "weight": weight}

                people["time"] = time
                people["weightedTime"] = eloHolderViktad[people["driverklass"]
                                                         ][people["klass"]]["weight"] * time
                print("test")
            else:
                continue

        newlist = sorted(eloHolderViktad, key=lambda d: d['weightedTime'])

        hold = {}
        for people in rally:
            probabilitys = {}
            # Total
            totalElo, probabilitys = eloCalculator("total", people, eloHolderTotal,
                                                   people["total_place"], probabilitys)

            # Klass
            klassElo, probabilitys = eloCalculator("klass", people, eloHolderKlass,
                                                   people["klass_place"], probabilitys)

            # if len(hold) == 0:
            #    for x in range(0, len(hold)):
            #        if people["weightedTime"] < hold[x]["weightedTime"]:

            # else:
            #    hold += people

        eloSaver(people, totalElo, klassElo, date, rallyName, probabilitys)


def eloChecker(name, driver):
    if name not in elo[driver]:
        elo[driver][name] = {"total": STARTINGELO,
                             "kombi": STARTINGELO, "klass": STARTINGELO, "history": {}}
    return elo[driver][name]


def eloCalculator(total, people, competition, placement, probabilitys):
    # Variable define
    if total == "total":
        againstElo = competition[people["driver"]]["elo"]
        againstAmount = competition[people["driver"]]["People count"]
        people["total placement of"] = againstAmount
    else:
        againstElo = competition[people["klass"]][people["driver"]]["elo"]
        againstAmount = competition[people["klass"]
                                    ][people["driver"]]["People count"]
        people["klass placement of"] = againstAmount
    if placement == "brutit":
        placement = againstAmount
    elo = 0

    if againstAmount > 1:
        # Prob outcome based on ELO
        driverElo = eloChecker(people["name"], people["driver"])[total]
        againstElo = againstElo / againstAmount
        probOutcome = 1 / (1+(10**((againstElo-driverElo)/400)))

        # Actual outcome based on position
        outcome = 1-(int(placement)-1) / (int(againstAmount)-1)

        # Calculate the outcome
        elo = K_VALUE*(outcome-probOutcome)

        probabilitys[total] = {"Outcome": outcome, "Probabilty": probOutcome}
    return elo, probabilitys


def eloSaver(people, totalElo, klassElo, date, rallyName, probabilitys):
    driverElo = eloChecker(people["name"], people["driver"])
    types = ["total", "kombi", "klass"]
    eloGather = {}
    for type in types:
        if type == "total":
            addElo = totalElo
        elif type == "kombi":
            addElo = totalElo * VALUETOWARDSTOTAL + \
                klassElo * (1 - VALUETOWARDSTOTAL)
        elif type == "klass":
            addElo = klassElo
        elo[people["driver"]][people["name"]][type] += addElo
        eloGather[type] = elo[people["driver"]][people["name"]][type]
    elo[people["driver"]][people["name"]]["history"][date] = {
        "Rally name": rallyName, "total placement": people["total_place"], "total placement of": people["total placement of"], "klass placement": people["klass_place"], "klass placement of": people["klass placement of"], "klass": people["klass"], "elo after rally": eloGather, "probabilitys": probabilitys}
    return elo, probabilitys


main()
