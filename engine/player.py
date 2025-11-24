import json

class Player:
    def __init__(self, stats_config):
        self.stats = stats_config.copy()
        self.flags = {}
        self.inventory = []
        self.completed_dialogues = set()
        self.notifications = []

    def add_completed_dialogue(self, dialogue_id):
        self.completed_dialogues.add(dialogue_id)

    def has_completed_dialogue(self, dialogue_id):
        return dialogue_id in self.completed_dialogues


    def get_stat(self, stat_name):
        return self.stats.get(stat_name, 0)

    def set_stat(self, stat_name, value):
        self.stats[stat_name] = value

    def modify_stat(self, stat_name, amount):
        if stat_name in self.stats:
            self.stats[stat_name] += amount
            # Add notification
            sign = "+" if amount > 0 else ""
            self.notifications.append(f"{stat_name} {sign}{amount}")

    def get_notifications(self):
        notifs = self.notifications[:]
        self.notifications = []
        return notifs

    def set_flag(self, flag_name, value):
        self.flags[flag_name] = value
        # Optional: Notify on flag changes? Maybe too noisy.
        # self.notifications.append(f"Flag updated: {flag_name}")

    def get_flag(self, flag_name):
        return self.flags.get(flag_name, False)
    
    def check_requirement(self, req_type, req_name, req_value):
        if req_type == "stats":
            return self.get_stat(req_name) >= req_value
        elif req_type == "flags":
            return self.get_flag(req_name) == req_value
        return False
