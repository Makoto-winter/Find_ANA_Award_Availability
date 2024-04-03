import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
from PIL import Image

load_dotenv()

# Enter your variables
# You also want to enter Departure Date and Return Date variables in the middle of the entire code.
YOUR_LOGINID = os.getenv("YOUR_ANAID")
YOUR_LOGINPASS = os.getenv("YOUR_ANAPASS")
CITY_COMBINATION_LIST = [["TYO", "JFK"], ["TYO", "ORD"], ["TYO", "IAD"], ["TYO", "IAH"], ["TYO", "SEA"], ["TYO", "SFO"], ["TYO", "LAX"], ["TYO", "MEX"], ["TYO", "YVR"]]  # CITY_COMBINATION_LIST = [["TYO", "JFK"], ["TYO", "ORD"], ["TYO", "IAD"], ["TYO", "IAH"], ["TYO", "SEA"], ["TYO", "SFO"], ["TYO", "LAX"], ["TYO", "MEX"], ["TYO", "YVR"]]
SEAT_CLASS_LIST = ["Economy", "Premium Economy", "Business"]  # SEAT_CLASS_LIST = ["Economy", "Premium Economy", "Business"]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.ana.co.jp/en/jp/")

driver.find_element(By.LINK_TEXT, "Login").click()

driver.find_element(By.NAME, "member_no").send_keys(YOUR_LOGINID)
driver.find_element(By.NAME, "member_password").send_keys(YOUR_LOGINPASS)
driver.find_element(By.ID, "login").click()

driver.find_element(By.ID, "is_not_login_conf").click()
driver.find_element(By.ID, "continue-login").click()

# Once logged in, wait for 8 seconds for the website to be completely loaded.
time.sleep(8)

# Clicking Flights Awards link
# for some reason, click() does not work here. So I did execute_script("arguments[0].click();", btn)
flight_awards = driver.find_elements(By.TAG_NAME, 'button')
for btn in flight_awards:
    if btn.text == "Flight Awards":
        driver.execute_script("arguments[0].click();", btn)
        break

time.sleep(1)

for combo in CITY_COMBINATION_LIST:
    city1, city2 = combo[0], combo[1]  # Going through different city combinations
    for boarding_class in SEAT_CLASS_LIST:  # Going through different boarding class
        for i in range(2):  # Flipping city1 and city2
            driver.find_element(By.LINK_TEXT, "Flight Award Reservations").click()
            time.sleep(10)

            # switching to a new tab
            initial_window = driver.current_window_handle
            for w in driver.window_handles:
                if w != initial_window:
                    driver.switch_to.window(w)
                    break

            # From
            driver.find_element(By.ID, "departureAirportCode:field_pctext").clear()
            driver.find_element(By.ID, "departureAirportCode:field_pctext").send_keys(city1)
            time.sleep(3)
            # somtimes, like 1 in 10 times, the next line causes an error, saying "could not find the option".
            # Do not know why... There's 3 seconds of wait already, which should be enough time to appear options.
            # To, Departure Date, and Return Date also cause the same error.
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, f"suggest_{city1}"))).click()  # driver.find_element(By.ID, f"suggest_{city1}").click()
            time.sleep(1)
            # To
            driver.find_element(By.ID, "arrivalAirportCode:field_pctext").clear()
            driver.find_element(By.ID, "arrivalAirportCode:field_pctext").send_keys(city2)
            time.sleep(2)
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, f"suggest_{city2}"))).click()  # driver.find_element(By.ID, f"suggest_{city2}").click()
            time.sleep(1)
            # Departure Date
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "awardDepartureDate:field_pctext"))).click()  # driver.find_element(By.ID, "awardDepartureDate:field_pctext").click()
            time.sleep(2)
            for i in range(0):  # needed when you need to click "See the next 3 months" button.
                time.sleep(1)
                driver.find_element(By.LINK_TEXT, "Next 3 months").click()
            driver.find_element(By.CSS_SELECTOR,
                                "#calsec2 table tbody tr:nth-child(2) td:nth-child(1)").click()  # current month is #calsec0 => calsec0 to calsec11. tr is nth week of the month => nth-child(1) - (5). td is the day of the week => nth-child(1) - (7)
            # Return Date
            driver.find_element(By.ID,
                                "awardReturnDate:field_pctext").click()  # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "awardReturnDate:field_pctext"))).click()
            time.sleep(2)
            for i in range(0):  # searching availability until around 6 month ahead
                time.sleep(0.5)
                driver.find_element(By.LINK_TEXT, "Next 3 months").click()
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR, "#calsec2 table tbody tr:nth-child(2) td:nth-child(3)").click()  # for testing,,, driver.find_element(By.CSS_SELECTOR, "#calsec2 table tbody tr:nth-child(2) td:nth-child(2)").click()  # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#calsec1 table tbody tr:nth-child(2) td:nth-child(3)"))).click()   # originally, "#calsec6 table tbody tr:nth-child(4) td"

            # Boarding Class
            select = Select(driver.find_element(By.ID, "boardingClass"))
            select.select_by_visible_text(boarding_class)
            # Passenger number increase
            # driver.find_element(By.CLASS_NAME, "passengerPlus").click()

            # Hit Search
            driver.find_element(By.CSS_SELECTOR, ".btnFloat input").click()

            # continue moving to the next day while class is not "next disable"
            while driver.find_element(By.CLASS_NAME, "next").get_attribute("class") != "next disable":
                # Result
                pic_number = 0  # for screenshots

                driver.execute_script('window.scrollBy(0, 100)')  # scroll 100px down to see the "next" button to be clicked, and to see if there's a flight without "Waitlisted" sign.

                outbound_date = driver.find_element(By.CSS_SELECTOR, ".selectItineraryOutbound em").text
                # Going through every outbound flight on a day
                for itinerary in driver.find_elements(By.CSS_SELECTOR,
                                                      ".selectItineraryOutbound .itinModeAvailabilityResult"):
                    if "Waitlisted" not in itinerary.text:  # get all elements without "Waitlisted"
                        print(f"Available. from:{city1} To:{city2} on {outbound_date}. Class:{boarding_class}")
                        # # screenshot
                        # pic_number += 1
                        # driver.save_screenshot(f"from:{city1}_To_{city2}_on_{outbound_date}_Class:{BOARDING_CLASS}.png")
                print(f"Searched. from:{city1} To:{city2} on {outbound_date}. Class:{boarding_class}")

                try:
                    # if there is an error message: "There are no results that match your specified search criteria. Please change your criteria, and retry your search again."
                    # In that case, you can not click the next button because it's hidden.
                    # This often occurs when departure and return dates are the same.
                    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID,
                                                                                        "loadingAreaForAjax")))  # Before attempting to click on the element, wait for the overlay (<div id="loadingAreaForAjax">) to disappear
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next"))).click()
                except:
                    break  # when there's an error message, break from the while loop
                    driver.close()
                    # switching back to the original tab
                    for w in driver.window_handles:
                        if w == initial_window:
                            driver.switch_to.window(w)
                            break

            # switch city1 and city2
            temp = city2
            city2 = city1
            city1 = temp

            driver.close()
            # switching back to the original tab
            for w in driver.window_handles:
                if w == initial_window:
                    driver.switch_to.window(w)
                    break
