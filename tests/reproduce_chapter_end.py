import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import Game

def test_chapter_end_logic():
    print("Initializing Game...")
    game = Game()
    
    # Mock Chapter 1 with an end dialogue
    game.chapters = [
        {
            "id": 1,
            "title": "Chapter 1",
            "intro_dialogue": "intro.json",
            "end_dialogue": "end_1.json",
            "time_limit": 1,
            "available_characters": {}
        },
        {
            "id": 2,
            "title": "Chapter 2",
            "intro_dialogue": "intro_2.json",
            "end_dialogue": "end_2.json",
            "available_characters": {}
        }
    ]
    game.current_chapter_idx = 0
    game.state["chapter"] = game.chapters[0]
    game.state["mode"] = "HUB"
    game.state["time"] = 0
    
    # Mock DialogueManager to track what's loaded
    loaded_dialogues = []
    original_load = game.dialogue_manager.load_dialogue
    def mock_load(file, player):
        loaded_dialogues.append(file)
        # We don't actually need to load real files for this test logic check
        # But the game might crash if we don't have a node. 
        # Let's just mock the current node to be None so it finishes immediately if run?
        # Or better, just track the calls.
    
    game.dialogue_manager.load_dialogue = mock_load
    
    print("\n--- Test Case: Time Limit Trigger ---")
    # Simulate time increment reaching limit
    game.state["time"] = 1 # Limit is 1
    
    # Simulate what handle_input does now: sets next mode to CHAPTER_OUTRO
    game.state["next_mode_after_dialogue"] = "CHAPTER_OUTRO"
    
    # 1. Finish the current dialogue (the one that triggered the time limit)
    print("Calling finish_dialogue() (End of current interaction)...")
    game.finish_dialogue()
    
    # Check state
    if game.state["mode"] == "CHAPTER_OUTRO":
        print("PASS: Mode set to CHAPTER_OUTRO.")
    else:
        print(f"FAIL: Expected CHAPTER_OUTRO, got {game.state['mode']}")

    # 2. Run update() to handle CHAPTER_OUTRO (load end dialogue)
    print("Calling update() (Handling CHAPTER_OUTRO)...")
    game.update()
    
    # Check if end_1.json was loaded
    if "end_1.json" in loaded_dialogues:
        print("PASS: Chapter 1 end dialogue was loaded.")
    else:
        print("FAIL: Chapter 1 end dialogue was NOT loaded.")
        print(f"Loaded dialogues: {loaded_dialogues}")
        
    # Check state - should be DIALOGUE now, waiting for user to read outro
    if game.state["mode"] == "DIALOGUE":
        print("PASS: Mode set to DIALOGUE (Outro playing).")
    else:
        print(f"FAIL: Expected DIALOGUE, got {game.state['mode']}")
        
    # Check next mode - should be CHAPTER_ADVANCE
    if game.state["next_mode_after_dialogue"] == "CHAPTER_ADVANCE":
        print("PASS: Next mode set to CHAPTER_ADVANCE.")
    else:
        print(f"FAIL: Expected CHAPTER_ADVANCE, got {game.state.get('next_mode_after_dialogue')}")

    # 3. Finish the outro dialogue
    print("Calling finish_dialogue() (End of Outro)...")
    game.finish_dialogue()
    
    # Check state
    if game.state["mode"] == "CHAPTER_ADVANCE":
        print("PASS: Mode set to CHAPTER_ADVANCE.")
    else:
        print(f"FAIL: Expected CHAPTER_ADVANCE, got {game.state['mode']}")

    # 4. Run update() to handle CHAPTER_ADVANCE (increment index)
    print("Calling update() (Handling CHAPTER_ADVANCE)...")
    game.update()
    
    # Check if we advanced to chapter 2
    if game.current_chapter_idx == 1:
        print("PASS: Advanced to Chapter 2.")
    else:
        print(f"FAIL: Did not advance to Chapter 2. Index: {game.current_chapter_idx}")

if __name__ == "__main__":
    test_chapter_end_logic()
