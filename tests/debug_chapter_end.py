import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import Game

def debug_chapter_end():
    print("Initializing Game...")
    game = Game()
    
    # Mock Chapter
    game.chapters = [{
        "id": 1,
        "title": "Test Chapter",
        "intro_dialogue": "intro.json",
        "end_dialogue": "end.json",
        "available_characters": {}
    }]
    game.current_chapter_idx = 0
    game.state["chapter"] = game.chapters[0]
    game.state["mode"] = "HUB"
    
    # Mock Dialogue Manager to return specific nodes
    class MockDialogueManager:
        def __init__(self):
            self.current_node_id = "root"
            
        def load_dialogue(self, file, player):
            print(f"Loading dialogue: {file}")
            self.current_node_id = "root"
            
        def get_current_node(self):
            if self.current_node_id == "root":
                return {
                    "id": "root",
                    "text": "Root Node",
                    "speaker": "NPC"
                }
            elif self.current_node_id == "node_2":
                return {
                    "id": "node_2",
                    "text": "Node 2",
                    "speaker": "NPC"
                }
            return None
            
        def get_valid_choices(self, player):
            if self.current_node_id == "root":
                return [{
                    "text": "Trigger End Chapter",
                    "effects": {"end_chapter": True},
                    "next_id": "node_2" # Go to next node, don't end immediately
                }]
            elif self.current_node_id == "node_2":
                return [{
                    "text": "Leave",
                    "action": "leave"
                }]
            return []
            
        def make_choice(self, idx, player):
            if self.current_node_id == "root":
                self.current_node_id = "node_2"
                return True
            elif self.current_node_id == "node_2":
                self.current_node_id = None
                return True
            return False

    game.dialogue_manager = MockDialogueManager()
    
    # Start dialogue
    print("\n--- Starting Dialogue ---")
    game.state["mode"] = "DIALOGUE"
    game.state["next_mode_after_dialogue"] = "HUB" # Default start
    game.state["choices"] = game.dialogue_manager.get_valid_choices(None)
    
    # 1. Make choice that triggers end_chapter but goes to next node
    print("Making choice: Trigger End Chapter")
    # Simulate handle_input logic
    choice_idx = 0
    choice = game.state["choices"][choice_idx]
    
    # Apply effects
    if choice.get("effects", {}).get("end_chapter"):
        print("Effect triggered: end_chapter")
        game.state["next_mode_after_dialogue"] = "CHAPTER_OUTRO"
        
    game.dialogue_manager.make_choice(choice_idx, None)
    
    # Verify state after first choice
    print(f"Next Mode State: {game.state.get('next_mode_after_dialogue')}")
    if game.state.get("next_mode_after_dialogue") == "CHAPTER_OUTRO":
        print("PASS: State is CHAPTER_OUTRO after effect.")
    else:
        print("FAIL: State lost!")

    # 2. Update loop (simulated)
    print("\n--- Next Turn (Node 2) ---")
    game.state["choices"] = game.dialogue_manager.get_valid_choices(None)
    
    # 3. Make choice to leave
    print("Making choice: Leave")
    choice_idx = 0
    choice = game.state["choices"][choice_idx]
    
    if choice.get("action") == "leave":
        print("Action: leave")
        game.finish_dialogue()
        
    # Verify final state
    print(f"\nFinal Mode: {game.state['mode']}")
    if game.state["mode"] == "CHAPTER_OUTRO":
        print("PASS: Correctly transitioned to CHAPTER_OUTRO.")
    else:
        print(f"FAIL: Expected CHAPTER_OUTRO, got {game.state['mode']}")

if __name__ == "__main__":
    debug_chapter_end()
