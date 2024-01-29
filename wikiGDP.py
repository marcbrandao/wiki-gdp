from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chromium.options import ChromiumOptions
from datetime import datetime
from getpass import getpass
import pandas as pd
import requests
import hashlib
import time
import re


# Setting up Multilogin X API access
MLX_BASE = "https://api.multilogin.com"
MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/v1"
LOCALHOST = "http://127.0.0.1"
HEADERS = {
 'Accept': 'application/json',
 'Content-Type': 'application/json'
 }

#TODO: Insert your account information in both variables below.
USERNAME = input("Insert your MLX email: ")
PASSWORD = getpass("Insert your MLX password: ")

#TODO: Insert the Folder ID and the Profile ID below 
FOLDER_ID = input("Insert the desired folder ID: ")
PROFILE_ID = input("Insert the desired profile ID: ")


# Function to sign into the application and get the token
def signin() -> str:

    payload = {
        'email': USERNAME,
        'password': hashlib.md5(PASSWORD.encode()).hexdigest()
    }

    r = requests.post(f'{MLX_BASE}/user/signin', json=payload)

    if(r.status_code != 200):
        print(f'\nError during login: {r.text}\n')
        
    else:
        response = r.json()['data']
        token = response['token']

    return token



# Function to start the Webdriver through MLX profile (API Request)
def start_profile() -> webdriver:

    r = requests.get(f'{MLX_LAUNCHER}/profile/f/{FOLDER_ID}/p/{PROFILE_ID}/start?automation_type=selenium', headers=HEADERS)
    response = r.json()

    if(r.status_code != 200):
        print(f'\nError while starting profile: {r.text}\n')
    else:
        print(f'\nProfile {PROFILE_ID} started.\n')
    
    selenium_port = response.get('status').get('message')
    driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=ChromiumOptions())

    return driver
 
    
# Function to stop the profile when closing Driver
def stop_profile() -> None:
    r = requests.get(f'{MLX_LAUNCHER}/profile/stop/p/{PROFILE_ID}', headers=HEADERS)

    if(r.status_code != 200):
        print(f'\nError while stopping profile: {r.text}\n')
    else:
        print(f'\nProfile {PROFILE_ID} stopped.\n')


#Get the token
token = signin()
HEADERS.update({"Authorization": f'Bearer {token}'})



# Set up Selenium WebDriver through MLX Selenium Automation
driver = start_profile()

# Set up the URL with the country list
main_url = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)'

# Navigate to the URL
driver.get(main_url)

# Wait for page to load
time.sleep(1)

# Finding and creating a list with all countries hyperlinks: containing the URL and name of the country.
country_links = driver.find_elements(By.CSS_SELECTOR, '.wikitable > tbody > tr > td:first-child > a')

# Creating a list of country page links to iterate over. Specify the exact part of each link object that is the URL.
country_urls = [(link.text, link.get_attribute('href')) for link in country_links if link.text not in ['European Union', 
                                                                                                       'ASEAN', 
                                                                                                       'Turkic States',]] #Exclude non-country entries that might appear on original list
# Initialize a DataFrame to store the combined data from all countries
combined_gdp_data = {}

# List for appending the countries which GDP tables are absent (insufficient data).
absent_countries = []

