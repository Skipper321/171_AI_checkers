import subprocess
import multiprocessing
import numpy as np

# Number of games to play
NUM_GAMES = 100  
NUM_CORES = multiprocessing.cpu_count()  # Use all CPU cores

# Paths to AI scripts
STUDENT_AI_PATH = "../src/checkers-python/main.py"
RANDOM_AI_PATH = "Sample_AIs/Random_AI/main.py"
BASE_COMMAND = f"python3 AI_Runner.py 8 8 2 l {STUDENT_AI_PATH} {RANDOM_AI_PATH}"

def play_game(_):
    """Runs a single game and returns the result (1 = win/Tie, 0 = loss)"""
    result = subprocess.run(BASE_COMMAND.split(), capture_output=True, text=True)
    output = result.stdout.lower()
    
    if "player 1 wins" in output:
        return 1  # Win
    elif "player 2 wins" in output:
        return 0  # Loss
    else:
        return 1  # Tie counts as a win

if __name__ == "__main__":
    # Run games in parallel using multiprocessing
    with multiprocessing.Pool(NUM_CORES) as pool:
        results = pool.map(play_game, range(NUM_GAMES))

    # Calculate win rate
    win_rate = np.mean(results) * 100

    # Print final results
    print(f"\nResults after {NUM_GAMES} games:")
    print(f"StudentAI Wins: {sum(results)}")
    print(f"Losses: {NUM_GAMES - sum(results)}")
    print(f"Win Rate: {win_rate:.2f}%")

    # Check if requirement is met
    if win_rate >= 60:
        print("StudentAI meets the 60% win rate requirement!")
    else:
        print("StudentAI does not meet the requirement. Keep improving!")
