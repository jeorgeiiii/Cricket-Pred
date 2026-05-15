import json
import random
import time
import os

def generate_script(json_path):
    """Generates a dramatic commentary based on the fan reaction data."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        reactions = data.get("fan_reactions", [])
        if not reactions:
            return "The script is missing! Someone call the BCCI writers."

        # Select 3 random reactions to weave into a narrative
        plot_points = random.sample(reactions, 3)
        
        narrative = (
            f"\n🎬 --- LIVE SCRIPT UPDATE ---\n"
            f"The 'Scriptwriter' is cooking a masterpiece at Ekana Stadium.\n\n"
            f"POINT 1: {plot_points[0]}\n"
            f"POINT 2: {plot_points[1]}\n"
            f"POINT 3: {plot_points[2]}\n\n"
            f"PREDICTION: Expect a suspicious DRS call or a 'tactical' misfield "
            f"in the next 2 overs to keep the TV ratings high."
        )
        return narrative
    except Exception as e:
        return f"Error: Could not read script data. {e}"

def main():
    # Path to your data
    data_file = os.path.join('data', 'tweets.json')
    
    print("🚀 IPL Scriptwriter Engine is starting...")
    print(f"Monitoring {data_file} for suspicious drama...\n")

    # Run the engine in a loop to simulate live match updates
    try:
        while True:
            commentary = generate_script(data_file)
            print(f"[{time.strftime('%H:%M:%S')}] NEW PLOT TWIST DETECTED:")
            print(commentary)
            print("-" * 60)
            
            # Update every 30 seconds
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nPipeline stopped. The writers are taking a break.")

if __name__ == "__main__":
    main()