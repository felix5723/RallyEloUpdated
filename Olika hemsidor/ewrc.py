from bs4 import BeautifulSoup
import requests
import csv
import json
from os import listdir
import os

OVERHEADURL = "https://www.ewrc-results.com"
NATIONSURL = "/events/?nat=16"
STATSDICT = {}
RALLYDICT = []
YEAR = 2015


def main():
    rallysGrabber()


def rallysGrabber():
    soup = loadURL(NATIONSURL)

    orgs = soup.find_all('div', class_="events-list-item mt-2")
    for org in orgs:
        org = org.find_all('a')
        for rally in org:
            year = rally.text
            if year.isnumeric() == True:
                rallyURL = rally['href']
                print(rally)
                carGrabber(rallyURL, rallyhref, rallyName)
            else:
                rallyhref = rally['href']
                rallyName = rally.text.strip()
                rallyName = rallyName.replace(":", "-")


def carGrabber(rallyURL, rallyhref, rallyName):
    soup = loadURL(rallyURL)
    bruten = False
    klassPlacement = {}
    year = 0

    # Date
    for a in soup.find_all('a', href=True):
        if a['href'] == rallyhref:
            date = a.parent.text.strip().split("•")[0].split(",")[0].split(".")
            if len(date) == 3:
                year = date[2].strip()
                month = date[1].strip()
                day = date[0].strip()
            else:
                year = date[4].strip()
                month = date[3].strip()
                day = date[2].split("–")[-1].strip()

            date = year.strip() + "-" + month.strip() + "-" + day.strip()
            year = int(year)
            fileName = date + " " + rallyName + ".csv"
            break

    if year >= YEAR:
        path = "Tävlingar/"
        # grab rally from folder
        alreadyMade = find_csv_filenames(path)
        if fileName not in alreadyMade:
            RALLYDICT.append(fileName)
            with open("Tävlingar/" + fileName, 'w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                header = ["total_place", "klass_place",
                          "number", "driverklass", "unique code", "name", "klass",  "driver"]

                writer.writerow(header)

            cars = soup.find_all('table')
            if cars:
                cars = cars[0].find_all('tr')
                if len(cars) > 1:
                    for car in cars:
                        if "retirements" not in car.text.lower() and "not in overall results, but not retired" not in car.text.strip().lower():
                            data = {}
                            car = car.find_all('td')
                            peopleURL = car[3].find('a')['href']

                            peopleGrabber(peopleURL, data, fileName,
                                          bruten, klassPlacement)
                        elif "not in overall results, but not retired" in car.text.strip().lower():
                            break
                        else:
                            bruten = True
                    bruten = False


def peopleGrabber(peopleURL, data, fileName, bruten, klassPlacement):
    soup = loadURL(peopleURL)

    driver = soup.find_all(
        'div', class_="driver p-1")[0].find_all('div')[0].find_all('a')
    codriver = soup.find_all('div', class_="codriver p-1")
    if codriver:
        codriver = codriver[0].find_all('div')[0].find_all('a')
    else:
        codriver = "ingen"
    car = soup.find('div', class_="car p-1").find_all('div')
    results = soup.find_all('div', class_="results p-1")[0].find_all('div')

    data["startnumber"] = car[0].text.strip()
    data["car"] = car[1].text.strip().split("  ")[0].strip()
    data["team"] = car[2].text.strip()
    data["klass"] = car[3].text.strip()

    if bruten == False:
        data["total_placement"] = results[1].text.strip().split(".")[0]

        if data["klass"] not in klassPlacement:
            klassPlacement[data["klass"]] = 1
        else:
            klassPlacement[data["klass"]] += 1
        data["klass_placement"] = klassPlacement[data["klass"]]
    else:
        data["total_placement"] = "brutit"
        data["klass_placement"] = "brutit"

    data["name"] = driver[0].text.strip().split(" ")
    data["name"] = data["name"][1] + " " + data["name"][0]
    data["driver"] = "driver"
    data["unique code"] = driver[0]['href'].strip().split("-")[0].split("/")[-1]
    peopleSaver(data, fileName)

    if codriver != "ingen":
        data["name"] = codriver[0].text.strip().split(" ")
        if len(data["name"]) == 2:
            data["name"] = data["name"][1] + " " + data["name"][0]
        else:
            data["name"] = data["name"][0]
        data["driver"] = "codriver"
        data["unique code"] = codriver[0]['href'].strip().split(
            "-")[0].split("/")[-1]
        peopleSaver(data, fileName)


def peopleSaver(data, fileName):
    with open("Tävlingar/" + fileName, 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([data["total_placement"], data["klass_placement"], data["startnumber"],
                         data["klass"], data["unique code"], data["name"], data["klass"], data["driver"]])


def loadURL(url):
    path_to_dir = "Tävlingar data/"
    alreadyMade = find_html_filenames(path_to_dir)
    searchurl = url.replace("/", "-")[1:-1] + ".html"
    if searchurl not in alreadyMade:
        newurl = OVERHEADURL + url
        page = requests.get(newurl)
        soup = BeautifulSoup(page.text, 'html.parser')

        if url != NATIONSURL:
            with open(path_to_dir + searchurl, "w") as f:
                f.write(str(soup))

    else:
        soup = BeautifulSoup(
            open(path_to_dir + searchurl), "html.parser")
    return soup


def find_html_filenames(path_to_dir, suffix=".html"):
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


try:
    main()
# except Exception as error:
#    print(error)
except KeyboardInterrupt:
    if len(RALLYDICT) > 0:
        removed = RALLYDICT.pop()
        path_to_dir = "Tävlingar/"
        file_path = path_to_dir + removed
        if os.path.exists(file_path):
            os.remove(file_path)
        print("Removed: " + file_path)
