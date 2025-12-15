#!/usr/bin/env python3
"""
Script to analyze the most common FULL names in the CSV (not initials)
"""

import csv
from collections import Counter, defaultdict
import re

def clean_full_name(name):
    """
    Clean and normalize full names, filtering out initials and short names
    """
    if not name or name.strip() == '':
        return None
    
    # Remove extra whitespace
    cleaned = name.strip()
    
    # Remove common prefixes
    prefixes_to_remove = ['dhr.', 'mevr.', 'meneer', 'mevrouw', 'dhr', 'mevr']
    for prefix in prefixes_to_remove:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
    
    # Filter out initials and very short names (less than 3 characters)
    if len(cleaned) < 3:
        return None
    
    # Filter out single letters or common initials
    if cleaned in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
        return None
    
    # Filter out names that are just numbers or special characters
    if re.match(r'^[0-9\s\.\-_]+$', cleaned):
        return None
    
    # Filter out names that are clearly not real names
    if any(word in cleaned.lower() for word in ['email', '@', 'www', 'http', 'com', 'nl', 'org']):
        return None
    
    return cleaned

def analyze_full_names(csv_file):
    """
    Analyze the most common full names and their items
    """
    print(f"Analyzing FULL names in {csv_file}...")
    
    name_counter = Counter()
    name_items = defaultdict(list)
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            naam = row.get('naam', '').strip()
            artikelen = row.get('artikelen', '').strip()
            
            if naam and naam != '':
                cleaned_name = clean_full_name(naam)
                if cleaned_name:
                    name_counter[cleaned_name] += 1
                    
                    if artikelen and artikelen != '':
                        # Clean up the items description
                        items_clean = artikelen.replace(';', ', ').strip()
                        name_items[cleaned_name].append(items_clean)
    
    print(f"\n📊 ANALYSIS RESULTS - FULL NAMES ONLY")
    print("=" * 60)
    
    # Get top 10 full names
    top_10_names = name_counter.most_common(10)
    
    print(f"\n🏆 TOP 10 MEEST VOORKOMENDE VOLLEDIGE NAMEN:")
    print("-" * 50)
    
    for i, (name, count) in enumerate(top_10_names, 1):
        print(f"{i:2d}. {name:<30} - {count:3d} keer")
    
    print(f"\n📦 ARTIKELEN PER NAAM:")
    print("=" * 60)
    
    for i, (name, count) in enumerate(top_10_names, 1):
        print(f"\n{i:2d}. {name} ({count} entries):")
        print("-" * 40)
        
        # Get all items for this name
        all_items = name_items[name]
        
        if all_items:
            # Count item frequency
            item_counter = Counter()
            for items in all_items:
                # Split items and count each
                item_list = [item.strip() for item in items.split(',') if item.strip()]
                for item in item_list:
                    if item and len(item) > 2:  # Filter out very short items
                        item_counter[item] += 1
            
            # Show most common items
            print("   Meest voorkomende artikelen:")
            for item, freq in item_counter.most_common(8):
                print(f"   • {item:<25} ({freq}x)")
            
            # Show some examples of full entries
            print(f"\n   Voorbeelden van entries:")
            for j, items in enumerate(all_items[:3], 1):
                if len(items) > 80:
                    items = items[:77] + "..."
                print(f"   {j}. {items}")
            
            if len(all_items) > 3:
                print(f"   ... en {len(all_items) - 3} meer entries")
        else:
            print("   Geen artikelen gevonden")
    
    # Additional statistics
    print(f"\n📈 ALGEMENE STATISTIEKEN:")
    print("-" * 40)
    print(f"Totaal aantal unieke volledige namen: {len(name_counter):,}")
    print(f"Totaal aantal entries: {sum(name_counter.values()):,}")
    
    # Show some interesting patterns
    print(f"\n🔍 INTERESSANTE PATRONEN:")
    print("-" * 40)
    
    # Names with most variety in items
    name_variety = [(name, len(set(name_items[name]))) for name, _ in top_10_names]
    name_variety.sort(key=lambda x: x[1], reverse=True)
    
    print("Namen met meeste variatie in artikelen:")
    for name, variety in name_variety[:5]:
        print(f"• {name}: {variety} verschillende soorten artikelen")
    
    # Show some unique names
    print(f"\n🎯 UNIEKE NAMEN (1x voorkomend):")
    unique_names = [name for name, count in name_counter.items() if count == 1]
    print(f"Aantal unieke namen: {len(unique_names):,}")
    
    if unique_names:
        print("Voorbeelden van unieke namen:")
        for name in unique_names[:10]:
            print(f"• {name}")

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_final.csv"
    analyze_full_names(csv_file)
