from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Setup Chrome driver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

# Open the token transaction URL
url = "https://birdeye.so/find-trades?tokenAddress=7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr&chain=solana"
driver.get(url)

all_data = []
headers = []

after_time = '04/23/2025 22:15'
before_time = '04/24/2025 22:20'

try:

    time.sleep(5)

    # hide popup
    close_button_class = "absolute right-6 top-6 cursor-pointer text-neutral-400"
    close_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.{close_button_class.replace(' ', '.')}")))
    close_button.click()
    print("close button clicked successfully")
    time.sleep(2)

    # filter button 
    first_button_class = "inline-flex items-center justify-center gap-1 whitespace-nowrap rounded border px-4 uppercase outline-none transition-colors"
    first_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.{first_button_class.replace(' ', '.')}")))
    first_button.click()
    print("First button clicked successfully")
    time.sleep(2)

    parent_label_class = "group box-border flex cursor-pointer items-center gap-2 text-subtitle-regular-14 text-neutral-700"
    parent_label_class_elements = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"label.{parent_label_class.replace(' ', '.')}"))
    )

    found = False
    for el in parent_label_class_elements:
        span = el.find_element(By.TAG_NAME, "span")
        if span.text.strip() == "Buy & Sell":
            el.click()
            print("Buy & Sell selected")
            found = True
            break

    if not found:
        print("Buy & Sell option not found.")

    parent_div_time_picker_class = "react-datepicker__input-container"
    parent_div_time_picker_class_elements = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"div.{parent_div_time_picker_class.replace(' ', '.')}"))
    )

    # for i, el in enumerate(parent_div_time_picker_class_elements):
    #     input_element = el.find_element(By.TAG_NAME, "input")
    #     if i == 0:
    #         driver.execute_script("arguments[0].value = arguments[1];", input_element, after_time)
    #         print("Added after time")
    #     elif i == 1:
    #         driver.execute_script("arguments[0].value = arguments[1];", input_element, before_time)
    #         print("Added before time")

    for i, el in enumerate(parent_div_time_picker_class_elements):
        input_element = el.find_element(By.TAG_NAME, "input")
        time_value = after_time if i == 0 else before_time

        # Focus, set value, and trigger events
        driver.execute_script("""
            const input = arguments[0];
            const value = arguments[1];
            input.dispatchEvent(new Event('click', { bubbles: true }));
            input.value = value;
        """, input_element, time_value)

        print("Added", "after time" if i == 0 else "before time")

    time.sleep(3)

    apply_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Apply']"))
    )
    apply_button.click()

    print("Apply button clicked successfully")




    time.sleep(60)
        

    # # Step 1: Click the first button with the specified class
    # buy_sell_option = "inline-flex items-center justify-center gap-1 whitespace-nowrap rounded border px-4 uppercase outline-none transition-colors"
    # first_button = WebDriverWait(driver, 15).until(
    #     EC.element_to_be_clickable((By.CSS_SELECTOR, f"button.{first_button_class.replace(' ', '.')}")))
    # first_button.click()
    # print("First button clicked successfully")
    # time.sleep(2)

    # # Step 2: Click "Buy & Sell" option
    # buy_sell_option = WebDriverWait(driver, 15).until(
    #     EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'cursor-pointer')]//span[text()='Buy & Sell']")))
    # buy_sell_option.click()
    # print("Buy & Sell selected")
    # time.sleep(2)

    # # Step 3: Set date range (using direct input value setting)
    # date_inputs = WebDriverWait(driver, 15).until(
    #     EC.presence_of_all_elements_located((By.XPATH, "//input[contains(@class, 'border-input') and contains(@class, 'h-10')]")))
    
    # # Set start date (first input)
    # driver.execute_script("arguments[0].value = '04/18/2025 00:00';", date_inputs[0])
    # # Set end date (second input)
    # driver.execute_script("arguments[0].value = '04/24/2025 23:59';", date_inputs[1])
    # print("Date range set")
    # time.sleep(1)

    # # Step 4: Click Apply button
    # apply_button = WebDriverWait(driver, 15).until(
    #     EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'bg-primary') and contains(text(), 'Apply')]")))
    # apply_button.click()
    # print("Filters applied")
    # time.sleep(3)

    # # Get table data
    # print("Extracting table data...")
    
    # # Get headers
    # header_row = WebDriverWait(driver, 15).until(
    #     EC.presence_of_element_located((By.XPATH, "//thead[contains(@class, 'bg-neutral-100')]/tr")))
    # headers = [th.text for th in header_row.find_elements(By.TAG_NAME, "th")]
    
    # # Pagination loop
    # page_num = 1
    # while True:
    #     print(f"Processing page {page_num}")
        
    #     # Get current page data
    #     rows = WebDriverWait(driver, 15).until(
    #         EC.presence_of_all_elements_located((By.XPATH, "//tbody/tr")))
        
    #     for row in rows:
    #         cells = row.find_elements(By.TAG_NAME, "td")
    #         row_data = [cell.text for cell in cells]
    #         all_data.append(row_data)
        
    #     # Try to click next page (second instance of pagination button)
    #     next_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'border-neutral-200') and contains(@class, 'h-10')]")
    #     if len(next_buttons) >= 2:
    #         next_button = next_buttons[1]
    #         if "disabled" in next_button.get_attribute("class"):
    #             print("Reached last page")
    #             break
    #         next_button.click()
    #         page_num += 1
    #         time.sleep(3)
    #     else:
    #         print("No more pages")
    #         break

except Exception as e:
    print(f"Error during scraping: {str(e)}")

finally:
    # Save data
    if headers and all_data:
        df = pd.DataFrame(all_data, columns=headers)
        df.to_csv("transaction_data.csv", index=False)
        print(f"Successfully saved {len(all_data)} records to transaction_data.csv")
    else:
        print("No data was collected")
    
    driver.quit()