from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from scrape_gmgn import get_roi_winrate
import time
import mysql.connector
from mysql.connector import Error
import datetime
import random

# Setup MySQL database
def setup_database():
    """
    Setup MySQL database with wallet_data table
    """
    try:
        # Connect to MySQL server (adjust credentials as needed)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Change to your MySQL username
            password="password"   # Change to your MySQL password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS wallet_scraper")
            
            # Switch to the database
            cursor.execute("USE wallet_scraper")
            
            # Create wallet_data table with created_at and updated_at columns
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallet_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                wallet_address VARCHAR(255) UNIQUE,
                ROI FLOAT,
                Winrate FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """)
            
            print("Database setup successful")
            return connection, cursor
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None, None

if __name__ == "__main__":
    # Setup database at the start
    print("Setting up database...")
    connection, cursor = setup_database()
    
    if not connection or not cursor:
        print("Failed to set up database. Exiting.")
        exit(1)
    
    print("Database ready. Starting web scraping...")
    
    # Setup Chrome driver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized") # To open browser in real time
    options.add_argument("--headless")  # Run in background
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
            time.sleep(5)
            print("Manual filter applying time ended.")

            pages_ended = 0
            page_num = 3

            while page_num <= 3 :
                
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
                                "ROI": stats['roi'],  # Random ROI > 15
                                "Winrate": stats['winrate']  # Random Winrate > 40
                            })
                            print(f"Collected: {trader_address} |")
                    except Exception as e:
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

    token_address = 'C8AjmccYUd5gYf8nf5KKYgr3zDNJ6UDHVVi312a2pump'
    traders_info = collect_traders_from_birdeye(token_address)
    
    # Filter the collected data based on ROI and Winrate criteria
    filtered_data = []
    total_traders = len(traders_info)
    skipped_traders = 0
    
    for trader in traders_info:
        # Convert ROI and Winrate to float values for comparison
        try:
            # Clean and convert ROI (remove % and convert to float)
            if trader["ROI"] is not None:
                roi_str = str(trader["ROI"]).replace('%', '').strip()
                trader["ROI"] = float(roi_str) if roi_str else None
            
            # Clean and convert Winrate (remove % and convert to float)
            if trader["Winrate"] is not None:
                winrate_str = str(trader["Winrate"]).replace('%', '').strip()
                trader["Winrate"] = float(winrate_str) if winrate_str else None
        except (ValueError, TypeError) as e:
            print(f"Error converting values for trader {trader['Trader']}: {e}")
            trader["ROI"] = None
            trader["Winrate"] = None
        
        # Skip entries with negative ROI or None values
        if trader["ROI"] is None or trader["ROI"] < 0:
            print(f"Skipping trader {trader['Trader']} due to negative or None ROI: {trader['ROI']}")
            skipped_traders += 1
            continue
            
        # Only include entries where ROI >= 15 and Winrate >= 40
        if trader["ROI"] >= 15 and trader["Winrate"] is not None and trader["Winrate"] >= 40:
            filtered_data.append(trader)
        else:
            print(f"Skipping trader {trader['Trader']} due to ROI ({trader['ROI']}) < 15 or Winrate ({trader['Winrate']}) < 40")
            skipped_traders += 1
    
    print(f"Filtered data: {len(filtered_data)} out of {total_traders} traders ({skipped_traders} skipped)")

    if filtered_data:
        # Save to Excel
        # df = pd.DataFrame(filtered_data)
        # df.to_excel("traders_with_roi.xlsx", index=False)
        # print(f"Saved {len(filtered_data)} traders with ROI and Winrate to 'traders_with_roi.xlsx'.")
        
        # Save to MySQL database - connection is already established
        try:
            inserted = 0
            updated = 0
            
            # Insert or update data into MySQL
            for trader in filtered_data:
                # Check if wallet_address already exists
                cursor.execute(
                    "SELECT id FROM wallet_data WHERE wallet_address = %s",
                    (trader["Trader"],)
                )
                result = cursor.fetchone()
                
                if result:
                    # Update existing record
                    cursor.execute(
                        "UPDATE wallet_data SET ROI = %s, Winrate = %s WHERE wallet_address = %s",
                        (trader["ROI"], trader["Winrate"], trader["Trader"])
                    )
                    updated += 1
                else:
                    # Insert new record
                    cursor.execute(
                        "INSERT INTO wallet_data (wallet_address, ROI, Winrate) VALUES (%s, %s, %s)",
                        (trader["Trader"], trader["ROI"], trader["Winrate"])
                    )
                    inserted += 1
            
            # Commit changes
            connection.commit()
            print(f"Database operations completed: {inserted} new entries inserted, {updated} entries updated.")
        except Error as e:
            print(f"Error saving to MySQL: {e}")
    else:
        print("No trader data matched the filtering criteria.")

    # Close database connection and web driver
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")
    
    driver.quit()
