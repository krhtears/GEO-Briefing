import json
import os

PERSONAS_FILE = "personas.json"

def load_personas():
    """Returns a list of dictionaries: [{'name': '...', 'prompt': '...'}, ...]"""
    if not os.path.exists(PERSONAS_FILE):
        return []
    
    try:
        with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_personas(personas):
    """Saves the list of personas to the file."""
    with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
        json.dump(personas, f, ensure_ascii=False, indent=4)

def add_persona(name, prompt):
    """Ads a new persona. Returns True if successful, False if full (max 5)."""
    personas = load_personas()
    if len(personas) >= 5:
        return False
    
    # Optional: Check duplicates?
    personas.append({"name": name, "prompt": prompt})
    save_personas(personas)
    return True

def delete_persona(index):
    """Deletes a persona by index."""
    personas = load_personas()
    if 0 <= index < len(personas):
        del personas[index]
        save_personas(personas)
        return True
    return False

def init_default_personas():
    """Initializes file with a default recipient if empty/missing (Optional helper)"""
    # Not strictly required as user can add them, but good for testing.
    pass
