from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PanahonScraper:
    def __init__(self):
        self.__panahon_url = "https://www.panahon.gov.ph/"
        self.__chrome_options = Options()
        self.__driver = None
        self.__data = None


    def start_scraping(self):
        try:
            self.__chrome_options.add_argument("--headless=new")
            self.__chrome_options.add_argument("--window-size=1920,1080")
            self.__chrome_options.add_argument("--no-sandbox")
            self.__chrome_options.add_argument("--disable-dev-shm-usage")
            self.__chrome_options.add_argument("--disable-gpu")
            self.__chrome_options.add_argument("--disable-extensions")
            self.__chrome_options.add_argument("--disable-software-rasterizer")
            self.__chrome_options.add_argument("--disable-background-timer-throttling")
            self.__chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            self.__chrome_options.add_argument("--disable-renderer-backgrounding")
            self.__chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.__chrome_options.add_experimental_option('useAutomationExtension', False)

            self.__driver = webdriver.Chrome(options=self.__chrome_options)
            self.__driver.get(self.__panahon_url)

            WebDriverWait(self.__driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Todo 2: Open Notification
            notification_button = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.notification-button"))
            )
            notification_button.click()
            print("Successfully clicked the notification button!")
            self.__driver.save_screenshot("after_click.png")
            print("Screenshot saved as 'after_click.png'")

            # Todo 3: Show Rainfall on map
            show_button = WebDriverWait(self.__driver, 10).until(
                EC.element_to_be_clickable((By.ID, "showSelectedAlertBtn"))
            )
            names = ['Rainfall', 'Thunderstorm', 'Flood', 'Tropical']

            for i in range(5):
                self.__select_type(index=i)
                show_button.click()
                self.__search_place()

                print(f"Successfully clicked the Show {names[i]} button!")
                self.__driver.save_screenshot(f"after_click_{names[i]}.png")
                print(f"Screenshot saved as 'after_click_{names[i]}.png'")

                self.__data = {names[i]: self.__wait_and_extract_content()}

        except Exception as e:
            print(f"Error: {str(e)}")

        finally:
            self.__driver.quit()


    def get_data(self):
        return self.__data


    def __wait_and_extract_content(self, timeout=10):
        try:
            # Wait for popup to be visible
            popup = WebDriverWait(self.__driver, timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ol-popup-content"))
            )

            # Wait for content to be non-empty
            WebDriverWait(self.__driver, timeout).until(
                lambda driver: popup.text.strip() != ""
            )

            content = popup.text
            print("✅ Popup content loaded successfully:")
            print(content)

            return content

        except TimeoutException:
            print("❌ Popup content didn't load within timeout period")

    def __search_place(self, location_name="Masinloc"):
        # Todo 1: Send Place key on Search
        search_input = WebDriverWait(self.__driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Search'], input[type='search']"))
        )

        search_input.clear()
        search_input.send_keys(location_name)

        print(f"Typed '{location_name}' into search box")

        # Press Enter key
        search_input.send_keys(Keys.ENTER)

        time.sleep(3)

        self.__driver.save_screenshot(f"search_results_{location_name}.png")
        print(f"Screenshot saved as 'search_results_{location_name}.png'")

        print(f"Current URL: {self.__driver.current_url}")

    def __select_type(self, index=None):
        select_element = self.__driver.find_element(By.ID, "alertTypeSelect")

        dropdown = Select(select_element)
        print(dropdown.select_by_index(index=index))
