from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from scrape_gmgn import get_roi_winrate
import time

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized") # To open browser in real time
# options.add_argument("--headless")  # Run in background
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=service, options=options)

def collect_traders_from_birdeye(token_address):

    """
    Collect trader wallet addresses from Birdeye.
    """

    # Open the token transaction URL
    birdeye_url = f"https://birdeye.so/find-trades?tokenAddress={token_address}&chain=solana"
    driver.get(birdeye_url)

    traders_data = []

    try:

        # wait for full page load
        time.sleep(3)

        # Close popup if appears
        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.absolute.right-6.top-6.cursor-pointer.text-neutral-400".replace(' ', '.')))
            )
            close_button.click()
            print("Closed the popup.")
        except:
            print("No popup appeared.")

        print("Waiting for manual filter...")
        # Wait for manual filter
        time.sleep(25)
        print("Manual filter applying time ended.")

        pages_ended = 0
        page_num = 1

        while pages_ended == 0:
            
            # Get table body rows
            rows = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tbody//tr"))
            )

            # extract traders address from links
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")

                try:
                    div = cells[5].find_element(By.TAG_NAME, "div")
                    a_tag = div.find_element(By.TAG_NAME, "a")
                    trader_link = a_tag.get_attribute("href")

                    if trader_link:
                        trader_address = trader_link.split("/profile/")[1].split("?")[0]
                        stats = get_roi_winrate(trader_address)
                        traders_data.append({
                            "Trader": trader_address,
                            "ROI": stats['roi'],
                            "Winrate": stats['winrate']
                        })
                        print(f"Collected: {trader_address} |")
                except:
                    print(f"Error processing row: {e}")
                    traders_data.append({
                        "Trader": "",
                        "ROI": None,
                        "Winrate": None
                    })

            print(f"Collected {len(traders_data)} trader address.")

            try:

                # Pagination
                pagination_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//div[contains(@class, 'flex') and contains(@class, 'items-center') and contains(@class, 'justify-center') and contains(@class, 'gap-3')]"
                    ))
                )

                # Then get all buttons inside the div
                buttons = pagination_div.find_elements(By.XPATH, ".//button")

                # Access next button
                next_button = buttons[1]

                # print(f"Next button: {next_button}")

                if next_button.get_attribute("disabled") is not None:
                    pages_ended = 1
                    print("Next button is disabled. Scraping finished.")
                    break
                else:
                    print('Clicking the next button...')
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    driver.execute_script("arguments[0].click();", next_button)
                    page_num += 1
                    time.sleep(5)
            except Exception as e:
                print(f"Pagination Error: {e}")
                break

    except Exception as e:
        print(f"Error: {e}")

    return traders_data

if __name__ == "__main__":
    token_address = '5SrwudGa1RHndbveXW1obMvH51Gh9amRRuMoPdqZpump'
    traders_info = collect_traders_from_birdeye(token_address)

    if traders_info:
        df = pd.DataFrame(traders_info)
        df.to_excel("traders_with_roi.xlsx", index=False)
        print(f"Saved {len(traders_info)} traders with ROI and Winrate to 'traders_with_roi.xlsx'.")
    else:
        print("No trader links were collected.")

    driver.quit()
