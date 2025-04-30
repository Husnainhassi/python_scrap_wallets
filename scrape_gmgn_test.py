from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time

options = Options()
options.add_argument("--headless")  # Run in background
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

url = "https://gmgn.ai/sol/address/BxAankqopWeLY5bDf5RmXmmU7PXfB7WKmcRNKChSoBai"
try:
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Wait for JavaScript to load
    time.sleep(5)  # Adjust as needed

    # Get the full rendered HTML
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    label_div = None

    for div in soup.find_all("div"):
        if div.get_text(strip=True) == '"7D Realized PnL"':
            label_div = div
            break

    print('label_div =>', label_div)

    # Find all divs and check their text content
    # realized_pnl_div = None
    # for div in soup.find_all('div'):
    #     if div.get_text(strip=True) == '"Realized PnL"':
    #         realized_pnl_div = div
    #         break

    # if realized_pnl_div:
    #     # pnl_value = realized_pnl_div.get_text(strip=True)
    #     print('Realized PnL =>')
    # else:
    #     print('Not found')
    #     pnl_value = "Not found"
except Exception as e:
    print(f"Error occurred: {str(e)}")

finally:
    if driver:
        print("Closing browser...")
        driver.quit()