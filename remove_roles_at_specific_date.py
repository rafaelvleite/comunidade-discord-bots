import discord
from discord.ext import commands
import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)  # Force reloading environment variables

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
ROLE_ID = int(os.getenv("DISCORD_ROLE_ID"))
REMOVAL_SCHEDULE_FILE = os.getenv("REMOVAL_SCHEDULE_FILE", "removal_schedule.json")

# Load user removal schedule from JSON file
def load_removal_schedule():
    try:
        with open(REMOVAL_SCHEDULE_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("[ERROR] Could not load removal schedule. Ensure the JSON file is formatted correctly.")
        return {}

removal_schedule = load_removal_schedule()

# Bot intents (make sure you enable them in the Discord developer portal)
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[LOG] Logged in as {bot.user}")

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"[ERROR] Could not find guild with ID {GUILD_ID}. Please check the guild ID.")
        await bot.close()
        return

    print(f"[LOG] Connected to guild: {guild.name} (ID: {GUILD_ID})")

    role = guild.get_role(ROLE_ID)
    if not role:
        print(f"[ERROR] Could not find role with ID {ROLE_ID}. Please check the role ID.")
        await bot.close()
        return

    print(f"[LOG] Role to be removed: {role.name} (ID: {ROLE_ID})")

    # Check the removal dates
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"[LOG] Today's date: {today}")

    # Iterate through the removal schedule
    for user_id, removal_date in removal_schedule.items():
        # Try to get the member
        member = guild.get_member(user_id)
        user_display_name = member.display_name if member else f"Unknown User ({user_id})"

        print(f"[LOG] Checking user: {user_display_name} with scheduled removal date: {removal_date}")

        if today >= removal_date:
            if not member:
                print(f"[WARNING] User {user_display_name} not found in the guild.")
                continue

            print(f"[LOG] Found member: {user_display_name}")

            if role in member.roles:
                await member.remove_roles(role)
                print(f"[SUCCESS] Removed role '{role.name}' from {user_display_name}.")
            else:
                print(f"[INFO] {user_display_name} does not have the role '{role.name}'. No action taken.")
        else:
            print(f"[INFO] No action for {user_display_name} today. Removal date not reached.")

    print("[LOG] Finished processing all users.")
    await bot.close()

bot.run(TOKEN)
