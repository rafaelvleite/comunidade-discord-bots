import json
import requests
import re
import time

# Load the enhanced JSON data
with open("chess_players_enhanced.json", "r") as file:
    chess_players = json.load(file)

# Function to clean up names (remove numbers & extra spaces)
def clean_name(name):
    return re.sub(r"^\d+", "", name).strip()  # Remove leading numbers and spaces

# Function to fetch Wikipedia info (URL, Image, Short Bio)
def get_wikipedia_info(player_name):
    formatted_name = player_name.replace(" ", "_")
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={formatted_name}&utf8=1"

    response = requests.get(search_url).json()

    if "query" in response and "search" in response["query"] and len(response["query"]["search"]) > 0:
        best_match = response["query"]["search"][0]["title"]
        page_url = f"https://en.wikipedia.org/wiki/{best_match.replace(' ', '_')}"

        # Step 1: Get Image
        image_url = None
        image_query_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&titles={best_match.replace(' ', '_')}&pithumbsize=500"
        image_response = requests.get(image_query_url).json()
        for page in image_response["query"]["pages"].values():
            if "thumbnail" in page:
                image_url = page["thumbnail"]["source"]

        # Step 2: Get Bio
        bio = "Biography not available"
        bio_query_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&titles={best_match.replace(' ', '_')}&exintro=1&explaintext=1"
        bio_response = requests.get(bio_query_url).json()
        for page in bio_response["query"]["pages"].values():
            if "extract" in page:
                bio = page["extract"].split("\n")[0]  # Take only the first paragraph

        return page_url, image_url, bio
    return None, None, None

# Loop through all players & fix missing data
for player in chess_players:
    # Clean the player's name
    player["Name"] = clean_name(player["Name"])

    # Check for missing Wikipedia info
    missing_wiki = not player.get("Wikipedia URL") or player["Wikipedia URL"] in [None, ""]
    missing_image = not player.get("Image URL") or player["Image URL"] in [None, ""]
    missing_bio = not player.get("Short Bio") or player["Short Bio"] in ["", "Biography not available"]

    if missing_wiki or missing_image or missing_bio:
        print(f"Fetching missing data for {player['Name']}...")
        wiki_url, image_url, bio = get_wikipedia_info(player["Name"])

        # Update only missing values
        if missing_wiki and wiki_url:
            player["Wikipedia URL"] = wiki_url
        if missing_image and image_url:
            player["Image URL"] = image_url
        if missing_bio and bio:
            player["Short Bio"] = bio

        time.sleep(1)  # Prevent rate limiting

# Save the fixed JSON
with open("chess_players_fixed.json", "w") as file:
    json.dump(chess_players, file, indent=2)

print("Fixed JSON saved as 'chess_players_fixed.json'")
