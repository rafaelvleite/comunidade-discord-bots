import json
import os
from deep_translator import GoogleTranslator

# Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "chess_players_fixed.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "chess_players_fixed_ptbr.json")

# Load the chess players data
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    chess_players = json.load(file)

# Initialize the translator
translator = GoogleTranslator(source="en", target="pt")

# Translate bios
for player in chess_players:
    if "Short Bio" in player and player["Short Bio"] not in ["Biography not available", "", None]:
        print(f"Translating bio for {player['Name']}...")

        try:
            player["Short Bio"] = translator.translate(player["Short Bio"])
        except Exception as e:
            print(f"Error translating {player['Name']}: {e}")

# Save the translated JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(chess_players, file, indent=2, ensure_ascii=False)

print(f"✅ Translation complete! Saved as `{OUTPUT_FILE}`.")
