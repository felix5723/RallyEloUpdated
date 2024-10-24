from selenium import webdriver
import time
from bs4 import BeautifulSoup
import csv
import re
from .database import database_connect, database_exit, database_add, database_start, database_add_rally, database_check_if_rally_added
from .selenium import selenium_grab


By, WebDriverWait, EC, driver = selenium_grab()


MAX_RALLYS = 5


def sleep():
    time.sleep(5)


def main(max_rallys):
    driver = webdriver.Chrome()
    database_start()
    cursor, conn = database_connect()

    rallyList = rallysGraber(driver, max_rallys)

    for href in rallyList:
        driver = rallyMaker(driver, href)
        rallyCars(cursor, conn, driver)

    driver.quit()
    database_exit(cursor, conn)


def rallysGraber(driver, max_rallys):
    url = 'https://www.infiniteracing.se/results/'

    driver.get(url)
    sleep()

    rallys = driver.find_elements(By.CLASS_NAME, "list-group-item")

    rallyList = []
    x = 0
    for rally in rallys:
        if x == max_rallys:
            break
        x += 1
        print(rally)
        data = rally
        rallyName = data.get_attribute('text')
        print(rallyName)
        href = rally.get_attribute('href')
        print(href)
        rallyList.append(href)

    return rallyList


def rallyMaker(driver, href):
    url = href
    driver.get(url)
    # sleep()

    try:
        # Totallista
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="totalListCheckBox"]'))
        )
        element.click()
    except:
        print("No total leaderboard")

        # Fler inställningar
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//a[@href="#collapse1"]'))
    )
    element.click()

    # Förarklass
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="driverClassCheckbox"]'))
    )
    element.click()

    return driver


def rallyCars(cursor, conn, driver):
    # Find the rally name and date
    h2_element = driver.find_element(By.XPATH, '//h2[1]')
    h2_text = driver.execute_script(
        "return arguments[0].childNodes[0].nodeValue;", h2_element).strip()
    rallyName, rallyDate, happend = split_on_last_space(h2_text)
    if database_check_if_rally_added(cursor, conn, rallyName, rallyDate) == False:
        print(rallyName)

        if happend == False:
            print("Inställd tävling")
        else:
            # Find scoreboard table
            for x in range(100):
                table = WebDriverWait(driver, 10).until(
                    # Use the appropriate selector for the table
                    EC.presence_of_element_located(
                        (By.ID, 'totalRankingTable'))
                )
                # table = driver.find_element_by_id('totalRankingTable')
                table_html = table.get_attribute('outerHTML')
                soup = BeautifulSoup(table_html, 'html.parser')
                soup = soup.find('tbody', id='resultTableBody')

                # Check if the tbody is found and contains more than 5 <tr> elements
                if soup and len(soup.find_all('tr')) > 5:
                    print("More than 5 rows found.")
                    break
                elif x == 5:
                    print(f"{x} tries have been made. Skipping...")
                    return
                else:
                    print(
                        f"Current number of rows: {len(soup.find_all('tr')) if soup else 0}")
                    print(f"{x} of 5 test have been made!")
                    print("Sleeping...")
                    sleep()  # Sleeping

            # Prep
            # with open("Tävlingar/infiniteracing/" + rallyDate + " " + rallyName + '.csv', 'w', newline='', encoding="utf-8") as file:
            #    writer = csv.writer(file)
            #    header = ["total_place", "klass_place",
            #              "number", "driverklass", "name", "klubb", "klass",  "driver", "time"]

            #    writer.writerow(header)

            # Loop through each car
            # Display the DataFrame to verify it was read correctly
            data = {}

            print(len(soup))
            cars = soup.find_all('tr')
            klass = {}
            for car in cars:
                data = {}
                # print(car.prettify())
                info = car.find_all('td')
                # for row in info:
                #    print(row)
                förare = info[0]

                # Allmän info
                data["total_place"] = info[0].text.split(".")[0]
                data["klass_place"] = 0
                data["number"] = info[1].text
                data["klass"] = info[5].text
                data["driverklass"] = info[2].text.split("-")[0]
                if data["total_place"] == " ":
                    data["total_place"] = "brutit"
                    data["klass_place"] = "brutit"
                    data["time"] = 0
                else:
                    data["time"] = info[-3].text.replace(".", ",")

                    # Klass placering
                    if data["klass"] in klass:
                        klass[data["klass"]] += 1
                    else:
                        klass[data["klass"]] = 1
                    data["klass_place"] = klass[data["klass"]]

                names = info[3].get_text(separator="\n").strip().split('\n')
                # for x in range(0, len(names)):
                #    names[x] = names[x].strip()
                klubbs = info[4].get_text(separator="\n").strip().split('\n')

                # Driver
                data["name"] = names[0].strip()
                data["klubb"] = klubbs[0].strip()
                data["driver"] = "driver"
                construct_data(cursor, conn, data,
                               rallyName, rallyDate)

                # Codriver
                data["name"] = names[-1].strip().split("Anmälare")[0]
                if klubbs[-1].strip()[:8].lower() == "anmälare":
                    for x in range(len(klubbs)-2, 0, -1):
                        if len(klubbs[x].strip()) > 0:
                            data["klubb"] = klubbs[x].strip()
                            break
                else:
                    data["klubb"] = klubbs[-1].strip()
                data["driver"] = "codriver"
                construct_data(cursor, conn, data,
                               rallyName, rallyDate)
        database_add_rally(cursor, conn, rallyName, rallyDate)


