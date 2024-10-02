from bs4 import BeautifulSoup
import csv
import requests
import pandas as pd
import os


def main():
    # Grab all rallys
    folder_path = "Filer_för_hemsidor/infiniteracing/"
    file_paths = rallyGraber(folder_path)

    # for loop and send to
    rally_extract(file_paths)


def rally_extract(file_paths):
    # Replace 'test2.csv' with the path to your actual CSV file
    # file_path = 'hold/2024-09-07 Ekrundan 2024.csv'
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'lxml')

            rallyName = file_path.split("/")[-1].split(" ", 1)[1].split(".")[0]
            rallyDate = file_path.split("/")[-1].split(" ", 1)[0]

            # Prep
            with open("Tävlingar/infiniteracing/" + rallyDate + " " + rallyName + '.csv', 'w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                header = ["total_place", "klass_place",
                          "number", "driverklass", "name", "klubb", "klass",  "driver", "time"]

                writer.writerow(header)

            # Loop through each car
            # Display the DataFrame to verify it was read correctly
            data = {}

            soup = soup.find('tbody')
            cars = soup.find_all('tr')
            klass = {}
            for car in cars:
                data = {}
                # print(car.prettify())
                info = car.find_all('td')
                for row in info:
                    print(row)
                förare = info[0]

                # Allmän info
                data["total_place"] = info[0].text.split(".")[0]
                data["klass_place"] = 0
                data["number"] = info[1].text
                data["klass"] = info[5].text
                data["driverklass"] = info[2].text.split("-")[0]
                data["time"] = info[9].text

                # Klass placering
                if data["klass"] in klass:
                    klass[data["klass"]] += 1
                else:
                    klass[data["klass"]] = 1
                data["klass_place"] = klass[data["klass"]]

                # Driver
                data["name"] = info[0].text
                data["klubb"] = info[0].text
                data["driver"] = "driver"
                construct_data(data, writer, rallyName, rallyDate)

                # Codriver
                data["name"] = info[1].text
                data["klubb"] = info[1].text
                data["driver"] = "codriver"
                construct_data(data, writer, rallyName, rallyDate)


def construct_data(data, writer, rallyName, rallyDate):
    if data["total_place"] == "":
        data["total_place"] = "brutit"
        data["klass_place"] = "brutit"

    if data["name"]:
        with open("Tävlingar/infiniteracing/" + rallyDate + " " + rallyName + '.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([data["total_place"], data["klass_place"], data["number"],
                            data["driverklass"], data["name"], data["klubb"], data["klass"], data["driver"], data["time"]])


def rallyGraber(folder_path):
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.html'):
                file_paths.append(os.path.join(root, file))
    return file_paths


main()
