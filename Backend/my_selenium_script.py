from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize the Chrome driver
driver = webdriver.Chrome()

# Open the website
driver.get("https://offcampushousing.usf.edu/housing")

# Wait for the page to load
time.sleep(5)  # Adjust the sleep time as necessary

# Locate the listings
try:
    listings = driver.find_elements(By.CSS_SELECTOR, "li.list-result-item")  # Selector for each listing item
    print(f"Found {len(listings)} listings on the page.")
except Exception as e:
    print(f"Error finding listings: {e}")
    driver.quit()
    exit()

# Loop through the listings and extract details
for index, listing in enumerate(listings):
    try:
        title_element = listing.find_element(By.CSS_SELECTOR, "h2.order-2.property-title a")  # Selector for the title link
        title = title_element.text if title_element else "N/A"
        
        price_element = listing.find_element(By.CSS_SELECTOR, "div.copy-section-container div div:first-child")  # Selector for the price
        price = price_element.text if price_element else "N/A"
        
        location_element = listing.find_element(By.CSS_SELECTOR, "address.copy-row.address-container")  # Selector for the location
        location = location_element.text if location_element else "N/A"
        
        # Print the details
        print(f"Listing {index + 1}:")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Location: {location}")
        print("------")
    except Exception as e:
        print(f"Error extracting data from listing {index + 1}: {e}")

# Close the browser
driver.quit()
