import subprocess

# Number of games to play
NUM_GAMES = 100

# Paths to AI scripts
STUDENT_AI_PATH = "../src/checkers-python/main.py"
RANDOM_AI_PATH = "Sample_AIs/Random_AI/main.py"

# Command to run AI_Runner
BASE_COMMAND = f"python3 AI_Runner.py 8 8 2 l {STUDENT_AI_PATH} {RANDOM_AI_PATH}"

# Track results
student_wins = 0
random_wins = 0
ties = 0

for i in range(NUM_GAMES):
    print(f"Running game {i + 1}/{NUM_GAMES}...")

    # Run the AI_Runner script
    result = subprocess.run(BASE_COMMAND.split(), capture_output=True, text=True)

    # Extract game result from output
    output = result.stdout
    if "player 1 wins" in output.lower():  # Adjust if your AI is player 1
        student_wins += 1
    elif "player 2 wins" in output.lower():  # Adjust if RandomAI is player 2
        random_wins += 1
    else:  # Tie case (assume tie message is clear)
        ties += 1
        student_wins += 1  # Since ties count as wins

# Calculate win rate
win_rate = (student_wins / NUM_GAMES) * 100

# Print final results
print(f"\nResults after {NUM_GAMES} games:")
print(f"StudentAI Wins: {student_wins}")
print(f"RandomAI Wins: {random_wins}")
print(f"Ties: {ties}")
print(f"Win Rate: {win_rate:.2f}%")

# Check if requirement is met
if win_rate >= 60:
    print("StudentAI meets the requirement")
else:
    print("StudentAI does not meet the 60% win rate requirement. Keep improving!")
