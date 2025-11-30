from web_scaper.PanahonScraper import PanahonScraper

scraper = PanahonScraper()
scraper.start_scraping("Legazpi")
data = scraper.get_data()
print(data)