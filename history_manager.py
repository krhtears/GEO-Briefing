import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"
MAX_HISTORY = 14

def load_history():
    """Loads the history list from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_to_history(results_data, active_personas=None):
    """
    Saves a new briefing result to history.
    results_data: List of dictionaries or a single dictionary representing the briefing.
    active_personas: List of persona names or dicts used in this briefing.
    Example entry: {"timestamp": "...", "data": [...], "personas": [...]}
    """
    history = load_history()
    
    # Calculate KST (UTC+9)
    # If environment is local and already KST, this might double add if we aren't careful.
    # But usually machines are UTC in cloud, or Local in desktop.
    # To be safe and explicit:
    from datetime import timedelta, timezone
    
    # Create KST timezone
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)
    
    new_entry = {
        "timestamp": now_kst.strftime("%Y-%m-%d %H:%M:%S"),
        "data": results_data,
        "personas": active_personas or []
    }
    
    # Prepend new entry
    history.insert(0, new_entry)
    
    # Keep only the last MAX_HISTORY items
    if len(history) > MAX_HISTORY:
        history = history[:MAX_HISTORY]
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def get_history_item(index):
    """Returns a specific history item by index."""
    history = load_history()
    if 0 <= index < len(history):
        return history[index]
    return None
