import discord
import pandas as pd
import zstandard as zstd
import os
import chess
import chess.svg
import cairosvg
import json
from dotenv import load_dotenv

# Determinar o caminho base onde o script está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUZZLE_FILE = os.path.join(BASE_DIR, "filtered_puzzles.csv.zst")
PUZZLE_IMAGE = os.path.join(BASE_DIR, "puzzle.png")
PUZZLE_JSON = os.path.join(BASE_DIR, "current_puzzle.json")
POSTED_PUZZLES_LOG = os.path.join(BASE_DIR, "posted_puzzles.json")

# Load environment variables
load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1337058925962334208

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

def post_solution(channel):
    """Post the solution of the previous puzzle."""
    try:
        with open(PUZZLE_JSON, "r") as json_file:
            puzzle = json.load(json_file)
    except FileNotFoundError:
        print("[ERROR] No puzzle file found. Did you run the previous job?")
        return

    # Parse the solution moves and exclude the first move (machine's move)
    moves = puzzle["moves"].split(" ")[1:]  # Exclude the first move
    formatted_moves = ", ".join(moves)

    # Create the solution message
    solution_message = (
        f"✅ **Solução do Puzzle da Hora!** ✅\n\n"
        f"**Melhor sequência de jogadas:** {formatted_moves}\n\n"
        f"🎉 Parabéns aos que acertaram! Continue praticando para melhorar no tabuleiro!\n"
        f"📱 **Quer mais desafios? Baixe o app XB PRO e treine onde estiver!**\n\n"
    )

    return solution_message

def get_random_puzzle():
    """Read the compressed CSV file and return a random puzzle that hasn't been posted recently."""
    with open(PUZZLE_FILE, "rb") as file:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(file) as reader:
            df = pd.read_csv(reader)

            # Load previously posted puzzles
            if os.path.exists(POSTED_PUZZLES_LOG):
                with open(POSTED_PUZZLES_LOG, "r") as log_file:
                    posted_puzzles = set(json.load(log_file))
            else:
                posted_puzzles = set()

            # Filter puzzles that haven't been posted recently
            available_puzzles = df[~df['PuzzleId'].isin(posted_puzzles)]

            # Select a random puzzle
            if len(available_puzzles) == 0:
                print("[WARNING] No more puzzles available. Resetting the log.")
                posted_puzzles.clear()
                available_puzzles = df

            puzzle = available_puzzles.sample(n=1).iloc[0]

            # Update posted puzzles log
            posted_puzzles.add(str(puzzle["PuzzleId"]))
            with open(POSTED_PUZZLES_LOG, "w") as log_file:
                json.dump(list(posted_puzzles), log_file)

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

def render_chessboard(board, output_file=PUZZLE_IMAGE):
    """Render the chessboard and save it as a PNG image."""
    # Invert the board if it's Black's turn to move
    flip_board = (board.turn == chess.BLACK)
    svg_board = chess.svg.board(board=board, flipped=flip_board)

    # Convert SVG to PNG and save it
    cairosvg.svg2png(bytestring=svg_board, write_to=output_file)

@bot.event
async def on_ready():
    print(f"[LOG] Logged in as {bot.user}")

    # Get the channel where the puzzle and solution should be posted
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"[ERROR] Channel with ID {CHANNEL_ID} not found.")
        await bot.close()
        return

    # STEP 1: Post the solution of the previous puzzle
    solution_message = post_solution(channel)
    if solution_message:
        await channel.send(solution_message)
        print("[LOG] Solution posted successfully.")

    # STEP 2: Post the new puzzle
    puzzle = get_random_puzzle()

    # Parse the moves and apply the first move to get the puzzle position
    moves = puzzle["moves"].split(" ")
    first_move = moves[0]  # First move from the solution
    puzzle_board = get_puzzle_position(puzzle["fen"], first_move)

    # Save puzzle details to JSON for the next solution post
    with open(PUZZLE_JSON, "w") as json_file:
        json.dump(puzzle, json_file)

    # Render and save the puzzle image
    render_chessboard(puzzle_board, output_file=PUZZLE_IMAGE)

    # Create the message
    black_turn = (puzzle_board.turn == chess.BLACK)
    turn_message = "Pretas jogam" if black_turn else "Brancas jogam"

    puzzle_message = (
        f"♟️ **Puzzle da Hora da Comunidade Xadrez Brasil!** ♟️\n"
        f"🔍 **Encontre a melhor sequência de jogadas!**\n\n"
        f"**Tema:** {puzzle['themes'].replace(' ', ', ')}\n"
        f"**Dificuldade:** {puzzle['rating']} pontos\n"
        f"**{turn_message}**\n\n"
        f"💡 Poste suas respostas abaixo e volte ao final da hora para ver a solução! 🎯\n\n"
        f"🔐 **Envie sua resposta no formato de anti-spoiler para evitar revelar a outros membros:**\n"
        f"**Exemplo:** `||e2e4 e7e5||`\n"
    )

    # Post the puzzle
    message = await channel.send(puzzle_message, file=discord.File(PUZZLE_IMAGE))
    print(f"[LOG] New puzzle posted successfully: {puzzle['fen']}")

    await bot.close()

bot.run(TOKEN)
