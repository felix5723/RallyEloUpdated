from bs4 import BeautifulSoup
import csv
import requests
import pandas as pd
import os


def main():
    # Grab all rallys
    folder_path = "Filer_för_hemsidor/reallyrally/"
    file_paths = rallyGraber(folder_path)

    # for loop and send to
    rally_extract(file_paths)


def rally_extract(file_paths):
    # Replace 'test2.csv' with the path to your actual CSV file
    # file_path = 'hold/2024-09-07 Ekrundan 2024.csv'
    for file_path in file_paths:
        rallyName = file_path.split("/")[-1].split(" ", 1)[1].split(".")[0]
        rallyDate = file_path.split("/")[-1].split(" ", 1)[0]

        # Read the CSV data, skipping unnecessary rows
        custom_headers = ['klass', '2', '3', '4', '5',
                          '6', '7', '8', '9', '10', '11', '12', '13']

        # Read the CSV data and specify custom headers
        klasser = pd.read_csv(file_path, skiprows=[
            0], names=custom_headers, header=None)

        # Leta upp alla klasser
        # Create a condition to check if Snr equals the value and the rest are NaN
        condition = klasser.iloc[:, 1:].isna().all(axis=1)

        # Filter the DataFrame based on the condition
        filtered_rows = klasser[condition]

        # Display the filtered rows
        print(filtered_rows)

        # Add them togheter
        klasses = {}
        max = 0
        last_klass = None
        for index, row in filtered_rows.iterrows():
            if last_klass == None:
                last_klass = row["klass"]
            klasses[index] = row["klass"]
            if max < index:
                max = index

        for x in range(0, max, 1):
            if x in klasses:
                klass = klasses[x]
                break

        df = pd.read_csv(file_path, skiprows=[0, 1], na_filter=False)

        # Prep
        with open("Tävlingar/reallyrally/" + rallyDate + " " + rallyName + '.csv', 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            header = ["total_place", "klass_place",
                      "number", "driverklass", "name", "klubb", "klass",  "driver", "time"]

            writer.writerow(header)

        # Loop through each car
        # Display the DataFrame to verify it was read correctly
        print(df)
        for index, row in df.iterrows():
            data = {}

            if row["Snr"] in klasses.values():
                klass = row["Snr"]

            if row["Snr"] not in klasses.values() and row["Snr"] != "Snr":
                print(row)
                # Allmän info
                data["total_place"] = row["Tot.pl"]
                data["klass_place"] = row["Kl.pl"]
                data["number"] = row["Snr"]
                data["klass"] = klass
                data["driverklass"] = row["Fk"]
                data["time"] = row["Tot.tid"]

                klubb = row["Klubb"].split("/")
                if len(klubb) != 2:
                    klubb = [klubb[0], klubb[0]]

                # Driver
                data["name"] = row["Namn"].split("/")[0].strip()
                data["klubb"] = row["Klubb"].split("/")[0].strip()
                data["driver"] = "driver"
                construct_data(data, writer, rallyName, rallyDate)

                # Codriver
                data["name"] = row["Namn"].split("/")[1].strip()
                data["klubb"] = row["Klubb"].split("/")[1].strip()
                data["driver"] = "codriver"
                construct_data(data, writer, rallyName, rallyDate)


def construct_data(data, writer, rallyName, rallyDate):
    if data["total_place"] == "":
        data["total_place"] = "brutit"
        data["klass_place"] = "brutit"

    if data["name"]:
        with open("Tävlingar/reallyrally/" + rallyDate + " " + rallyName + '.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([data["total_place"], data["klass_place"], data["number"],
                            data["driverklass"], data["name"], data["klubb"], data["klass"], data["driver"], data["time"]])


def rallyGraber(folder_path):
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                file_paths.append(os.path.join(root, file))
    return file_paths


main()
