from os import listdir
import csv
import json
import os
import glob

elo = {"driver": {}, "codriver": {}}
STARTINGELO = 800
K_VALUE = 32
K_FAKTOR_MAX = 3
VALUETOWARDSTOTAL = 0.75  # Antal lutning mot totalen i decimal form


def find_csv_files(folder_path):
    # Using glob to find all .csv files in the folder and subfolders
    return glob.glob(os.path.join(folder_path, '**', '*.csv'), recursive=True)


def find_files():
    # Specify the two folder paths
    folder_path_1 = 'Tävlingar/raceconsult'  # Replace with your first folder path
    folder_path_2 = 'Tävlingar/reallyrally'  # Replace with your second folder path
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

    return sorted_csv_files


def turn_into_data(sorted_csv_files):
    # gå igenom varje rally
    rallys = []
    for path in sorted_csv_files:
        hold = {}
        rally = path.split("\\")[-1]
        print(rally)
        with open(path, newline='', encoding="utf-8") as csvfile:
            date = rally.split(" ")[0]
            rallyName = rally.split(" ")[1].split(".")[0] + " " + date
            rally = csv.DictReader(csvfile)

            hold["date"] = date
            hold["rallyName"] = rallyName
            csv_data = []
            for row in rally:
                csv_data.append(row)
            rally = csv_data
            hold["data"] = rally
            csvfile.close()
        rallys.append(hold)
    return rallys


def count_same_value(list_of_dicts, key, value_to_find):
    return sum(1 for person in list_of_dicts if person.get(key) == value_to_find)


def placement_of_counter(rally):
    drivers = rally["data"]
    total_amounts = {"total": 0}
    for driver in drivers:
        if driver["driver"] == "driver":
            if driver["klass"] not in total_amounts:
                total_amounts[driver["klass"]] = 0
            total_amounts[driver["klass"]] += 1
            total_amounts["total"] += 1

    for driver in drivers:
        # len(driver["klass"] in drivers)
        driver["total_place_of"] = total_amounts["total"]
        driver["klass_place_of"] = total_amounts[driver["klass"]]
    return rally


def dnf_checker(rally):
    drivers = rally["data"]
    total_amount = len(drivers)
    for driver in drivers:
        dnf = False
        if driver["total_place"].lower() == "brutit":
            dnf = True
        driver["dnf"] = dnf
    return rally


def check_driver_in_driversData(driversData, data):
    date = data["date"]
    rallyName = data["rallyName"]
    drivers = data["data"]
    for driver in drivers:
        driver_combined = driver["name"] + " - " + driver["klubb"]
        seat = driver["driver"]
        if driver_combined not in driversData[seat]:
            driversData[seat][driver_combined] = {
                "k_faktor": 1,
                "elo": {"total_elo": 800, "klass_elo": 800, "history": {}},
                "rallys": {date: {"date": date, "rallyName": rallyName, "klass": driver["klass"], "data": driver}}}
        else:
            driversData[seat][driver_combined]["rallys"][date] = {
                "date": date, "rallyName": rallyName, "klass": driver["klass"], "data": driver}
    return driversData


def find_driver_in_driversData(driver, driversData):
    driver_combined = driver["name"] + " - " + driver["klubb"]
    if driver_combined in driversData[driver["driver"]]:
        return driver_combined
    return None


def dynamic_K_faktor(rallys, k_faktor):
    if len(rallys) > 10:
        last_key = next(reversed(rallys))
        if rallys[last_key]["data"]["dnf"] == False:
            k_faktor = round(k_faktor + 0.1, 2)
            if k_faktor > K_FAKTOR_MAX:
                k_faktor = K_FAKTOR_MAX
            return k_faktor
        else:
            return 1
    elif 0 < len(rallys) < 10:
        return K_FAKTOR_MAX
    else:
        return 1


