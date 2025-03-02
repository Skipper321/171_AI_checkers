import subprocess
import multiprocessing
import numpy as np
import random
import sys

# Number of games to play
NUM_GAMES = 100  
NUM_CORES = multiprocessing.cpu_count()  # Use all CPU cores

# Paths to AI scripts
STUDENT_AI_PATH = "../src/checkers-python/main.py"
POOR_AI_PATH = "Sample_AIs/Poor_AI/main.py"

def play_game(game_num):
    """Runs a single game with StudentAI randomly assigned as Player 1 or Player 2"""
    
    # Randomly assign StudentAI to Player 1 or Player 2
    if random.random() < 0.5:
        command = f"python3 AI_Runner.py 8 8 2 l {STUDENT_AI_PATH} {POOR_AI_PATH}"
        student_is_player_1 = True
    else:
        command = f"python3 AI_Runner.py 8 8 2 l {POOR_AI_PATH} {STUDENT_AI_PATH}"
        student_is_player_1 = False

    try:
        # Run the game and capture the output
        result = subprocess.run(command.split(), capture_output=True, text=True)
        output = result.stdout.lower()

        # Determine if StudentAI won
        if "player 1 wins" in output:
            win = 1 if student_is_player_1 else 0
        elif "player 2 wins" in output:
            win = 1 if not student_is_player_1 else 0
        else:
            win = 1  # Tie counts as a win

        # Print progress
        print(f"✅ Game {game_num+1}/{NUM_GAMES} complete - {'Win' if win else 'Loss'}", flush=True)
        return win

    except Exception as e:
        print(f"❌ Error in game {game_num+1}: {e}", flush=True)
        return 0  # Count as a loss if an error occurs

if __name__ == "__main__":
    print(f"\n🎮 Running {NUM_GAMES} games with StudentAI...\n")

    # Run games in parallel using multiprocessing
    with multiprocessing.Pool(NUM_CORES) as pool:
        results = pool.map(play_game, range(NUM_GAMES))

    # Calculate win rate
    win_rate = np.mean(results) * 100

    # Print final results
    print(f"\n📊 Results after {NUM_GAMES} games:")
    print(f"🏆 Wins: {sum(results)}")
    print(f"❌ Losses: {NUM_GAMES - sum(results)}")
    print(f"🎯 Win Rate: {win_rate:.2f}%")

    # Check if requirement is met
    if win_rate >= 60:
        print("✅ StudentAI meets the 60% win rate requirement!")
    else:
        print("❌ StudentAI does not meet the requirement. Keep improving!")
