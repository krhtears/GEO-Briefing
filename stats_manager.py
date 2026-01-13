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
    Logic: 
    - 1 count per question for the same keyword.
    - If "Keyword A" appears 5 times in one question's answer, it counts as 1.
    
    results_data: List of dicts [{'gemini': '...', 'gpt': '...'}, ...]
    Returns: Dict {
        BrandName: {
            "count": int (Total),
            "details": {Keyword: int (Count)}
        }
    }
    """
    competitors = load_competitors()
    
    # Initialize Structure
    stats = {}
    for c in competitors:
        stats[c['name']] = {
            "count": 0,
            "details": {k: 0 for k in c['keywords']}
        }
    
    for item in results_data:
        # Combine text from both models for searching
        content = (item.get('gemini', '') + " " + item.get('gpt', ''))
        
        for competitor in competitors:
            brand_name = competitor['name']
            keywords = competitor['keywords']
            
            for kw in keywords:
                # Unique count per question: Check existence only
                if kw in content:
                    stats[brand_name]["count"] += 1
                    stats[brand_name]["details"][kw] += 1
                
    return stats
