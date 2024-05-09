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

    # Date
    for a in soup.find_all('a', href=True):
        if a['href'] == rallyhref:
            date = a.parent.text.strip().split("•")[0].split(",")[0].split(".")
            date = date[2].strip() + "-" + date[1].strip() + \
                "-" + date[0].strip()
            fileName = date + " " + rallyName + ".csv"
            break

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
                    if "retirements" not in car.text.lower():
                        data = {}
                        car = car.find_all('td')
                        peopleURL = car[3].find('a')['href']

                        peopleGrabber(peopleURL, data, fileName,
                                      bruten, klassPlacement)
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
        data["name"] = data["name"][1] + " " + data["name"][0]
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
    removed = RALLYDICT.pop()
    path_to_dir = "Tävlingar/"
    file_path = path_to_dir + removed
    if os.path.exists(file_path):
        os.remove(file_path)
    print("Removed: " + file_path)