def elo_calculator(driver, driversData, elo_gathered, date, rallyName):
    # Skapa variabler
    seat = driver["driver"]
    placement = {
        "total": driver["total_place"], "klass": driver["klass_place"]}
    againstAmountDict = {
        "total": driver["total_place_of"], "klass": driver["klass_place_of"]}

    # Hitta elon och ta sedan bort den från elo_gatherd
    if driver["name"] == "Felix Holmsten":
        print("stop")
    driver_combined = find_driver_in_driversData(driver, driversData)
    elo_data = driversData[seat][driver_combined]["elo"]
    driverEloDict = {
        "total": elo_data["total_elo"], "klass": elo_data["klass_elo"]}

    for klass in againstAmountDict:
        againstAmount = againstAmountDict[klass] - 1
        driverPlacement = placement[klass]
        if driverPlacement.lower() == "brutit":
            driverPlacement = againstAmount
        driverElo = driverEloDict[klass]

        if klass == "total":
            k_faktor = dynamic_K_faktor(
                driversData[seat][driver_combined]["rallys"], driversData[seat][driver_combined]["k_faktor"])

            againstElo = elo_gathered[seat]["total"] - elo_data["total_elo"]
        else:
            againstElo = elo_gathered[seat]["klass"][driver["klass"]
                                                     ] - elo_data["klass_elo"]

        if againstAmount > 1:
            # Prob outcome based on ELO
            againstElo = againstElo / againstAmount
            probOutcome = 1 / (1+(10**((againstElo-driverElo)/400)))

            # Actual outcome based on position
            outcome = 1-(int(driverPlacement)-1) / (int(againstAmount)-1)

            # Calculate the outcome
            elo = K_VALUE*k_faktor*(outcome-probOutcome)
            driversData[seat][driver_combined]["k_faktor"] = k_faktor
            if klass == "total":
                total_prob = {"Outcome": outcome,
                              "Probability": probOutcome, "Elo change": elo}
            else:
                klass_prob = {"Outcome": outcome,
                              "Probability": probOutcome, "Elo change": elo}
        else:
            if klass == "total":
                total_prob = {"Outcome": 0.5,
                              "Probability": 0.5, "Elo change": 0}
            else:
                klass_prob = {"Outcome": 0.5,
                              "Probability": 0.5, "Elo change": 0}
            elo = 0
        elo_data[klass+"_elo"] += elo

    # Spara elon i history
    elo_data["history"][date] = {"rallyName": rallyName, "date": date, "klass": driver["klass"],
                                 "total_elo": elo_data["total_elo"], "klass_elo": elo_data["klass_elo"],
                                 "probabilitys": {"total": total_prob, "klass": klass_prob}}


def elo_graber(driversData, driversInRally):
    elo_gathered = {"driver": {"total": 0, "klass": {}},
                    "codriver": {"total": 0, "klass": {}}}
    for driver in driversInRally:
        seat = driver["driver"]
        driver_klass = driver["klass"]
        driver_combined = find_driver_in_driversData(driver, driversData)
        if driver_combined:
            driver_elo = driversData[seat][driver_combined]["elo"]
            elo_gathered[seat]["total"] += driver_elo["total_elo"]
            if driver["klass"] not in elo_gathered[seat]["klass"]:
                elo_gathered[seat]["klass"][driver_klass] = 0
            elo_gathered[seat]["klass"][driver_klass] += driver_elo["klass_elo"]
    return elo_gathered


def elo_uppdater(driversData, winnerTime, rally):
    date = rally["date"]
    rallyName = rally["rallyName"]
    data = rally["data"]
    elo_gathered = elo_graber(driversData, data)
    for driver in data:
        elo_calculator(driver, driversData, elo_gathered, date, rallyName)


def turn_time_into_hour(before_time):
    after_time = 0
    before_time = before_time.replace(
        "(", "").replace(")", "").replace("?", "")  # Hade velat få bort den här
    before_time = before_time.split(",")
    if len(before_time) == 2:
        after_time += int(before_time[1]) / 60 / 60 / 10  # 10:dels sekund
    before_time = before_time[0]

    before_time = before_time.split(":")
    if len(before_time) == 3:  # Om det finns en timme
        after_time += int(before_time[0])  # Timme
        after_time += int(before_time[1]) / 60  # Minut
        after_time += int(before_time[2]) / 60 / 60  # Sekund
    elif len(before_time) == 2:  # Om det finns en timme
        after_time += int(before_time[0]) / 60  # Minut
        after_time += int(before_time[1]) / 60 / 60  # Sekund
    elif len(before_time) == 1:  # Om det finns en timme
        after_time += int(before_time[0]) / 60 / 60  # Sekund

    return after_time


def finder_winner_per_class(förare_data):
    vinnartider = {}
    for förare in förare_data:
        if förare["dnf"] == False:
            klass = förare["klass"]
            tid = turn_time_into_hour(förare["time"])
            if klass not in vinnartider or tid < vinnartider[klass]:
                vinnartider[klass] = tid
            if förare["total_place"] == '1':
                vinnartider["total"] = tid
    return vinnartider


def saver(driversData):
    with open("new_elo.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(driversData, ensure_ascii=False, indent=2))


def main():
    driversData = {"driver": {}, "codriver": {}}
    eloRanking = {}
    sorted_csv_files = find_files()
    rallys = turn_into_data(sorted_csv_files)
    for rally in rallys:
        print(rally["rallyName"])
        rally = placement_of_counter(rally)
        rally = dnf_checker(rally)
        driversData = check_driver_in_driversData(driversData, rally)
        winnerTime = finder_winner_per_class(rally["data"])
        elo_uppdater(driversData, winnerTime, rally)
        continue
    saver(driversData)


main()
