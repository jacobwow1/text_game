import json
import os
from .player import Player
from .dialogue import DialogueManager
from .ui import GameUI

class Game:
    def __init__(self):
        self.load_config()
        self.player = Player(self.config["stats"])
        self.dialogue_manager = DialogueManager("content/dialogues")
        self.ui = GameUI()
        
        self.chapters = self.load_chapters_data()
        self.current_chapter_idx = 0
        
        self.state = {
            "day": 1,
            "time": "Morning",
            "location": "Office",
            "mode": "START_SCREEN", # Initial mode
            "player": self.player,
            "current_node": None,
            "choices": [],
            "hub_options": [],
            "history": [],
            "chapter": None,
            "points_remaining": self.config.get("starting_points", 8)
        }
        
        self.running = True
        self.characters = self.load_characters()
        self.last_node_id = None

    def load_config(self):
        with open("content/config.json", "r") as f:
            self.config = json.load(f)

    def load_characters(self):
        if os.path.exists("content/characters.json"):
            with open("content/characters.json", "r") as f:
                return json.load(f)
        return []

    def load_chapters_data(self):
        if os.path.exists("content/chapters.json"):
            with open("content/chapters.json", "r") as f:
                return json.load(f)
        return []

    def run(self):
        while self.running:
            self.update()
            self.ui.render(self.state)
            self.handle_input()

    def update(self):
        # Pass notifications to UI
        self.state["notifications"] = self.player.get_notifications()
        self.state["stat_categories"] = self.config.get("stat_categories", {})

        if self.state["mode"] == "START_SCREEN":
            pass # Waiting for input
        elif self.state["mode"] == "STAT_ALLOCATION":
            pass # Waiting for input
        elif self.state["mode"] == "CHAPTER_SPLASH":
            pass # Waiting for input
        elif self.state["mode"] == "STATS_SCREEN":
            pass # Waiting for input
        elif self.state["mode"] == "CHAPTER_START":
            # Load intro dialogue
            chapter = self.chapters[self.current_chapter_idx]
            self.state["chapter"] = chapter
            self.dialogue_manager.load_dialogue(chapter["intro_dialogue"], self.player)
            self.state["mode"] = "DIALOGUE"
            self.state["history"] = []
            self.last_node_id = None
            
            # Pre-process first node so it appears in render
            node = self.dialogue_manager.get_current_node()
            if node:
                speaker = node.get("speaker", "Unknown")
                self.state["history"].append((speaker, node["text"]))
                self.last_node_id = node["id"]
                self.state["choices"] = self.dialogue_manager.get_valid_choices(self.player)
                
                # Fix soft-lock: If no choices, add a "Leave" option
                if not self.state["choices"]:
                    self.state["choices"].append({
                        "text": "[End Conversation]",
                        "action": "leave"
                    })

            # After this dialogue ends, we should go to HUB
            self.state["next_mode_after_dialogue"] = "HUB"
            
        elif self.state["mode"] == "HUB":
            self.update_hub_options()
        elif self.state["mode"] == "DIALOGUE":
            node = self.dialogue_manager.get_current_node()
            self.state["current_node"] = node
            
            # Update history if new node
            if node and node["id"] != self.last_node_id:
                speaker = node.get("speaker", "Unknown")
                self.state["history"].append((speaker, node["text"]))
                self.last_node_id = node["id"]

            self.state["choices"] = self.dialogue_manager.get_valid_choices(self.player)
            
            # Fix soft-lock: If no choices, add a "Leave" option
            if not self.state["choices"]:
                self.state["choices"].append({
                    "text": "[End Conversation]",
                    "action": "leave"
                })

    def update_hub_options(self):
        options = []
        # Add characters to talk to
        for char in self.characters:
            # Check if character is available in this chapter
            chapter = self.state["chapter"]
            available_chars = chapter.get("available_characters", {})
            
            target_dialogue = None
            
            # Handle new list format or old string format
            if isinstance(available_chars, dict):
                if char["name"] in available_chars:
                    char_dialogues = available_chars[char["name"]]
                    
                    # Handle list of conditional dialogues
                    if isinstance(char_dialogues, list):
                        for dialogue_conf in char_dialogues:
                            # Check requirements
                            reqs = dialogue_conf.get("requirements", {})
                            allowed = True
                            
                            # Check stats
                            if "stats" in reqs:
                                for stat, value in reqs["stats"].items():
                                    if self.player.get_stat(stat) < value:
                                        allowed = False
                                        break
                            
                            # Check flags
                            if allowed and "flags" in reqs:
                                for flag, value in reqs["flags"].items():
                                    if self.player.get_flag(flag) != value:
                                        allowed = False
                                        break
                                        
                            if allowed:
                                # Check if already completed
                                if not self.player.has_completed_dialogue(dialogue_conf["file"]):
                                    target_dialogue = dialogue_conf["file"]
                                    break
                                    
                    # Handle simple string (legacy support for simple chapter config)
                    elif isinstance(char_dialogues, str):
                         if not self.player.has_completed_dialogue(char_dialogues):
                            target_dialogue = char_dialogues

            # If no specific dialogue found, check for generic fallback
            if not target_dialogue:
                 # Only show generic if we haven't found a specific one AND character is in the chapter
                 # We assume if they are in available_characters, they are present.
                 # But we might want to only show generic if they have NO other pending dialogues?
                 # The user wants: "go back to a character and have a new dialogue tree... Otherwise, that character would say some generic message"
                 # So if we found no target_dialogue above, we use generic.
                 
                 # Check if character is even in this chapter's available list
                 is_present = False
                 if isinstance(available_chars, dict) and char["name"] in available_chars:
                     is_present = True
                 
                 if is_present:
                     target_dialogue = char.get("generic_dialogue")

            if not target_dialogue:
                continue

            options.append({
                "text": f"Speak to {char['name']} ({char['role']})",
                "action": "talk",
                "target": target_dialogue
            })
        
        options.append({"text": "End Day", "action": "end_day"})
        options.append({"text": "Quit Game", "action": "quit"})
        self.state["hub_options"] = options

    def handle_input(self):
        user_input = self.ui.get_input()
        
        # Global Stats Toggle
        if user_input.lower() in ['s', 'stats'] and self.state["mode"] in ["HUB", "DIALOGUE"]:
            self.state["previous_mode"] = self.state["mode"]
            self.state["mode"] = "STATS_SCREEN"
            return
            
        if self.state["mode"] == "STATS_SCREEN":
            if user_input.lower() in ['b', 'back', 's', 'stats']:
                self.state["mode"] = self.state.get("previous_mode", "HUB")
            return

        if self.state["mode"] == "START_SCREEN":
            self.state["mode"] = "STAT_ALLOCATION"
            return

        if self.state["mode"] == "STAT_ALLOCATION":
            self.handle_stat_allocation(user_input)
            return

        if self.state["mode"] == "CHAPTER_SPLASH":
            self.state["mode"] = "CHAPTER_START"
            return

        try:
            choice_idx = int(user_input) - 1
        except ValueError:
            return

        if self.state["mode"] == "HUB":
            if 0 <= choice_idx < len(self.state["hub_options"]):
                option = self.state["hub_options"][choice_idx]
                if option["action"] == "talk":
                    self.dialogue_manager.load_dialogue(option["target"], self.player)
                    self.state["mode"] = "DIALOGUE"
                    self.state["history"] = []
                    self.last_node_id = None
                    self.state["current_dialogue_file"] = option["target"]
                    self.state["next_mode_after_dialogue"] = "HUB"
                elif option["action"] == "end_day":
                    # Go to chapter end
                    chapter = self.chapters[self.current_chapter_idx]
                    self.dialogue_manager.load_dialogue(chapter["end_dialogue"], self.player)
                    self.state["mode"] = "DIALOGUE"
                    self.state["history"] = []
                    self.last_node_id = None
                    self.state["next_mode_after_dialogue"] = "CHAPTER_END"
                elif option["action"] == "quit":
                    self.running = False
        
        elif self.state["mode"] == "DIALOGUE":
            choices = self.state["choices"]
            if 0 <= choice_idx < len(choices):
                choice = choices[choice_idx]
                
                # Handle "Leave" action
                if choice.get("action") == "leave":
                    self.finish_dialogue()
                    return

                # Add player choice to history
                self.state["history"].append(("You", choice["text"]))

                # Check for special effects
                effects = choice.get("effects", {})
                if effects.get("end_chapter"):
                    self.state["next_mode_after_dialogue"] = "CHAPTER_END"

                if self.dialogue_manager.make_choice(choice_idx, self.player):
                    # Check if dialogue ended (no next node)
                    if not self.dialogue_manager.get_current_node():
                        self.finish_dialogue()

    def finish_dialogue(self):
        # Mark as completed if it was a character dialogue
        if "current_dialogue_file" in self.state:
            self.player.add_completed_dialogue(self.state["current_dialogue_file"])
            del self.state["current_dialogue_file"]

        next_mode = self.state.get("next_mode_after_dialogue", "HUB")
        
        if next_mode == "CHAPTER_END":
            # Advance chapter
            self.current_chapter_idx += 1
            if self.current_chapter_idx < len(self.chapters):
                # Check requirements for next chapter
                next_chapter = self.chapters[self.current_chapter_idx]
                if self.check_chapter_requirements(next_chapter):
                    self.state["chapter"] = next_chapter
                    self.state["mode"] = "CHAPTER_SPLASH"
                else:
                    print("\n[GAME OVER] You did not meet the requirements to proceed.")
                    print(f"Failed Requirement: {next_chapter.get('failure_message', 'Unknown cause')}")
                    self.running = False
            else:
                # Game Over / Win
                print("Game Over - Thanks for playing!")
                self.running = False
        else:
            self.state["mode"] = next_mode

    def check_chapter_requirements(self, chapter):
        reqs = chapter.get("requirements", {})
        # Check stats
        if "stats" in reqs:
            for stat, value in reqs["stats"].items():
                if self.player.get_stat(stat) < value:
                    return False
        
        # Check flags
        if "flags" in reqs:
            for flag, value in reqs["flags"].items():
                if self.player.get_flag(flag) != value:
                    return False
        return True

    def handle_stat_allocation(self, user_input):
        # Simple CLI for stat allocation
        # Input format: "StatName" to increase
        # Or "done" to finish
        if user_input.lower() == "done":
            if self.state["points_remaining"] == 0:
                self.state["chapter"] = self.chapters[self.current_chapter_idx]
                self.state["mode"] = "CHAPTER_SPLASH"
            return
        
        stat = user_input.strip() # Case sensitive for now, or match keys
        
        # Get allowed stats (Personality only)
        allowed_stats = self.config.get("stat_categories", {}).get("Personality", [])
        
        # Find stat with case-insensitive match
        target_stat = None
        for s in allowed_stats:
            if s.lower() == stat.lower():
                target_stat = s
                break
        
        if target_stat and self.state["points_remaining"] > 0:
            self.player.modify_stat(target_stat, 1)
            self.state["points_remaining"] -= 1

