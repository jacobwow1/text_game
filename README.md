# Text RPG Framework

This is the framework for a custom text-based narrative RPG assembled from JSON files and run in Python.

## Directory Structure
- `content/config.json`: Game settings and stats.
- `content/characters.json`: List of characters in the game.
- `content/chapters/`: Folder containing chapter files, linking dialogues together.
- `content/dialogues/`: Folder containing dialogue trees.

## 1. Adding Stats
Edit `content/config.json` to add new stats and starting points.
```json
{
    "stats": {
        "Intelligence": 1,
        "Wisdom": 1
        ...
    },
    "starting_points": 4
}
```

## 2. Adding Characters
Edit `content/characters.json` to add new people to the office Hub.
```json
[
    {
        "name": "Advisor Name",
        "role": "Job Title",
        "generic_dialogue": "generic_fallback.json"
    }
]
```
- `generic_dialogue`: (Optional) A file to play if the character has no other specific things to say.
*Note: All specific dialogues must be defined in `chapters.json`.*

## 3. Defining Chapters
Create new `.json` files in `content/chapters/` (e.g., `chapter_1.json`, `chapter_2.json`). The game loads them and sorts them by `id`.

```json
{
    "id": 1,
    "title": "Chapter Title",
    "intro_dialogue": "intro.json",
    "end_dialogue": "outro.json",
    "available_characters": {
        "Advisor Name": [
            {
                "file": "secret_dialogue.json",
                "requirements": {"flags": {"found_secret": true}}
            },
            {
                "file": "standard_dialogue.json"
            }
        ]
    },
    "requirements": {
        "flags": {"previous_choice_made": true}
    },
    "time_limit": 3,
    "failure_message": "You failed because..."
}
```
- `time_limit`: (Optional) Integer. If the time counter reaches this value, the chapter ends automatically (triggering `end_dialogue`). 0=Morning, 1=Afternoon, 2=Evening, 3=Night.
- `available_characters`: Can be a simple string (filename) or a list of objects.
    - If a list, the game checks them in order. The first one that meets its `requirements` (and hasn't been completed yet) is chosen.
    - If no dialogue is found, the character's `generic_dialogue` is used.
- `requirements`: (Optional) Conditions to unlock this chapter.

## 4. Writing Dialogue
Create a new `.json` file in `content/dialogues/`.

### Structure
- `start_node`: The ID of the first node.
- `nodes`: A list of dialogue nodes.

### Node Fields
- `id`: Unique string ID.
- `text`: The dialogue text.
- `speaker`: Name of the speaker.
- `sequence`: (Optional) A list of additional dialogue nodes to show in sequence.
    - Each object in the list has a `speaker` and `text` field.
- `choices`: List of options.
*Note: If choices are left empty, the dialogue will be given an "End conversation" option.*

### Choice Fields
- `text`: What the player sees.
- `next_id`: The ID of the node to go to next.
- `requirements`: (Optional) Conditions to see/pick this choice.
    - `stats`: `{"Intelligence": 4}`
    - `flags`: `{"met_before": true}`

### Effects
Modify player stats or flags when a choice is made.
```json
"effects": {
    "stats": {"Wisdom": 1},
    "flags": {"met_advisor": true},
    "end_chapter": true
}
```
- `effects`: (Optional) Changes to game state.
    - `flags`: Set flags (e.g., `"met_advisor": true`).
    - `stats`: Modify stats (e.g., `"Wisdom": 1`).
    - `increment_time`: (Optional) Boolean. If true, advances time by 1 slot.
    - `end_chapter`: (Optional) Boolean. If true, ends the chapter immediately. Use this for major story decisions that advance time.    

### Actions
Modify the player's state when a choice is made.
- `action`: (Optional) Actions to perform when the choice is made.
    - `leave`: (Optional) Boolean. If true, ends conversation ends.

### Example
```json
{
    "start_node": "greeting",
    "nodes": [
        {
            "id": "greeting",
            "text": "Hello.",
            "speaker": "Bob",
            "choices": [
                {
                    "text": "[WISDOM] Are you okay? You look sad.",
                    "next_id": "comfort",
                    "requirements": {
                        "stats": {
                            "Wisdom": 3
                        }
                    },
                    "effects": {
                        "stats": {
                            "Friendship": 1
                        }
                    }
                },
                {
                    "text": "Hey Bob, how are you?",
                    "next_id": "clueless"
                }
            ]
        },
        {
            "id": "comfort",
            "text": "Yeah, I got a bad score on my math exam. Maybe we can study together tomorrow.",
            "speaker": "Bob",
            "effects": {
                "flags": {
                    "study_tomorrow": true
                }
            },
            "choices": []
        },
        {
            "id": "clueless",
            "text": "Don't you know? I just failed my math exam!",
            "speaker": "Bob",
            "choices": [
                {
                    "text": "I'm sorry to hear that. We can study together tomorrow.",
                    "action": "leave",
                    "effects": {
                        "flags": {
                            "study_tomorrow": true
                        }
                    }
                }
            ]
        }    
    ]
}
```

## Running the Game
Run `python3 main.py` in the terminal.
