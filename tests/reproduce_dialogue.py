import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.core import Game
from engine.player import Player

def test_dialogue_logic():
    print("Initializing Game...")
    game = Game()
    
    # Mock Chapter 1 Data with our new structure
    # We rely on the actual files we created, so we just need to ensure we are in the right state
    game.current_chapter_idx = 0
    game.state["chapter"] = game.chapters[0]
    
    # Mock Player
    player = game.player
    
    print("\n--- Test Case 1: Default Dialogue ---")
    # Initially, no flags. Should get "chen_default.json"
    game.update_hub_options()
    options = game.state["hub_options"]
    chen_option = next((o for o in options if "Advisor Chen" in o["text"]), None)
    
    if chen_option and chen_option["target"] == "chen_default.json":
        print("PASS: Correctly selected default dialogue.")
    else:
        print(f"FAIL: Expected chen_default.json, got {chen_option['target'] if chen_option else 'None'}")

    print("\n--- Test Case 2: Dialogue Completion & Fallback ---")
    # Mark default as completed
    player.add_completed_dialogue("chen_default.json")
    
    # Now, since we don't have the secret flag, we should fall back to generic
    game.update_hub_options()
    options = game.state["hub_options"]
    chen_option = next((o for o in options if "Advisor Chen" in o["text"]), None)
    
    if chen_option and chen_option["target"] == "chen_generic.json":
        print("PASS: Correctly fell back to generic dialogue.")
    else:
        print(f"FAIL: Expected chen_generic.json, got {chen_option['target'] if chen_option else 'None'}")

    print("\n--- Test Case 3: Conditional Dialogue ---")
    # Set the flag
    player.set_flag("found_secret", True)
    
    # Now we should see the secret dialogue
    game.update_hub_options()
    options = game.state["hub_options"]
    chen_option = next((o for o in options if "Advisor Chen" in o["text"]), None)
    
    if chen_option and chen_option["target"] == "chen_secret.json":
        print("PASS: Correctly selected secret dialogue after flag set.")
    else:
        print(f"FAIL: Expected chen_secret.json, got {chen_option['target'] if chen_option else 'None'}")

    print("\n--- Test Case 4: All Completed ---")
    # Mark secret as completed too
    player.add_completed_dialogue("chen_secret.json")
    
    # Should fall back to generic again
    game.update_hub_options()
    options = game.state["hub_options"]
    chen_option = next((o for o in options if "Advisor Chen" in o["text"]), None)
    
    if chen_option and chen_option["target"] == "chen_generic.json":
        print("PASS: Correctly fell back to generic after all specifics completed.")
    else:
        print(f"FAIL: Expected chen_generic.json, got {chen_option['target'] if chen_option else 'None'}")

if __name__ == "__main__":
    test_dialogue_logic()
