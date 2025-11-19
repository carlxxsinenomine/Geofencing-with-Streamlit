from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def click_notification_button():
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.panahon.gov.ph/")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )


        # Todo 2: Open Notification
        notification_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.notification-button"))
        )
        notification_button.click()
        print("Successfully clicked the notification button!")
        driver.save_screenshot("after_click.png")
        print("Screenshot saved as 'after_click.png'")

        # Todo 3: Show Rainfall on map
        show_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "showSelectedAlertBtn"))
        )

        show_button.click()
        search_place(driver=driver)

        print("Successfully clicked the Show Rainfall button!")
        driver.save_screenshot("after_click_rainfall.png")
        print("Screenshot saved as 'after_click_rainfall.png'")

        # Todo 4: Show Thunderstorm on map
        select_type(index=1,driver=driver)
        show_button.click()
        search_place(driver=driver)

        print("Successfully clicked the Show Thunderstorm button!")
        driver.save_screenshot("after_click_thunderstorm.png")
        print("Screenshot saved as 'after_click_thunderstorm.png'")
        # Todo 5: Show Flood Advisory
        select_type(index=2, driver=driver)
        show_button.click()
        search_place(driver=driver)

        print("Successfully clicked the Show Tropical Flood button!")
        driver.save_screenshot("after_click_flood.png")
        print("Screenshot saved as 'after_click_flood.png'")
        # Todo 6: Show Tropical Cyclone
        select_type(index=3, driver=driver)
        show_button.click()
        search_place(driver=driver)

        print("Successfully clicked the Show Tropical Cyclone button!")
        driver.save_screenshot("after_click_cyclone.png")
        print("Screenshot saved as 'after_click_cyclone.png'")



    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        driver.quit()

def search_place(location_name="Legaspi", driver=None):
    # Todo 1: Send Place key on Search
    search_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']"))
    )

    search_input.clear()
    search_input.send_keys(location_name)

    print(f"Typed '{location_name}' into search box")

    # Press Enter key
    search_input.send_keys(Keys.ENTER)

    time.sleep(3)

    driver.save_screenshot(f"search_results_{location_name}.png")
    print(f"Screenshot saved as 'search_results_{location_name}.png'")

    print(f"Current URL: {driver.current_url}")

def select_type(index=None, driver=None):
    select_element = driver.find_element(By.ID, "alertTypeSelect")

    dropdown = Select(select_element)


    print(dropdown.select_by_index(index=index))  # Selects "Thunderstorm" (index 1)

if __name__ == "__main__":
    click_notification_button()