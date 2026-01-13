import json
import os

COMPETITORS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitors.json")

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

def calculate_stats(results_data, competitors=None):
    """
    Counts references to competitors in the briefing results.
    Logic: 
    - 1 count per question for the same keyword.
    - If "Keyword A" appears 5 times in one question's answer, it counts as 1.
    
    results_data: List of dicts [{'gemini': '...', 'gpt': '...'}, ...]
    competitors: Optional list of competitor dicts. If None, loads from file.
    Returns: Dict {
        BrandName: {
            "count": int (Total),
            "details": {Keyword: int (Count)}
        }
    }
    """
    if competitors is None:
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

def generate_trend_chart_image(history_items):
    """
    Generates a static PNG image of the trend chart using Matplotlib.
    Returns the absolute path to the generated image file.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        import pandas as pd
        import tempfile
        
        # 1. Prepare Data
        trend_data = []
        for item in reversed(history_items):
            try:
                # Use stored competitors if available, else load default
                stored_competitors = item.get('competitors', None)
                raw_stats = calculate_stats(item['data'], competitors=stored_competitors)
                stats = {k: v['count'] for k, v in raw_stats.items()}
                date_str = item['timestamp'][5:10] # MM-DD
                stats['Date'] = date_str
                trend_data.append(stats)
            except Exception:
                continue
                
        if not trend_data:
            return None
            
        df = pd.DataFrame(trend_data)
        if 'Date' not in df.columns:
            return None
            
        # 2. Plotting
        plt.figure(figsize=(10, 6))
        
        # Try to use a Korean-supporting font if available, else standard
        # Windows usually has Malgun Gothic
        font_name = "Malgun Gothic"
        plt.rc('font', family=font_name)
        plt.rc('axes', unicode_minus=False) # Fix minus sign issue
        
        # Plot each brand
        brands = [c for c in df.columns if c != 'Date']
        styles = ['-', '--', '-.', ':']
        
        for i, brand in enumerate(brands):
            style = styles[i % len(styles)]
            plt.plot(df['Date'], df[brand], label=brand, linestyle=style, marker='o')
            
        plt.title('최근 14회 브리핑 브랜드 언급량 추이')
        plt.xlabel('날짜 (MM-DD)')
        plt.ylabel('언급 횟수')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 3. Save to Temp File
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "briefing_trend_chart.png")
        plt.savefig(file_path, dpi=100)
        plt.close()
        
        return file_path
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        return None
