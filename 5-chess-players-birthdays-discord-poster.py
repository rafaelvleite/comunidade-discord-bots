import discord
import os
import json
import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_BIRTHDAY_CHANNEL_ID"))

# Carregar o arquivo JSON fixo com aniversários
BIRTHDAY_FILE = os.path.join(os.path.dirname(__file__), "chess_players_fixed_ptbr.json")

# Ler os aniversários dos jogadores de xadrez
with open(BIRTHDAY_FILE, "r") as file:
    chess_players = json.load(file)

# Obter a data de hoje no formato MM-DD
today = datetime.datetime.now().strftime("%m-%d")

# Inicializar o bot do Discord
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"[LOG] Logado como {bot.user}")

    # Obter o canal do Discord
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERRO] Canal com ID {CHANNEL_ID} não encontrado.")
        await bot.close()
        return

    # Encontrar jogadores com aniversário hoje
    birthday_players = [player for player in chess_players if player["Birth Date"] == today]

    if birthday_players:
        for player in birthday_players:
            # Criar a mensagem de aniversário
            message = f"🎉 **Feliz Aniversário, {player['Name']}!** 🎂🎊\n"
            message += f"📅 Nascido em: {player['Full Birth Date']}\n\n"

            if player.get("Short Bio") and player["Short Bio"] != "Biography not available":
                message += f"📜 **Biografia:** {player['Short Bio']}\n\n"

            if player.get("Wikipedia URL"):
                message += f"📖 [Saiba mais]({player['Wikipedia URL']})\n"

            message += "\nVamos celebrar esta lenda do xadrez hoje! 🏆♟️"
            message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"  # Separador

            # Enviar a mensagem de aniversário no Discord
            await channel.send(message)
            print(f"[LOG] Mensagem de aniversário enviada para {player['Name']}!")

    else:
        print("[LOG] Nenhum aniversário hoje.")

    await bot.close()

bot.run(TOKEN)
