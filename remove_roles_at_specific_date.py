import discord
from discord.ext import commands
import datetime
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # Force reloading environment variables

TOKEN = os.getenv("DISCORD_TOKEN")

# List of users to check with their removal dates
removal_schedule = {
    318467529645359104: "2026-02-05",  # Gosder
    505589838964064275: "2026-02-05",  # kelvader18
    1237888120784031835: "2026-02-05",  # João
    818189931695571046: "2026-02-05",  # Light 🦇
    803745674386341909: "2026-02-05",  # Lucaskb13
    1123787651531677786: "2026-02-05",  # Devorador do Nubank
    331793062416220160: "2026-02-05",  # heitorsp
    1317980616826032202: "2026-02-05",  # Osix
    848331633429577758: "2026-02-05",  # Zimmer
    759121743599763497: "2026-02-05",  # mdkmaycon
    184805940862648321: "2026-02-08",  # GuiTerrys...
    348627491365191681: "2026-02-08",  # 
    380130664894300182: "2026-02-08",  # 
    1336744461874626714: "2026-02-08",  # 
    513457225889480715: "2026-02-08",  # 
    250375299571646465: "2026-02-08",  # 
    1169805108004007998: "2026-02-08",  # 
    406623812864573471: "2026-02-08",  # 
    434786926604582922: "2026-02-08",  # 
    1336500443207176212: "2026-02-08",  # 
}

# Bot intents (make sure you enable them in the Discord developer portal)
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[LOG] Logged in as {bot.user}")

    # Guild (server) ID and Role ID to be removed
    guild_id = 1335436694844997734  # Replace with your server's ID
    role_id = 1336061135446605925  # Replace with the role you want to remove

    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"[ERROR] Could not find guild with ID {guild_id}. Please check the guild ID.")
        await bot.close()
        return

    print(f"[LOG] Connected to guild: {guild.name} (ID: {guild_id})")

    role = guild.get_role(role_id)
    if not role:
        print(f"[ERROR] Could not find role with ID {role_id}. Please check the role ID.")
        await bot.close()
        return

    print(f"[LOG] Role to be removed: {role.name} (ID: {role_id})")

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
