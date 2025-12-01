import json
import os

class DialogueManager:
    def __init__(self, content_dir):
        self.content_dir = content_dir
        self.current_dialogue = None
        self.current_node_id = None

    def load_dialogue(self, filename, player=None):
        path = os.path.join(self.content_dir, filename)
        with open(path, 'r') as f:
            self.current_dialogue = json.load(f)
        
        start_ref = self.current_dialogue.get("start_node", "root")
        self.current_node_id = self._resolve_node_id(start_ref, player)
        
        if player:
            node = self.get_current_node()
            if node:
                self._apply_effects(node.get("effects", {}), player)
                
        return self.get_current_node()

    def get_current_node(self):
        if not self.current_dialogue:
            return None
        
        # Find node by ID
        nodes = self.current_dialogue.get("nodes", [])
        for node in nodes:
            if node["id"] == self.current_node_id:
                return node
        return None

    def _resolve_node_id(self, id_ref, player):
        """
        Resolves a node ID reference which can be a string or a list of conditional targets.
        """
        if isinstance(id_ref, str):
            return id_ref
        
        if isinstance(id_ref, list):
            for target in id_ref:
                # Check requirements
                reqs = target.get("requirements", {})
                allowed = True
                
                if player:
                    # Check stats
                    if "stats" in reqs:
                        for stat, value in reqs["stats"].items():
                            if player.get_stat(stat) < value:
                                allowed = False
                                break
                    
                    # Check flags
                    if allowed and "flags" in reqs:
                        for flag, value in reqs["flags"].items():
                            if player.get_flag(flag) != value:
                                allowed = False
                                break
                
                if allowed:
                    return target["id"]
            
            # If no match found, return None or maybe the last one?
            # For now return None, which will result in end of dialogue or error
            return None
            
        return None

    def _apply_effects(self, effects, player):
        if "flags" in effects:
            for flag, value in effects["flags"].items():
                player.set_flag(flag, value)
        if "stats" in effects:
            for stat, value in effects["stats"].items():
                player.modify_stat(stat, value)

    def get_valid_choices(self, player):
        node = self.get_current_node()
        if not node:
            return []
        
        valid_choices = []
        for choice in node.get("choices", []):
            # Check requirements
            reqs = choice.get("requirements", {})
            allowed = True
            
            # Check stats
            if "stats" in reqs:
                for stat, value in reqs["stats"].items():
                    if player.get_stat(stat) < value:
                        allowed = False
                        break
            
            # Check flags
            if "flags" in reqs:
                for flag, value in reqs["flags"].items():
                    if player.get_flag(flag) != value:
                        allowed = False
                        break
            
            if allowed:
                valid_choices.append(choice)
        
        return valid_choices

    def make_choice(self, choice_index, player):
        choices = self.get_valid_choices(player)
        if 0 <= choice_index < len(choices):
            choice = choices[choice_index]
            
            # Apply choice effects
            self._apply_effects(choice.get("effects", {}), player)

            next_ref = choice.get("next_id")
            self.current_node_id = self._resolve_node_id(next_ref, player)
            
            # Apply new node effects
            new_node = self.get_current_node()
            if new_node:
                self._apply_effects(new_node.get("effects", {}), player)
                
            return True
        return False
