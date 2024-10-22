from selenium import webdriver
import time
from bs4 import BeautifulSoup
import csv
from .database import database_connect, database_exit, database_add, database_start, database_add_rally, database_check_if_rally_added


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = 'https://reallyrally.se/#/race'

MAX_RALLYS = 5


def sleep():
    time.sleep(5)


def main(max_rallys):
    driver = webdriver.Chrome()
    database_start()
    cursor, conn = database_connect()

    rallyList, rallyData, driver = rallysGraber(driver, max_rallys)

    for x in range(len(rallyList)):
        if rallyList[x] != False:
            checkURL(driver)
            driver, made_it = rallyMaker(driver, rallyList[x], x)
            if made_it == True:
                rallyDate, rallyName = rallyData[x].split(" ", 1)
                if database_check_if_rally_added(cursor, conn, rallyName, rallyDate) == False:
                    rallyCars(cursor, conn, driver, rallyData[x])

    driver.quit()
    database_exit(cursor, conn)


def checkURL(driver):
    while True:
        if driver.current_url == URL:
            break
        else:
            driver.back()


def rallysGraber(driver, max_rallys):
    driver.get(URL)
    sleep()

    rallyList = []
    rallyData = []
    x = 0
    tested_rallys = 0

    rallys = driver.find_element(By.CLASS_NAME, 'p-card-content')
    rallys_html = rallys.get_attribute('innerHTML')
    rallys = rallys.find_elements(By.XPATH, './div')
    # Parse the HTML with BeautifulSoup
    rallys_html = BeautifulSoup(rallys_html, 'html.parser')
    rallys_html = rallys_html.find_all("div")
    for rowNumber in range(len(rallys)):
        if x == max_rallys:
            break
        x += 1

        button = WebDriverWait(rallys[rowNumber], 10).until(
            EC.element_to_be_clickable(
                # Relative XPath to find button inside the row
                (By.XPATH, './/button[contains(@class, "p-button-primary")]')
            )
        )

        if tested_rallys < 2:
            try:
                # Try to locate the button within the current row by its label or class
                E_button = WebDriverWait(rallys[rowNumber], 1).until(
                    EC.element_to_be_clickable(
                        # Using XPath to locate the button by its text
                        (By.XPATH,
                         './/button[span[text()="Gå direkt till E-anmälan"]]')
                    )
                )

                # If the button is found, perform an action (e.g., click it)
                print("Competition hasn't yet been finished")
                rallyList, rallyData = dataCompresser(
                    rallyList, rallyData, button, False)

                # Do something after clicking the button
                # For example, navigate to another page, scrape data, etc.

            except Exception as e:
                tested_rallys += 1
                print(f"Button not found or other error: {e}")
                rallyList, rallyData = dataCompresser(
                    rallyList, rallyData, button, True)
        else:
            rallyList, rallyData = dataCompresser(
                rallyList, rallyData, button, True)

        # button.click()

    return rallyList, rallyData, driver


def rallyMaker(driver, button, rowNumber):
    made_it = True
    rallys = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'p-card-content'))
    )
    rallys = rallys.find_elements(By.XPATH, './div')
    button = WebDriverWait(rallys[rowNumber], 5).until(
        EC.element_to_be_clickable(
            # Relative XPath to find button inside the row
            (By.XPATH, './/button[contains(@class, "p-button-primary")]')
        )
    )
    button.click()

    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '(//*[@class="p-menubar-button"])[2]')
            ))
        element.click()
    except:
        made_it = False
        print("No menu bar")

    try:
        # Wait for the span with the text 'Totalplacering' to be visible
        span_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.XPATH,
                    '//span[@class="p-menuitem-text ng-star-inserted" and text()="Resultat"]')
            )
        )

        # Now find the parent button and click it
        parent_button = span_element.find_element(
            By.XPATH, './..')  # Navigate to the parent button
        parent_button.click()  # Click the button
        print("Clicked the 'Resultat' button.")
    except Exception as e:
        print("Testing different way...")
        try:
            element = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                        '(//*[@class="p-ripple p-element p-menuitem-link ng-star-inserted"])')
                ))
            element.click()
        except Exception as e:
            print("Testing different way...")
            try:
                element = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                            '(//*[@class="p-ripple p-element p-menuitem-link ng-star-inserted"])[2]')
                    ))
                element.click()
            except Exception as e:
                made_it = False
                print("No results button")

    try:
        # Wait for the span with the text 'Totalplacering' to be visible
        span_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.XPATH,
                    '//span[@class="p-button-label" and text()="Resultat sorterade på klassplacering"]')
            )
        )

        # Now find the parent button and click it
        parent_button = span_element.find_element(
            By.XPATH, './..')  # Navigate to the parent button
        parent_button.click()  # Click the button
        print("Clicked the 'Resultat sorterade på klassplacering' button.")
    except Exception as e:
        made_it = False
        print("No klass results")

    return driver, made_it


