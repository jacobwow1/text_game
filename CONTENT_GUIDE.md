# Text RPG Content Guide

This framework allows you to create a story-driven RPG using JSON files.

## Directory Structure
- `content/config.json`: Game settings and stats.
- `content/characters.json`: List of characters in the game.
- `content/dialogues/`: Folder containing dialogue trees.

## 1. Defining Stats
Edit `content/config.json` to change the available stats and starting points.
```json
{
    "stats": {
        "Logic": 1,
        "Empathy": 1
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
        "dialogue_file": "default.json" 
    }
]
```
*Note: The `dialogue_file` here is a default/fallback. Specific dialogues are usually defined in `chapters.json`.*

## 3. Defining Chapters
Edit `content/chapters.json` to create the story flow.
```json
[
    {
        "id": 1,
        "title": "Chapter Title",
        "intro_dialogue": "intro.json",
        "end_dialogue": "outro.json",
        "available_characters": {
            "Advisor Name": "chapter1_advisor.json"
        },
        "requirements": {
            "flags": {"previous_choice_made": true}
        },
        "failure_message": "You failed because..."
    }
]
```
- `available_characters`: A dictionary mapping character names to their dialogue file for this chapter.
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
    - `stats`: `{"Logic": 4}`
    - `flags`: `{"met_before": true}`
### Effects
Modify player stats or flags when a choice is made.
```json
"effects": {
    "stats": {"Logic": 1},
    "flags": {"met_advisor": true},
    "end_chapter": true
}
```
- `end_chapter`: If set to `true`, the chapter will end (triggering the Outro dialogue) as soon as this conversation finishes. Use this for major story decisions that advance time.
- `effects`: (Optional) Changes to make when chosen.
    - `stats`: `{"Authority": 1}`
    - `flags`: `{"angered_advisor": true}`

### Example
```json
{
    "id": "greeting",
    "text": "Hello.",
    "speaker": "Bob",
    "choices": [
        {
            "text": "[EMPATHY] You look sad.",
            "next_id": "comfort",
            "requirements": {"stats": {"Empathy": 3}}
        }
    ]
}
```

## Running the Game
Run `python3 main.py` in the terminal.
