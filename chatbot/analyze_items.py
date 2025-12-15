#!/usr/bin/env python3
"""
Script to analyze the most common items in the CSV
"""

import csv
from collections import Counter
import re

def clean_item(item):
    """
    Clean and normalize item names
    """
    if not item or item.strip() == '':
        return None
    
    # Clean up the item
    cleaned = item.strip().lower()
    
    # Remove common prefixes/suffixes
    cleaned = re.sub(r'^(diverse|diversen|etc|enz|\.\.\.)', '', cleaned)
    cleaned = re.sub(r'(diverse|diversen|etc|enz|\.\.\.)$', '', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned if cleaned else None

def analyze_items(csv_file):
    """
    Analyze the most common items
    """
    print(f"Analyzing items in {csv_file}...")
    
    item_counter = Counter()
    total_entries = 0
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            artikelen = row.get('artikelen', '').strip()
            total_entries += 1
            
            if artikelen and artikelen != '':
                # Split by common separators
                items = re.split(r'[,;]', artikelen)
                
                for item in items:
                    cleaned_item = clean_item(item)
                    if cleaned_item and len(cleaned_item) > 2:  # Filter out very short items
                        item_counter[cleaned_item] += 1
    
    print(f"\n📦 MEEST VOORKOMENDE ARTIKELEN:")
    print("=" * 50)
    
    # Get top 20 items
    top_items = item_counter.most_common(20)
    
    for i, (item, count) in enumerate(top_items, 1):
        percentage = (count / total_entries) * 100
        print(f"{i:2d}. {item.title():<30} - {count:4d}x ({percentage:.1f}%)")
    
    print(f"\n📈 STATISTIEKEN:")
    print("-" * 30)
    print(f"Totaal aantal entries: {total_entries:,}")
    print(f"Unieke artikelen: {len(item_counter):,}")
    print(f"Meest voorkomende item: '{top_items[0][0]}' ({top_items[0][1]}x)")
    
    # Categories analysis
    print(f"\n🏷️  CATEGORIEËN:")
    print("-" * 30)
    
    categories = {
        'Meubels': ['kast', 'tafel', 'stoel', 'bank', 'dressoir', 'bureau', 'salontafel', 'eettafel'],
        'Elektronica': ['tv', 'koelkast', 'wasmachine', 'oven', 'droger', 'vaatwasser', 'computer'],
        'Bed & Matras': ['matras', 'bed', 'boxspring', 'topper'],
        'Hout': ['hout', 'planken', 'houten'],
        'Diverse': ['diverse', 'diversen', 'huisraad', 'spullen']
    }
    
    for category, keywords in categories.items():
        count = 0
        for item, freq in item_counter.items():
            if any(keyword in item for keyword in keywords):
                count += freq
        
        percentage = (count / total_entries) * 100
        print(f"{category:<15}: {count:4d}x ({percentage:.1f}%)")

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_final.csv"
    analyze_items(csv_file)