def rallyCars(cursor, conn, driver, rallyData):
    # Find scoreboard table
    for x in range(100):
        table = WebDriverWait(driver, 10).until(
            # Use the appropriate selector for the table
            EC.presence_of_element_located((By.XPATH, '//table'))
        )
        table_html = table.get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, 'html.parser')
        soup = soup.find_all('tr')

        # Check if the tbody is found and contains more than 5 <tr> elements
        if soup and len(soup) > 5:
            print("More than 5 rows found.")
            break
        elif x == 4:
            print(f"{x} tries have been made. Skipping...")
            return
        else:
            print(
                f"Current number of rows: {len(soup.find_all('tr')) if soup else 0}")
            print(f"{x} of 4 test have been made!")
            print("Sleeping...")
            sleep()  # Sleeping

    # Prep
    with open("Tävlingar/reallyrally/" + rallyData + '.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        header = ["total_place", "klass_place",
                  "number", "driverklass", "name", "klubb", "klass",  "driver", "time"]

        writer.writerow(header)

    # Loop through each car
    # Display the DataFrame to verify it was read correctly
    for row in soup:
        row = row.find_all('td')
        for x in range(len(row)):
            row[x] = row[x].text.strip()
        if len(row) == 1:
            klass = row[0]
        else:
            data = {}
            if row[0] == "93":
                print("alloha")

            if row[0] != "Snr":
                # Allmän info
                data["total_place"] = row[1]
                data["klass_place"] = row[2]
                data["number"] = row[0]
                data["klass"] = klass
                data["driverklass"] = row[3]
                data["time"] = row[9]
                data["time"] = data["time"].replace(".", ":")

                # Driver
                data["name"] = row[4].split("/")[0].strip()
                data["name"] = " ".join(data["name"].split())
                data["klubb"] = row[5].split("/")[0].strip()
                data["driver"] = "driver"
                construct_data(cursor, conn, data, writer, rallyData)

                # Codriver
                data["name"] = row[4].split("/")[1].strip()
                data["name"] = " ".join(data["name"].split())
                data["klubb"] = row[5].split("/")[1].strip()
                data["driver"] = "codriver"
                construct_data(cursor, conn, data, writer, rallyData)
    rallyDate, rallyName = rallyData.split(" ", 1)
    database_add_rally(cursor, conn, rallyName, rallyDate)


def construct_data(cursor, conn, data, writer, rallyData):
    if data["total_place"] == "" or data["time"].strip() == "":
        data["total_place"] = "brutit"
        data["klass_place"] = "brutit"
        data["time"] = ""

    rallyDate, rallyName = rallyData.split(" ", 1)
    if data["name"]:  # rallyName, rallyDate, driver, name, klubb, klass, driverKlass, time, startnummer, total_place, klass_place
        database_add(cursor, conn, rallyName, rallyDate, data["driver"], data["name"], data["klubb"], data["klass"],
                     data["driverklass"], data["time"], data["number"], data["total_place"], data["klass_place"])

    if data["name"]:
        with open("Tävlingar/reallyrally/" + rallyData + '.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([data["total_place"], data["klass_place"], data["number"],
                            data["driverklass"], data["name"], data["klubb"], data["klass"], data["driver"], data["time"]])


def dataCompresser(rallyList, rallyData, button, finished):
    rallyName = button.text
    parent_button = button.find_element(
        By.XPATH, './..')  # Navigate to the parent button
    parent_button = parent_button.find_element(
        By.XPATH, './..')  # Navigate to the parent button

    rallyDate = parent_button.text
    rallyDate = rallyDate.split("Tävlingsdatum: ")[-1]
    rallyData.append(rallyDate + " " + rallyName)
    print(rallyDate + " " + rallyName)
    # {"rallyName": rallyName, "rallyDate": rallyDate}

    if finished == False:
        button = False
    rallyList.append(button)

    return rallyList, rallyData


if __name__ == "__main__":
    main(MAX_RALLYS)
