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
    #520362697620193293: "2025-02-05",  # rafaelvleite
}

# Bot intents (make sure you enable them in the Discord developer portal)
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[LOG] Logged in as {bot.user}")

    # Guild (server) ID and Role ID to be removed
    guild_id = 1335436694844997734  # Comunidade Xadrez Brasil
    role_id = 1336061135446605925  # Membro Comunidade Xadrez Brasil

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
        print(f"[LOG] Checking user {user_id} with scheduled removal date: {removal_date}")

        if today >= removal_date:
            member = guild.get_member(user_id)
            if not member:
                print(f"[WARNING] User with ID {user_id} not found in the guild.")
                continue

            print(f"[LOG] Found member: {member.name} (ID: {user_id})")

            if role in member.roles:
                await member.remove_roles(role)
                print(f"[SUCCESS] Removed role '{role.name}' from {member.name} (ID: {user_id}).")
            else:
                print(f"[INFO] {member.name} (ID: {user_id}) does not have the role '{role.name}'. No action taken.")
        else:
            print(f"[INFO] No action for user {user_id} today. Removal date not reached.")

    print("[LOG] Finished processing all users.")
    await bot.close()

bot.run(TOKEN)