# Iterate over each country's URL
for country_name, url in country_urls[:15]:
    # Navigate to the country's page
    driver.get(url)
    # Wait for page to load table
    time.sleep(1)
    # Checking if there will be any suitable table at all 
    table_found = False
    
    # Inside the country's page, try to find a valid table:
    try:
        # Find all tables on the page
        tables = driver.find_elements(By.CLASS_NAME, 'wikitable')
        
        # For each of the tables between those tables found, identify the headers using wiki element 'th'.
        for table in tables:
            header_cells = table.find_elements(By.TAG_NAME, 'th')

            # Check if any header cell contains 'US$PPP' or 'US$ PPP' but not 'per capita' or 'growth'. 
            if any(('GDP' in cell.text) and ('US$'        in cell.text  or
                                             'US$PPP'     in cell.text  or
                                             'US$nominal' in cell.text) for cell in header_cells):
               
                # If it detects a table has those text in the headers, it found the GDP table!
                table_found = True 
                
                #Find the rows by element ('tr' in Wikitables)
                rows = table.find_elements(By.TAG_NAME, 'tr')

                # Find the index number of the column that contains 'US$PPP' or 'US$ PPP'
                gdp_col_index = next((i for i, cell in enumerate(header_cells) if ('US$ PPP' in cell.text or 
                                                                                   'US$PPP'  in cell.text or 
                                                                                   'PPP'     in cell.text)
                                                                               and ('capita' not in cell.text or 
                                                                                    'growth' not in cell.text)
                                     ), None) # If it doesn't find a column like this, gdp_col_index = None
                
                # In case you find the index number:
                if gdp_col_index is not None:
                    
                    for row in rows[1:]:  # Skip the header row
                        # Find all elements with both 'td' and 'th' tags - some countries' years column are disposed as th 
                        td_cells = row.find_elements(By.TAG_NAME, 'td')
                        th_cells = row.find_elements(By.TAG_NAME, 'th')
                        cells = th_cells + td_cells  # Concatenate the lists
                    
                        if len(cells) > gdp_col_index: # In case there are more than the index column, the first column should be the year
                            year = cells[0].text[:4]  # Only grab first 4 characters on the Year collumn (skipping notes)
                            gdp_text = cells[gdp_col_index].text # Put row data in text mode
                            gdp_numeric = re.sub(r'[^\d.]', '', gdp_text)  # Remove non-numeric characters
                            
                            if gdp_numeric:
                                gdp = float(gdp_numeric)  # Convert to float
                            else:
                                gdp = None  # If no numeric value found

                            if year not in combined_gdp_data:
                                combined_gdp_data[year] = {}
                                
                            combined_gdp_data[year][country_name] = gdp
                    break
                    
        if not table_found:
            absent_countries.append(country_name)
                            
    except Exception as e:
        print(f'Error processing {country_name}: {e}')


# Close the WebDriver
stop_profile()
        
# Put the absent_countries list in Alphabetical order.
absent_list = sorted(absent_countries)

# Print the list showing which countries are absent.        
print(f'There are {len(absent_list)} countries without a GDP table: \n {absent_list} \n')        
        



### POST SCRAPING MANIPULATIONS ###

# Viewing option: only .1 decimal
pd.set_option('display.float_format', '{:.1f}'.format)
# Vieweing option: all collums and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 250)

# Transforming the gross GDP data into a DataFrame
final_df = pd.DataFrame(combined_gdp_data) #Transpose if you wish (useful for checking countries)



# Calculate the GDP growth percentage data based on the previous year
gdp_growth_df = final_df.pct_change(axis=1, fill_method=None) * 100


# Get the current year to calculate -10
current_year = datetime.now().year
start_year = current_year - 10


# Create a copy of the slice to avoid SettingWithCopyWarning
filtered_df = final_df.loc[:, str(start_year):str(current_year - 1)].copy()
filtered_growth_df = gdp_growth_df.loc[:, str(start_year):str(current_year - 1)].copy()


# Convert DataFrame values to numeric
for col in filtered_df.columns:
    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    
for col in filtered_growth_df.columns:
    filtered_growth_df[col] = pd.to_numeric(filtered_growth_df[col], errors='coerce')
    


print("Tables generated: filtered_df and filtered_growth_df objects available. \n")

# Get user input regarding which table they want to see
table_type = input('Select the table you would like to see\n 1. GDP volume \n 2. GDP Growth Rate \n \n')

# Create a function to display the filtered GDP data
def display_df(table_type):
    if table_type == "1":
        return filtered_df #testing, it was return before
    elif table_type == "2":
        return filtered_growth_df
    else:
        print(f'Wrong option!')

#Display the chosen table type
selected_df = display_df(table_type).sort_values(by=[str(int(current_year) - 1)], ascending=False)
display(selected_df)

while True:
    further_actions = input('\n Would you like to display one or more tables? (Y/N):  ')

    if further_actions == "N":
        print("Finishing application.")
        break
    elif further_actions != "Y":
        print("Wrong choice! Please enter 'Y' or 'N'.")
        continue

    table_type = input('Select the table you would like to see \n 1. GDP volume \n 2. GDP Growth Rate \n')
    selected_df = display_df(table_type).sort_values(by=[str(int(current_year) - 1)], ascending=False)
    display(selected_df)