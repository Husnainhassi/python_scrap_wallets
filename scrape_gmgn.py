from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--headless")  # Run in background
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def get_roi_winrate(wallet_address):
    
    """
    Given a wallet address, open tab, get ROI and Winrate from gmgn.ai, then close tab.
    """
    try:
        url = f"https://gmgn.ai/sol/address/{wallet_address}"
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        # Wait for JavaScript to load
        time.sleep(5)  # Adjust as needed

        # Get the full rendered HTML
        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        winrate_div = soup.find(class_="css-1vihibg")
        winrate_text = winrate_div.get_text(strip=True)
        winrate_value = winrate_text.replace("%", "")
        print('winrate =>', winrate_value)

        time.sleep(2)

        roi_div = soup.find(class_="css-1y0msoc")
        roi_text = roi_div.get_text(strip=True)
        roi_value = roi_text.split("%")[0]
        print('roi =>', roi_value)

        return {"roi": roi_value, "winrate": winrate_value}

    except Exception as e:
        print(f"Error scraping {wallet_address}: {str(e)}")
        return None

    finally:
        if driver:
            driver.quit()