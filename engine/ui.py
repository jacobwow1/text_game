from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt

class GameUI:
    def __init__(self):
        self.console = Console()

    def render(self, game_state):
        self.console.clear()
        
        # Check for notifications
        notifications = game_state.get("notifications", [])
        notif_text = ""
        if notifications:
            notif_text = " | ".join([f"[bold yellow]{n}[/]" for n in notifications])
            
        if game_state['mode'] == 'START_SCREEN':
            self.console.print(Panel("[bold green]Consul of Concordia[/]\n\nPress Enter to Start", title="Welcome"))
            return

        if game_state['mode'] == 'STAT_ALLOCATION':
            text = f"Points Remaining: {game_state['points_remaining']}\n\n"
            text += "Type the name of a stat to increase it. Type 'done' when finished.\n\n"
            
            table = Table()
            table.add_column("Stat")
            table.add_column("Value")
            
            # Only show Personality stats
            categories = game_state.get('stat_categories', {})
            personality_stats = categories.get("Personality", [])
            
            for stat in personality_stats:
                value = game_state['player'].get_stat(stat)
                table.add_row(stat, str(value))
            
            self.console.print(Panel(text, title="Character Creation"))
            self.console.print(table)
            return

        if game_state['mode'] == 'CHAPTER_SPLASH':
            chapter = game_state.get('chapter')
            title = chapter['title'] if chapter else "Unknown Chapter"
            self.console.print(Panel(f"[bold magenta]{title}[/]\n\nPress Enter to Begin", title="Chapter Start"))
            return

        # Header (Only show for in-game states)
        from .core import Game
        time_str = Game.TIME_SLOTS[game_state['time']] if 0 <= game_state['time'] < len(Game.TIME_SLOTS) else "Late Night"
        header_text = f"Day: {game_state['day']} | Time: {time_str} | Location: {game_state['location']}"
        if notif_text:
            header_text += f"\n\nUpdates: {notif_text}"
            
        self.console.print(Panel(header_text, title="State", style="bold blue"))

        if game_state['mode'] == 'STATS_SCREEN':
            self.render_stats_screen(game_state)
            return

        if game_state['mode'] == 'GAME_OVER':
            message = game_state.get('game_over_message', 'Game Over')
            self.console.print(Panel(f"[bold red]{message}[/]\n\nPress Enter to Quit", title="Game Over"))
            return

        # Main Content (Dialogue or Hub)
        main_content = ""
        if game_state['mode'] == 'HUB':
            main_content = "You are in your office. Who would you like to speak with?\n\n"
            # Show available characters? No, they are in choices.
            # Maybe show some flavor text or status.
            main_content += "[dim]Press 'S' to view Stats[/]"
        elif game_state['mode'] == 'DIALOGUE':
            history = game_state.get('history', [])
            
            # Truncate history to fit in panel (show last 6 items)
            MAX_HISTORY = 6
            display_history = history[-MAX_HISTORY:]
            
            if len(history) > MAX_HISTORY:
                main_content += "[dim]... (previous messages hidden) ...[/]\n\n"
            
            for speaker, text in display_history:
                if speaker == "You":
                    main_content += f"[bold cyan]You:[/] {text}\n\n"
                else:
                    main_content += f"[bold yellow]{speaker}:[/] {text}\n\n"
            
            # Show current node text if not in history (it should be, but just in case)
            # Actually, core.py handles history.
            pass
            
        self.console.print(Panel(main_content, title="Story"))

        # Actions (Footer)
        choices = game_state.get('choices', [])
        if game_state['mode'] == 'HUB':
            choices = game_state.get('hub_options', [])
        
        action_text = ""
        for i, choice in enumerate(choices):
            action_text += f"{i+1}. {choice['text']}\n"
        
        if not action_text:
            action_text = "..."
            
        self.console.print(Panel(action_text, title="Actions"))

    def render_stats_screen(self, game_state):
        player = game_state['player']
        categories = game_state.get('stat_categories', {})
        
        # If no categories defined, just show all in one
        if not categories:
            categories = {"General": list(player.stats.keys())}
            
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column()
        
        for cat, stats in categories.items():
            table = Table(title=cat, box=None)
            table.add_column("Stat")
            table.add_column("Value")
            
            for stat in stats:
                val = player.get_stat(stat)
                table.add_row(stat, str(val))
            
            grid.add_row(table)
            grid.add_row("") # Spacer

        self.console.print(Panel(grid, title="Player Stats (Press 'B' to Back)"))

    def get_input(self):
        return Prompt.ask("Select an option")
