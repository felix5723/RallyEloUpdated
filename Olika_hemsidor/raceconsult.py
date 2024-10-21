import requests
import csv
from bs4 import BeautifulSoup
from .database import database_connect, database_exit, database_add, datebase_start, database_add_rally, database_check_if_rally_added

MAX_RALLYS = 4


def main(max_rallys):
    datebase_start()
    cursor, conn = database_connect()

    urls = grabRallys(max_rallys)

    # url = input("Klistra in länken till tävlingen: ")
    # url = "https://www.raceconsulting.com/rally/resultat/totalresultat.jsp?competition=1484"
    for url in urls:
        print(url)
        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')

        rallyInfo = soup.find('div', class_="resultathuvud")
        rallyInfo = rallyInfo.find_all('div')[4]
        rallyInfo = rallyInfo.find_all('div')
        rallyName = " ".join(rallyInfo[1].text.split())
        rallyName = rallyName.replace(":", "-").replace("/", "-")
        rallyDate = " ".join(rallyInfo[0].text.split())
        if database_check_if_rally_added(cursor, conn, rallyName, rallyDate) == False:
            print(rallyName)
            print(rallyDate)

            #with open("Tävlingar/raceconsult/" + rallyDate + " " + rallyName + '.csv', 'w', newline='', encoding="utf-8") as file:
            #    writer = csv.writer(file)
            #    header = ["total_place", "klass_place",
            #              "number", "driverklass", "name", "klubb", "klass",  "driver", "time"]

            #    writer.writerow(header)

            # print(soup.prettify())
            cars = soup.find_all('tbody')
            for car in cars:
                data = {}
                # print(car.prettify())
                info = car.find_all('tr')
                förare = info[0]

                # Allmän info
                data["total_place"] = info[0].find_all('td')[0].text
                data["klass_place"] = info[1].find_all('td')[0].text
                data["number"] = info[0].find_all('td')[1].text
                data["klass"] = info[0].find_all('td')[6].text
                data["driverklass"] = info[0].find_all('td')[2].text
                data["time"] = info[1].find_all('td')[-2].text

                # Driver
                data["name"] = info[0].find_all('td')[4].text
                data["klubb"] = info[0].find_all('td')[5].text
                data["driver"] = "driver"
                construct_data(cursor, conn, data,
                               rallyName, rallyDate)

                # Codriver
                data["name"] = info[1].find_all('td')[4].text
                data["klubb"] = info[1].find_all('td')[5].text
                data["driver"] = "codriver"
                construct_data(cursor, conn, data,
                               rallyName, rallyDate)
            database_add_rally(cursor, conn, rallyName, rallyDate)
    database_exit(cursor, conn)


def grabRallys(max_rallys):
    urls = []
    banned = ["221", "222", "392", "812",
              "1026", "1061", "1084", "1097", "1424"]

    made_rallys = 0
    for year in range(2025, 2004, -1):
        if made_rallys > max_rallys:
            break
        url = "https://www.raceconsulting.com/rally/resultat/index.jsp?year=" + \
            str(year)
        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')
        rallysInYear = soup.find('table').find_all('tr')
        for x in range(1, (len(rallysInYear)-1), 1):
            made_rallys += 1
            if made_rallys > max_rallys:
                break
            # for rally in rallysInYear:
            totalurl = "https://www.raceconsulting.com/rally/resultat/totalresultat.jsp?competition="
            rallysInYear[x] = rallysInYear[x].find_all('td')
            if rallysInYear[x]:
                number = rallysInYear[x][0].find(
                    'a')['href'].split("=")[-1]
                if number not in banned:
                    totalurl = totalurl + number
                    urls.append(totalurl)
                else:
                    print("BANNED")
                    print(number)

    return urls


def construct_data(cursor, conn, data, rallyName, rallyDate):
    if data["total_place"] == "":
        data["total_place"] = "brutit"
        data["klass_place"] = "brutit"

    if data["name"]:  # rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place
        database_add(cursor, conn, rallyName, rallyDate, data["driver"], data["name"], data["klubb"], data["klass"],
                     data["driverklass"], data["time"], data["number"], data["total_place"], data["klass_place"])

    #if data["name"]:
    #    with open("Tävlingar/raceconsult/" + rallyDate + " " + rallyName + '.csv', 'a', newline='', encoding="utf-8") as file:
    #        writer = csv.writer(file)
    #        writer.writerow([data["total_place"], data["klass_place"], data["number"],
    #                        data["driverklass"], data["name"], data["klubb"], data["klass"], data["driver"], data["time"]])


if __name__ == "__main__":
    main(MAX_RALLYS)
