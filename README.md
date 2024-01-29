# wiki-gdp
# Last Checkpoint: 7AM BRT 9 Jan - Notes for the whole slice [:60]

    # [Corrected and Resolved]:
        # Switzerland had US$ nominal instead of US$nominal UPDATE: corrected by including variation in the code
        # France: had hierarchized headers, corrected.
        # Finland: only had EUR values instead of Bil US$ #Not solved for PPP (solved only for Nominal GDP yet, PPP to be added)
        # Phillipines: years are shown as th instead of td, years had special characters in it
        # Pakistan: years are show as th instead of td
            # Adapted the code to accept year as just the 4 first characters of the cell [Phillipines fix]
            # Adapted the code to accept year as being a th too, not just td [th year fix]
                # Created a rows cells table composed of any th cells if they are classified as such instead of as td.


    # [Partially Available]: Missing or incomplete data issues:
        # Russia only has values 1992-2021
        # Denmark: only has up to 2017
        # South Africa only has up to 2022
        # Vietnam: only has some  years
        # Czech Republic: only has 2015-2020
        # To be completed . . . 
        
    
    # [Solvable Missing Data]: issues regarding missing or incomplete data [50:70]

        
    # [Non-solvable]: fully missing data issues
        # Iraq: no tables at all in the page
        # Kuwait: no compatible table for IMF data
        # Slovakia: no compatible table for IMF data
        # Cuba: no tables at all in the page
        # Kenya: no compatible table for IMF data - data only available for each 5 years (2010, 2015, 2020...)
        # Oman: no compatible table for IMF data - data only available for each 5 years (2010, 2015, 2020...)

    # List of Countries:
        # https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)
        # https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(PPP) (alternative - non-optimal - full of non-country items such as territories, continents, etc).





UPDATE 29/Jan:

Project is finished!
- Would take too much time to document each limitation of each one of the countries, so I developed tools in the code to detect how many countries didn't have a proper GDP table and to retrieve the data from the ones that had, even if they don't have some years.
- Countries that didn't have information beyond 2017 (e.g.), 2018> values will appear as NaN.
- Interactive way to show the tables
- Developed in a Jupyter Notebook. To be tested in VS or PyCharm, however, should work perfectly in Jupyter.
- Launches profile from MLX and performs the activities, generating the outputs and display options after manual gathering.
- No use of automatic HTML scraping.



        # Additional data (US$Nom): https://en.wikipedia.org/wiki/List_of_countries_by_past_and_projected_GDP_(nominal)
        # Additional data (US$PPP): https://en.wikipedia.org/wiki/List_of_countries_by_past_and_projected_GDP_(PPP)

        # Additional data (IMF original source - checker): https://www.imf.org/en/Publications/WEO/Issues/2023/10/10/world-economic-outlook-october-2023#data-tools
