import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.player import Player
from engine.dialogue import DialogueManager

class TestEngine(unittest.TestCase):
    def test_player_stats(self):
        config = {"Logic": 1, "Authority": 1}
        p = Player(config)
        self.assertEqual(p.get_stat("Logic"), 1)
        p.modify_stat("Logic", 1)
        self.assertEqual(p.get_stat("Logic"), 2)

    def test_dialogue_flow(self):
        # Mock content dir
        dm = DialogueManager("content/dialogues")
        # We assume sample.json exists from previous steps
        node = dm.load_dialogue("sample.json")
        self.assertEqual(node["id"], "greeting")
        
        # Test choices
        p = Player({"Logic": 5, "Authority": 1}) # High logic to see hidden option
        choices = dm.get_valid_choices(p)
        self.assertEqual(len(choices), 2) # Should see both
        
        # Test making a choice
        dm.make_choice(0, p) # "Let's see it"
        self.assertEqual(dm.current_node_id, "report_view")

if __name__ == '__main__':
    unittest.main()
