from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

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

# Prepare the main content for listings
main_content = ""

# Loop through the listings and extract details
for index, listing in enumerate(listings):
    try:
        title_element = listing.find_element(By.CSS_SELECTOR, "h2.order-2.property-title a")  # Selector for the title link
        title = title_element.text if title_element else "N/A"
        
        price_element = listing.find_element(By.CSS_SELECTOR, "div.copy-section-container div div:first-child")  # Selector for the price
        price = price_element.text if price_element else "N/A"
        
        location_element = listing.find_element(By.CSS_SELECTOR, "address.copy-row.address-container")  # Selector for the location
        location = location_element.text if location_element else "N/A"
        
        # Placeholder for review stars (you can replace this with actual data if available)
        reviews = '<span class="star">★</span><span class="star">★</span><span class="star">★</span><span class="star">★</span><span class="star">☆</span>'

        # Append the details to the main content
        main_content += f"""
        <div class="listing">
            <div class="title">{title}</div>
            <div class="price">Price: {price}</div>
            <div class="location">Location: {location}</div>
            <div class="reviews">Reviews: {reviews}</div>
        </div>
        """
        print(f"Listing {index + 1}: Title: {title}, Price: {price}, Location: {location}")  # Debugging line
    except Exception as e:
        print(f"Error extracting data from listing {index + 1}: {e}")

# Close the browser
driver.quit()

# Print the main content to verify
print("Main content generated:")
print(main_content)

# HTML Template for listings page
listings_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Listings</title>
    <link rel="stylesheet" href="website.css">
</head>
<body>
    <header>
        Listings
    </header>
    <main>
        {main_content}
    </main>
</body>
</html>
"""

# Fill the HTML template with main content
listings_html_output = listings_html_template.format(main_content=main_content)

# Define the path for the listings HTML file
listings_file_path = os.path.join(os.getcwd(), "listings.html")

# Write the HTML content to a file
with open(listings_file_path, "w", encoding="utf-8") as file:
    file.write(listings_html_output)

print(f"Data has been written to {listings_file_path}")

