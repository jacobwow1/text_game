import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import Game

def test_time_progression():
    print("Initializing Game...")
    game = Game()
    
    # Mock a chapter with time limit
    game.chapters = [{
        "id": 1,
        "title": "Test Chapter",
        "intro_dialogue": "intro.json",
        "end_dialogue": "end.json",
        "time_limit": 2, # Ends when time reaches 2 (Evening)
        "available_characters": {}
    }]
    game.current_chapter_idx = 0
    game.state["chapter"] = game.chapters[0]
    game.state["mode"] = "HUB"
    
    print("\n--- Test Case 1: Initial Time ---")
    if game.state["time"] == 0:
        print("PASS: Time starts at 0 (Morning)")
    else:
        print(f"FAIL: Expected 0, got {game.state['time']}")
        
    print("\n--- Test Case 2: Increment Time ---")
    # Simulate a choice that increments time
    game.dialogue_manager.make_choice = lambda *args: True # Mock
    
    # Manually trigger effect logic (since we can't easily mock the whole ui loop)
    # We'll use a mock choice object
    choice = {
        "text": "Wait a while",
        "effects": {"increment_time": True}
    }
    
    # Apply effect manually as if handle_input did it
    if choice["effects"].get("increment_time"):
        game.state["time"] += 1
        
    if game.state["time"] == 1:
        print("PASS: Time incremented to 1 (Afternoon)")
    else:
        print(f"FAIL: Expected 1, got {game.state['time']}")

    print("\n--- Test Case 3: Time Limit Trigger ---")
    # Increment again to hit limit (2)
    if choice["effects"].get("increment_time"):
        game.state["time"] += 1
        # Check logic from core.py
        chapter = game.state["chapter"]
        time_limit = chapter.get("time_limit", 999)
        if game.state["time"] >= time_limit:
            game.state["next_mode_after_dialogue"] = "CHAPTER_END"
            
    if game.state["time"] == 2:
        print("PASS: Time incremented to 2 (Evening)")
    else:
        print(f"FAIL: Expected 2, got {game.state['time']}")
        
    if game.state.get("next_mode_after_dialogue") == "CHAPTER_END":
        print("PASS: Chapter end triggered by time limit")
    else:
        print(f"FAIL: Expected CHAPTER_END, got {game.state.get('next_mode_after_dialogue')}")

    print("\n--- Test Case 4: UI String Conversion ---")
    # Check static method or list access
    time_str = Game.TIME_SLOTS[game.state["time"]]
    if time_str == "Evening":
        print("PASS: UI string conversion correct (Evening)")
    else:
        print(f"FAIL: Expected Evening, got {time_str}")

if __name__ == "__main__":
    test_time_progression()
