import requests
from bs4 import BeautifulSoup
import pandas as pd

### Step 1: Scraping Liquipedia ###

# Fetch Liquipedia data
liquipedia_url = 'https://liquipedia.net/chess/Birthday_list'
response = requests.get(liquipedia_url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', {'class': 'wikitable'})

liquipedia_players = []
for row in table.find_all('tr')[1:]:  # Skip the header row
    columns = row.find_all('td')
    if len(columns) >= 3:
        birth_year = columns[0].get_text(strip=True)
        birth_date = columns[1].get_text(strip=True)
        name = columns[2].get_text(strip=True)
        liquipedia_players.append({'Name': name, 'Birth Year': birth_year, 'Birth Date': birth_date})

# Convert Liquipedia data to DataFrame
df_liquipedia = pd.DataFrame(liquipedia_players)
df_liquipedia["Birth Year"] = pd.to_numeric(df_liquipedia["Birth Year"], errors='coerce')
df_liquipedia["Birth Date"] = pd.to_datetime(df_liquipedia["Birth Date"], format="%B %d", errors='coerce').dt.strftime("%m-%d")
df_liquipedia["Full Birth Date"] = pd.to_datetime(df_liquipedia["Birth Date"] + "-" + df_liquipedia["Birth Year"].astype(str), format="%m-%d-%Y", errors='coerce')


### Step 2: Scraping BornGlorious ###

base_url = "https://www.bornglorious.com/united_states/birthday/?pf=10873124&pd="
month_urls = [f"{base_url}{str(month).zfill(2)}" for month in range(1, 13)]

born_glorious_players = []

for url in month_urls:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate player name and birthday elements
    for row in soup.find_all('div', class_='panel-primary'):  
        name_tag = row.find('div', class_='panel-heading')  # Extracts Name
        name = name_tag.get_text(strip=True) if name_tag else "Unknown"

        # Extract Birth Date correctly
        try:
            date_span = row.find_all('span', style=True)[1]  # Finds the second <span> with style
            birth_date_raw = date_span.find('b').get_text(strip=True) if date_span else "Unknown"
        except:
            birth_date_raw = "Unknown"

        # Extract Year & Birth Date separately
        try:
            birth_date_obj = pd.to_datetime(birth_date_raw, format="%b %d, %Y", errors='coerce')
            birth_year = birth_date_obj.year if birth_date_obj else None
            birth_date = birth_date_obj.strftime("%m-%d") if birth_date_obj else None
        except:
            birth_year = None
            birth_date = None

        born_glorious_players.append({'Name': name, 'Birth Year': birth_year, 'Birth Date': birth_date, 'Full Birth Date': birth_date_obj})

# Convert to DataFrame
df_born_glorious = pd.DataFrame(born_glorious_players)

# Drop NaN values safely
df_born_glorious.dropna(subset=["Birth Date"], inplace=True)

# Convert Birth Year to integer format
df_born_glorious["Birth Year"] = df_born_glorious["Birth Year"].astype("Int64")  # Keeps NaNs clean
df_born_glorious["Full Birth Date"] = pd.to_datetime(df_born_glorious["Full Birth Date"], errors='coerce')

### Step 3: Merging DataFrames ###
df_combined = pd.concat([df_liquipedia, df_born_glorious], ignore_index=True)

### Step 4: Data Formatting and Cleaning ###
df_combined.drop_duplicates(subset=['Name', 'Birth Year', 'Birth Date'], inplace=True)
df_combined.dropna(subset=['Name'], inplace=True)
df_combined.reset_index(drop=True, inplace=True)
df_combined["Full Birth Date"] = df_combined["Full Birth Date"].dt.strftime("%Y-%m-%d")

# Display final DataFrame
print(df_combined)

# Final Step: Convert and Export to JSON
df_combined.to_json("chess_players_birthdays.json", orient="records", indent=2)