def construct_data(cursor, conn, data, rallyName, rallyDate):
    if data["total_place"] == "":
        data["total_place"] = "brutit"
        data["klass_place"] = "brutit"

    if data["name"]:  # rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place
        database_add(cursor, conn, rallyName, rallyDate, data["driver"], data["name"], data["klubb"], data["klass"],
                     data["driverklass"], data["time"], data["number"], data["total_place"], data["klass_place"])

    # if data["name"]:
    #    with open("Tävlingar/infiniteracing/" + rallyDate + " " + rallyName + '.csv', 'a', newline='', encoding="utf-8") as file:
    #        writer = csv.writer(file)
    #        writer.writerow([data["total_place"], data["klass_place"], data["number"],
    #                        data["driverklass"], data["name"], data["klubb"], data["klass"], data["driver"], data["time"]])


def split_on_last_space(text):
    # Find the last occurrence of a space
    print(text[-4:len(text)])
    print(text[-4:len(text)].isnumeric())
    if text[-4:len(text)].isnumeric() == True:
        if text[-6:-8].isnumeric() == True:
            text = text.replace((text[-5:-2]), "-")
        else:
            text = text.replace((text[-5:-2]), " ")
    if text[-8:].lower() == "inställd":
        happend = False
        return None, None, happend
    else:
        happend = True
    text = text.replace(" -", "-")
    text = text.replace("/", "-")
    last_space_index = text.rfind(' ')

    # If there's no space in the string, return it as is
    if last_space_index == -1:
        return text, ""

    # Split the string into two parts
    before_last_space = text[:last_space_index]
    after_last_space = text[last_space_index + 1:]  # Skip the space
    after_last_space = after_last_space.split("-")
    if len(after_last_space) == 3:
        if len(after_last_space[1]) == 1:
            after_last_space[1] = "0" + after_last_space[1]
        if len(after_last_space[0]) == 1:
            after_last_space[0] = "0" + after_last_space[0]
        after_last_space = "20" + \
            after_last_space[-1] + "-" + after_last_space[-2] + \
            "-" + after_last_space[-3]
    else:
        after_last_space = "20" + \
            after_last_space[-1] + "-" + "01" + "-" + "01"

    return before_last_space, after_last_space, happend


if __name__ == "__main__":
    main(MAX_RALLYS)
