import discord
import random
import pandas as pd
import zstandard as zstd
import os
import chess
import chess.svg
import cairosvg
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1337058925962334208

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

def get_random_puzzle():
    """Read the compressed CSV file and return a random puzzle."""
    with open("./lichess_db_puzzle.csv.zst", "rb") as file:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(file) as reader:
            df = pd.read_csv(reader)
            puzzle = df.sample(n=1).iloc[0]  # Randomly select one puzzle

            # Convert to serializable types
            return {
                "puzzle_id": str(puzzle["PuzzleId"]),
                "fen": str(puzzle["FEN"]),
                "moves": str(puzzle["Moves"]),
                "rating": int(puzzle["Rating"]),
                "themes": str(puzzle["Themes"]),
                "game_url": str(puzzle["GameUrl"]),
                "opening_tags": str(puzzle["OpeningTags"])
            }

def get_puzzle_position(fen, first_move):
    """Apply the first move to the FEN and return the resulting position."""
    board = chess.Board(fen)
    
    # Apply the first move from the solution
    move = chess.Move.from_uci(first_move)
    board.push(move)
    
    return board

def render_chessboard(board, output_file="puzzle.png"):
    """Render the chessboard and save it as a PNG image."""
    # Invert the board if it's Black's turn to move
    flip_board = (board.turn == chess.BLACK)
    svg_board = chess.svg.board(board=board, flipped=flip_board)

    # Convert SVG to PNG and save it
    cairosvg.svg2png(bytestring=svg_board, write_to=output_file)

@bot.event
async def on_ready():
    print(f"[LOG] Logged in as {bot.user}")

    # Get the channel where the puzzle should be posted
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] Channel with ID {CHANNEL_ID} not found.")
        await bot.close()
        return

    # Get a random puzzle and save it to a JSON file for the evening solution
    puzzle = get_random_puzzle()

    # Parse the moves and apply the first move to get the puzzle position
    moves = puzzle["moves"].split(" ")
    first_move = moves[0]  # First move from the solution
    puzzle_board = get_puzzle_position(puzzle["fen"], first_move)
    
    # Save puzzle details to JSON for the solution
    with open("./current_puzzle.json", "w") as json_file:
        json.dump(puzzle, json_file)

    # Render and save the puzzle image
    render_chessboard(puzzle_board, output_file="puzzle.png")

    # Create the message
    black_turn = (puzzle_board.turn == chess.BLACK)
    if black_turn:
        turn_message = "Pretas jogam"
    else:
        turn_message = "Brancas jogam"

    puzzle_message = (
        f"♟️ **Puzzle do Dia da Comunidade Xadrez Brasil!** ♟️\n"
        f"🔍 **Encontre a melhor sequência de jogadas!**\n\n"
        f"**Tema:** {puzzle['themes'].replace(' ', ', ')}\n"
        f"**Dificuldade:** {puzzle['rating']} pontos\n"
        f"**{turn_message}**\n\n"
        f"💡 Poste suas respostas abaixo e volte ao final do dia para ver a solução! 🎯\n\n"
        f"🔐 **Envie sua resposta no formato de anti-spoiler para evitar revelar a outros membros:**\n"
        f"**Exemplo:** `||e2e4 e7e5||`\n"
    )

    # Enviar a mensagem com a imagem do puzzle
    await channel.send(puzzle_message, file=discord.File("./puzzle.png"))
    print(f"[LOG] Puzzle posted successfully: {puzzle['fen']}")

    await bot.close()

bot.run(TOKEN)
