from os import listdir
import csv
import json
import os
import glob

elo = {"driver": {}, "codriver": {}}
STARTINGELO = 800
K_VALUE = 32
VALUETOWARDSTOTAL = 0.75  # Antal lutning mot totalen i decimal form


def find_csv_files(folder_path):
    # Using glob to find all .csv files in the folder and subfolders
    return glob.glob(os.path.join(folder_path, '**', '*.csv'), recursive=True)


def main():
    # Specify the two folder paths
    folder_path_1 = 'Tävlingar/raceconsult'  # Replace with your first folder path
    folder_path_2 = 'Tävlingar/reallyrally'  # Replace with your second folder path
    # Replace with your second folder path
    folder_path_3 = 'Tävlingar/infiniteracing'

    # Find CSV files in both folders
    csv_files_1 = find_csv_files(folder_path_1)
    csv_files_2 = find_csv_files(folder_path_2)
    csv_files_3 = find_csv_files(folder_path_3)

    # Combine the paths from both folders
    combined_csv_files = csv_files_1 + csv_files_2 + csv_files_3

    # Sort the combined list of paths
    sorted_csv_files = sorted(
        combined_csv_files, key=lambda x: os.path.basename(x))
    # grab rally from folder
    # rallys = find_csv_filenames(sorted_csv_files)

    # gå igenom varje rally
    for path in sorted_csv_files:
        rally = path.split("\\")[-1]
        if rally == '2023-08-18 EC SNAPPHANERALLYT.csv':
            print("yesss")
        print(rally)
        with open(path, newline='', encoding="utf-8") as csvfile:
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

    eloHolderWeighted = {"driver": {"elo": 0, "People count": 0},
                         "codriver": {"elo": 0, "People count": 0}}
    eloHolderViktad = {"A": {}, "B": {}, "C": {}}
    # "J": {}, "DB": {}, "L": {}, "R": {}, "FA": {}, "FC": {}, "FB": {}}

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

            eloHolderWeighted[people["driver"]]["elo"] += elo["total"]
            eloHolderWeighted[people["driver"]]["People count"] += 1

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
                    if people["number"] == '43' and people["name"] == 'Tim Liljegren':
                        print("Tim!")
                    driverKlass = people["driverklass"]

                    hold = 0
                    time = people["time"]
                    time = time.replace(
                        "(", "").replace(")", "").replace("?", "")
                    time = time.split(",")
                    if len(time) == 2:
                        hold += int(time[1]) / 10 / 3600
                    time = time[0].split(":")
                    if len(time) > 1:
                        if len(time) == 3:
                            hold += int(time[0])
                        hold += int(time[-2]) / 60  # Minuter
                        hold += int(time[-1]) / 3600  # Sekunder
                    else:
                        time = time[0]
                        hold += int(time[-1]) / 3600  # Sekunder
                    time = hold

                    if people["driverklass"] not in eloHolderViktad:
                        eloHolderViktad[people["driverklass"]] = {}

                    if people["klass_place"] == "1" or people["klass"] not in eloHolderViktad[driverKlass]:
                        if len(eloHolderViktad[driverKlass]) > 0:
                            weightTime = next(
                                iter(eloHolderViktad[driverKlass].items()))[-1]["newTime"]
                            weight = weightTime / time
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
            else:
                people["time"] = 999
                people["weightedTime"] = 999
                continue

        weightedList = sorted(rally, key=lambda d: d['weightedTime'])

        totalElo = 0
        klassElo = 0
        viktadElo = 0
        hold = {}
        for people in rally:

            probabilitys = {}
            # Total
            totalElo, probabilitys = eloCalculator("total", people, eloHolderTotal,
                                                   people["total_place"], probabilitys)

            # Klass
            klassElo, probabilitys = eloCalculator("klass", people, eloHolderKlass,
                                                   people["klass_place"], probabilitys)

            # Weighted
            weightPlace = 0
            for weightedPeople in weightedList:
                if people["driver"] == weightedPeople["driver"]:
                    weightPlace += 1
                if people["name"] == weightedPeople["name"] and people["number"] == weightedPeople["number"]:
                    viktadElo, probabilitys = eloCalculator("weighted", people, eloHolderWeighted,
                                                            weightPlace, probabilitys)
                    break

            eloSaver(people, totalElo, klassElo, viktadElo,
                     date, rallyName, probabilitys)

        # for people in weightedList:
        #    # Weighted
        #    viktadElo, probabilitys = eloCalculator("weighted", people, eloHolderWeighted,
        #                                            people["klass_place"], probabilitys)#

        #    eloSaver("weighted", people, totalElo, klassElo, viktadElo,
        #             date, rallyName, probabilitys)

            # if len(hold) == 0:
            #    for x in range(0, len(hold)):
            #        if people["weightedTime"] < hold[x]["weightedTime"]:

            # else:
            #    hold += people


def eloChecker(name, driver):
    if name not in elo[driver]:
        elo[driver][name] = {"total": STARTINGELO,
                             "kombi": STARTINGELO, "klass": STARTINGELO, "weighted": STARTINGELO, "history": {}}
    return elo[driver][name]


def eloCalculator(total, people, competition, placement, probabilitys):
    # Variable define
    if total == "total":
        againstElo = competition[people["driver"]]["elo"]
        againstAmount = competition[people["driver"]]["People count"]
        people["total placement of"] = againstAmount
    elif total == "klass":
        againstElo = competition[people["klass"]][people["driver"]]["elo"]
        againstAmount = competition[people["klass"]
                                    ][people["driver"]]["People count"]
        people["klass placement of"] = againstAmount
    else:
        againstElo = competition[people["driver"]]["elo"]
        againstAmount = competition[people["driver"]]["People count"]
        people["total placement of"] = againstAmount - 1
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
    else:
        elo = 0
    return elo, probabilitys


def eloSaver(people, totalElo, klassElo, viktadElo, date, rallyName, probabilitys):
    driverElo = eloChecker(people["name"], people["driver"])
    types = ["total", "kombi", "klass", "weighted"]
    eloGather = {}
    for type in types:
        if type == "total":
            addElo = totalElo
        elif type == "kombi":
            addElo = totalElo * VALUETOWARDSTOTAL + \
                klassElo * (1 - VALUETOWARDSTOTAL)
        elif type == "klass":
            addElo = klassElo
        elif type == "weighted":
            addElo = viktadElo
        elo[people["driver"]][people["name"]][type] += addElo
        eloGather[type] = elo[people["driver"]][people["name"]][type]
    elo[people["driver"]][people["name"]]["history"][date] = {
        "Rally name": rallyName, "total placement": people["total_place"], "total placement of": people["total placement of"], "klass placement": people["klass_place"], "klass placement of": people["klass placement of"], "klass": people["klass"], "elo after rally": eloGather, "probabilitys": probabilitys}
    return elo, probabilitys


main()
