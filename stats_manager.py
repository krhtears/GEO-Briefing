
BRAND_KEYWORDS = {
    "메가스터디교육": ["엠베스트", "엘리하이", "엘리하이키즈"],
    "밀크T": ["밀크티", "밀크T", "밀크T초등", "밀크T중등", "밀크T아이", "밀크티초등", "밀크티아이", "밀크티유아", "천재교과서"],
    "홈런": ["아이스크림홈런", "홈런초등", "홈런중등", "홈런유아", "아이스크림에듀", "아이스크림"],
    "비상": ["온리원", "온리원초등", "온리원중등", "온리원키즈", "온리원유아"],
    "웅진": ["웅진씽크빅", "스마트올", "스마트올초등", "스마트올중학", "스마트올중등"],
    "윙크": ["윙크"]
}

BRAND_ORDER = ["메가스터디교육", "밀크T", "홈런", "웅진", "비상", "윙크"]

def calculate_stats(results_data):
    """
    Counts references to brands in the briefing results.
    results_data: List of dicts [{'gemini': '...', 'gpt': '...'}, ...]
    Returns: Dict {BrandName: Count}
    """
    stats = {brand: 0 for brand in BRAND_ORDER}
    
    for item in results_data:
        # Combine text from both models for searching
        # Converting to lowercase for case-insensitive matching if needed, 
        # though Korean keywords usually don't need case normalization as much as English.
        # But '밀크T' has English, so let's check exact matches or just simple inclusion.
        # Simple inclusion is requested: "단어가 포함되면"
        
        content = (item.get('gemini', '') + " " + item.get('gpt', ''))
        
        for brand, keywords in BRAND_KEYWORDS.items():
            for kw in keywords:
                # Count occurrences? Or just binary "mentioned"? 
                # User said "언급되는 횟수" (number of times mentioned).
                # So we count total occurrences of ALL keywords for that brand.
                count = content.count(kw)
                stats[brand] += count
                
    return stats
