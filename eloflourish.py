import json
import time
from os import listdir
import csv
import json
import os
import glob
import re


def main():
    data = loadData()
    dates = getDates()
    print(f'There have so far been {len(dates)} rallys driven')
    # Find top 10 at each given date
    leaderboard = {"driver": {}, "codriver": {},
                   "top10": {"driver": {}, "codriver": {}}}
    x = 0
    for date in dates:
        x += 1
        if x == 1000:
            break
        finder(leaderboard, data, date)

    yearleaderboard = leaderboard
    leaderboard = cleaner(leaderboard)
    makecsv(leaderboard)

    leaderboard = yearleaderboard
    leaderboard = yearcleaner(leaderboard)
    yearmakecsv(leaderboard)


def loadData():
    with open('elo.json', encoding='utf-8') as fh:
        data = json.load(fh)
    return data


def find_csv_files(folder_path):
    # Using glob to find all .csv files in the folder and subfolders
    return glob.glob(os.path.join(folder_path, '**', '*.csv'), recursive=True)


def keep_date_format(text):
    # Pattern to match the nnnn-nn-nn format
    pattern = r'\b\d{4}-\d{2}-\d{2}\b'

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)

    # Join the matches with a space or any separator you prefer
    result = ' '.join(matches)

    return result


def getDates():
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
    dates = sorted(
        combined_csv_files, key=lambda x: os.path.basename(x))
    # grab rally from folder
    # rallys = find_csv_filenames(sorted_csv_files)

    for x in range(len(dates)):
        dates[x] = keep_date_format(dates[x])

    return dates


def sorter(my_dict):
    my_dict = dict(
        sorted(my_dict.items(), key=lambda item: item[1], reverse=True))
    return my_dict


def top10EloGrabber(my_dict):
    my_dict = sorter(my_dict)
    dict_items = list(my_dict.items())
    # Access the item at index 10 (remember Python uses 0-based indexing, so index 10 is the 11th item)
    if len(dict_items) > 10:
        key, value = dict_items[9]
        top10_elo = value
        # print(f"Key: {key}, Value: {value}")
    else:
        # print("The dictionary does not have an index 9.")
        top10_elo = min(my_dict.values())
    return my_dict, top10_elo


def remover(my_dict, leaderboard, seat):
    for x in range(len(my_dict)-1, 10, -1):
        dict_items = list(my_dict.items())
        key, value = dict_items[x]
        # print(x)
        # print(key)
        # print(key not in leaderboard["top10"][seat])
        if key not in leaderboard["top10"][seat]:
            del my_dict[key]
            break
        elif key in leaderboard["top10"][seat]:
            my_dict[key] = 0
    return my_dict


def finder(leaderboard, data, date):
    for seat in ["driver", "codriver"]:
        top10_elo = 0
        if date not in leaderboard[seat]:
            leaderboard[seat][date] = {}
        my_dict = leaderboard[seat][date]
        for name in data[seat].keys():
            try:
                newElo = data[seat][name]["history"][date]["elo after rally"]['total']
            except:
                newElo = 0

            if newElo > top10_elo or len(my_dict) < 10 and newElo != 0:
                my_dict[name] = newElo
                # Ta bort ifall det är mer än 10 personer och den lägsta av dem inte finns med i leaderboarden
                if len(my_dict) > 10:
                    my_dict = sorter(my_dict)
                    my_dict = remover(my_dict, leaderboard, seat)
                    my_dict, top10_elo = top10EloGrabber(my_dict)

            if name in leaderboard["top10"][seat] and name not in my_dict:
                my_dict[name] = leaderboard["top10"][seat][name]
                my_dict = sorter(my_dict)
                my_dict = remover(my_dict, leaderboard, seat)
                my_dict, top10_elo = top10EloGrabber(my_dict)

        for name in my_dict.keys():
            # Updated for leaderboard during given date
            leaderboard[seat][date][name] = my_dict[name]

            # Updated for top10 leaderboard
            if name not in leaderboard["top10"][seat]:
                # print(my_dict[name])
                leaderboard["top10"][seat][name] = my_dict[name]
            elif name in leaderboard["top10"][seat]:
                if name not in my_dict:
                    # print(leaderboard["top10"][seat][name])
                    my_dict[name] = "None"
                else:
                    my_dict[name] = leaderboard[seat][date][name]
                leaderboard["top10"][seat][name] = my_dict[name]

    return leaderboard


def cleaner(leaderboard):
    hold = leaderboard
    leaderboard = {"driver": {}, "codriver": {}}
    for seat in ["driver", "codriver"]:
        for date in hold[seat].keys():
            for name in hold["top10"][seat]:
                if name not in leaderboard[seat]:
                    leaderboard[seat][name] = {}
                if name in hold[seat][date]:
                    elo = hold[seat][date][name]
                else:
                    elo = 0
                if elo == 0:
                    elo = ""
                leaderboard[seat][name][date] = elo

    return leaderboard


def makecsv(leaderboard):
    leaderboard = leaderboard["driver"]
    with open('driverelo.csv', mode='w', newline='', encoding="utf-8") as file:
        file.close
    with open('driverelo.csv', mode='a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        # Step 1: Write the header row (dates as headers)
        # Extract the dates (keys) from the inner dictionary and add "Name" at the start
        headers = ['Name'] + list(leaderboard['Mikael Gustafsson'].keys())
        writer.writerow(headers)

        # Step 2: Write the data row (name and Elo values)
        for name, dates in leaderboard.items():
            # Create a row with the name followed by the values (Elo ratings)
            row = [name] + list(dates.values())
            writer.writerow(row)


def yearcleaner(leaderboard):
    hold = leaderboard

    # Initialize an empty dictionary to store one key from each year
    latest_per_year = {}
    latest_per_year_list = []

    # Iterate over the dictionary
    for date_key, value in hold["driver"].items():
        year = date_key[:4]

        # If the year is not already in the result, add this key-value pair
        if year not in latest_per_year or date_key > latest_per_year[year][0]:
            latest_per_year[year] = date_key
    for date in latest_per_year:
        latest_per_year_list.append(latest_per_year[date])

    leaderboard = {"driver": {}, "codriver": {}}
    for seat in ["driver", "codriver"]:
        for date in hold[seat].keys():
            if date in latest_per_year_list:
                for name in hold["top10"][seat]:
                    if name not in leaderboard[seat]:
                        leaderboard[seat][name] = {}
                    if name in hold[seat][date]:
                        elo = hold[seat][date][name]
                    else:
                        elo = 0
                    if elo == 0:
                        elo = ""
                    leaderboard[seat][name][date] = elo

    return leaderboard


def yearmakecsv(leaderboard):
    leaderboard = leaderboard["driver"]
    with open('driverelo_year.csv', mode='w', newline='', encoding="utf-8") as file:
        file.close
    with open('driverelo_year.csv', mode='a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        # Step 1: Write the header row (dates as headers)
        # Extract the dates (keys) from the inner dictionary and add "Name" at the start
        headers = ['Name'] + list(leaderboard['Mikael Gustafsson'].keys())
        writer.writerow(headers)

        # Step 2: Write the data row (name and Elo values)
        for name, dates in leaderboard.items():
            # Create a row with the name followed by the values (Elo ratings)
            row = [name] + list(dates.values())
            writer.writerow(row)


main()
