import requests
import csv
from bs4 import BeautifulSoup


def main():
    # url = input("Klistra in länken till tävlingen: ")
    url = "https://www.raceconsulting.com/rally/resultat/totalresultat.jsp?competition=1484"
    page = requests.get(url)

    soup = BeautifulSoup(page.text, 'html.parser')

    rallyInfo = soup.find('div', class_="resultathuvud")
    rallyInfo = rallyInfo.find_all('div')[4]
    rallyInfo = rallyInfo.find_all('div')
    rallyName = " ".join(rallyInfo[1].text.split())
    rallyDate = " ".join(rallyInfo[0].text.split())

    with open("raceconsult/" + rallyDate + " " + rallyName + '.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        header = ["total_place", "klass_place",
                  "number", "driverklass", "name", "klubb", "klass",  "driver"]

        writer.writerow(header)

    # print(soup.prettify())
    cars = soup.find_all('tbody')
    for car in cars:
        data = {}
        print(car.prettify())
        info = car.find_all('tr')
        förare = info[0]

        # Allmän info
        data["total_place"] = info[0].find_all('td')[0].text
        data["klass_place"] = info[1].find_all('td')[0].text
        data["number"] = info[0].find_all('td')[1].text
        data["klass"] = info[0].find_all('td')[6].text
        data["driverklass"] = info[0].find_all('td')[2].text

        # Driver
        data["name"] = info[0].find_all('td')[4].text
        data["klubb"] = info[0].find_all('td')[5].text
        data["driver"] = "driver"
        construct_data(data, writer, rallyName, rallyDate)

        # Codriver
        data["name"] = info[1].find_all('td')[4].text
        data["klubb"] = info[1].find_all('td')[5].text
        data["driver"] = "codriver"
        construct_data(data, writer, rallyName, rallyDate)


def construct_data(data, writer, rallyName, rallyDate):
    print(data)
    if data["total_place"] == "":
        data["total_place"] = "brutit"
        data["klass_place"] = "brutit"

    with open("raceconsult/" + rallyDate + " " + rallyName + '.csv', 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([data["total_place"], data["klass_place"], data["number"],
                         data["driverklass"], data["name"], data["klubb"], data["klass"], data["driver"]])
    print("Hello")


main()
