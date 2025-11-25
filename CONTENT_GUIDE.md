# Text RPG Content Guide

This framework allows you to create a story-driven RPG using JSON files.

## Directory Structure
- `content/config.json`: Game settings and stats.
- `content/characters.json`: List of characters in the game.
- `content/dialogues/`: Folder containing dialogue trees.

## 1. Adding Stats
Edit `content/config.json` to add new stats and starting points.
```json
{
    "stats": {
        "Ratio": 1,
        "Providentia": 1
        ...
    },
    "starting_points": 8
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
- `choices`: List of options.

### Choice Fields
- `text`: What the player sees.
- `next_id`: The ID of the node to go to next.
- `requirements`: (Optional) Conditions to see/pick this choice.
    - `stats`: `{"Ratio": 4}`
    - `flags`: `{"met_before": true}`
### Effects
Modify player stats or flags when a choice is made.
```json
"effects": {
    "stats": {"Ratio": 1},
    "flags": {"met_advisor": true},
    "end_chapter": true
}
```
- `effects`: (Optional) Changes to game state.
    - `flags`: Set flags (e.g., `"met_advisor": true`).
    - `stats`: Modify stats (e.g., `"Influence": 1`).
    - `increment_time`: (Optional) Boolean. If true, advances time by 1 slot.
    - `end_chapter`: (Optional) Boolean. If true, ends the chapter immediately. Use this for major story decisions that advance time.

### Example
```json
{
    "id": "greeting",
    "text": "Hello.",
    "speaker": "Bob",
    "choices": [
        {
            "text": "[PROVIDENTIA] You look sad.",
            "next_id": "comfort",
            "requirements": {"stats": {"Providentia": 3}}
        }
    ]
}
```

## Running the Game
Run `python3 main.py` in the terminal.
