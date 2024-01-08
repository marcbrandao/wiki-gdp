from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

# Set up Selenium WebDriver
driver = webdriver.Chrome()

# Navigate to the main Wiki page
main_url = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)'
driver.get(main_url)

# Wait for the page to load
time.sleep(1)

# Finding the links to each country's page
country_links = driver.find_elements(By.CSS_SELECTOR, '.wikitable > tbody > tr > td:first-child > a')
country_urls = [(link.text, link.get_attribute('href')) for link in country_links if link.text not in ['European Union', 'ASEAN', 'Turkic States']]
# Initialize a DataFrame to store the combined data
combined_gdp_data = {}





# Iterate over each country's URL
for country_name, url in country_urls:
    # Navigate to the country's page
    driver.get(url)
    # Wait for page to load table
    time.sleep(1)
    
    try:
        # Find all tables on the page
        tables = driver.find_elements(By.CLASS_NAME, 'wikitable')
        
        # Identify the correct table by checking headers for "GDP"
        for table in tables:
            header_cells = table.find_elements(By.TAG_NAME, 'th')
            
            # Check if any header cell contains 'US$nominal' or 'US$ nominal' but not 'per capita'
            if any(('US$nominal' in cell.text or 'US$ nominal' in cell.text) and 'per capita' not in cell.text for cell in header_cells):
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                # Find the index of the column that contains 'US$nominal' or 'US$ nominal'
                gdp_col_index = next((i for i, cell in enumerate(header_cells) 
                                      if ('US$nominal' in cell.text or 'US$ nominal' in cell.text) 
                                      and 'per capita' not in cell.text), None)
                
                if gdp_col_index is not None:
                    for row in rows[1:]:  # Skip the header row
                        # Find elements with both 'td' and 'th' tags - some countries' years collumn is disposed as th 
                        td_cells = row.find_elements(By.TAG_NAME, 'td')
                        th_cells = row.find_elements(By.TAG_NAME, 'th')
                        cells = th_cells + td_cells  # Concatenate the lists
                        # Fallback for Year in 'th' if not found in 'td'
                        #year_cell = row.find_elements(By.TAG_NAME, 'th') if len(cells) < len(header_cells) else cells

                        if len(cells) > gdp_col_index:
                            year = cells[0].text[:4]  # Assuming the year is the first column, only grab first 4 chars
                            gdp = cells[(gdp_col_index)].text
                            if year not in combined_gdp_data:
                                combined_gdp_data[year] = {}
                            combined_gdp_data[year][country_name] = gdp
                    break

                    
                    
                    
    except Exception as e:
        print(f"Error processing {country_name}: {e}")

        
        
        
        
        
# Close the WebDriver
driver.quit()

# Transforming the data into a DataFrame
final_df = pd.DataFrame(combined_gdp_data) #Transpose if you wish (useful for checking countries)

# Get the current year to calculate -10
current_year = datetime.now().year

# Starting year for the count
start_year = current_year - 10

# Filter columns for the years selected
filtered_df = final_df.loc[:, str(start_year):str(current_year - 1)]

# Display the filtered GDP data
filtered_df