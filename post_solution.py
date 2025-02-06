import discord
import json
import os
from dotenv import load_dotenv

# Determinar o caminho base onde o script está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUZZLE_JSON = os.path.join(BASE_DIR, "current_puzzle.json")

# Load environment variables
load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1337058925962334208

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"[LOG] Logged in as {bot.user}")

    # Get the channel where the solution should be posted
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] Channel with ID {CHANNEL_ID} not found.")
        await bot.close()
        return

    # Read the puzzle from the JSON file
    try:
        with open(PUZZLE_JSON, "r") as json_file:
            puzzle = json.load(json_file)
    except FileNotFoundError:
        print("[ERROR] No puzzle file found. Did you run the morning puzzle job?")
        await bot.close()
        return

    # Parse the solution moves and exclude the first move (machine's move)
    moves = puzzle["moves"].split(" ")[1:]  # Exclude the first move
    formatted_moves = ", ".join(moves)

    # Format solution details
    fen_position = puzzle["fen"]

    # Create the solution message
    solution_message = (
        f"✅ **Solução do Puzzle do Dia!** ✅\n\n"
        f"**Melhor sequência de jogadas:** {formatted_moves}\n\n"
        f"🎉 Parabéns aos que acertaram! Continue praticando para melhorar no tabuleiro!\n"
        f"📱 **Quer mais desafios? Baixe o app XB PRO e treine onde estiver!**\n\n"
        f" "
    )

    # Post the solution
    await channel.send(solution_message)
    print(f"[LOG] Solution posted successfully: {fen_position}")

    await bot.close()

bot.run(TOKEN)
