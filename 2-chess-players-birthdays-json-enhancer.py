import json
import requests
import time

# Load JSON data
with open("chess_players_birthdays.json", "r") as file:
    chess_players = json.load(file)

# Function to get Wikipedia page, image, and bio separately
def get_wikipedia_info(player_name):
    formatted_name = player_name.replace(" ", "_")  # Ensure Wikipedia correctly formats spaces
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

# Enhance JSON with Wikipedia data
for player in chess_players:
    print(f"Fetching data for {player['Name']}...")
    try:
        wiki_url, image_url, bio = get_wikipedia_info(player['Name'])
        print(f"  Wikipedia URL: {wiki_url}")
        print(f"  Image URL: {image_url}")
        print(f"  Bio: {bio}")

        # Only update if values are found (prevent overwriting with None)
        if wiki_url:
            player["Wikipedia URL"] = wiki_url
        if image_url:
            player["Image URL"] = image_url
        if bio:
            player["Short Bio"] = bio

        time.sleep(1)  # Prevent rate limiting
    except Exception as e:
        print(f"Error fetching data for {player['Name']}: {e}")

# Save enhanced JSON
with open("chess_players_enhanced.json", "w") as file:
    json.dump(chess_players, file, indent=2)

print("Enhanced JSON saved as 'chess_players_enhanced.json'")
