from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless")  # Run in background
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.get("https://gmgn.ai/sol/address/BxAankqopWeLY5bDf5RmXmmU7PXfB7WKmcRNKChSoBai")

# Find element with exact text
element = driver.find_element(By.XPATH, "//*[text()='7D Realized PnL']/following-sibling::div[1]")
print('element =>', element.text)