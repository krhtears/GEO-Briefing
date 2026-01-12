import json
import os

COMPETITORS_FILE = "competitors.json"

def load_competitors():
    """Loads the competitor list from the JSON file."""
    if not os.path.exists(COMPETITORS_FILE):
        return []
    
    with open(COMPETITORS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_competitors(competitors):
    """Saves the competitor list to the JSON file."""
    with open(COMPETITORS_FILE, "w", encoding="utf-8") as f:
        json.dump(competitors, f, ensure_ascii=False, indent=4)

def calculate_stats(results_data):
    """
    Counts references to competitors in the briefing results.
    results_data: List of dicts [{'gemini': '...', 'gpt': '...'}, ...]
    Returns: Dict {BrandName: Count}
    """
    competitors = load_competitors()
    stats = {c['name']: 0 for c in competitors}
    
    for item in results_data:
        # Combine text from both models for searching
        content = (item.get('gemini', '') + " " + item.get('gpt', ''))
        
        for competitor in competitors:
            brand_name = competitor['name']
            keywords = competitor['keywords']
            
            for kw in keywords:
                # Count total occurrences of ALL keywords for that brand.
                count = content.count(kw)
                stats[brand_name] += count
                
    return stats
