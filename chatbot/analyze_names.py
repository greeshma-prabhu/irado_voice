#!/usr/bin/env python3
"""
Script to analyze the most common names in the CSV and what items they have
"""

import csv
from collections import Counter, defaultdict
import re

def clean_name(name):
    """
    Clean and normalize names for better matching
    """
    if not name or name.strip() == '':
        return None
    
    # Remove extra whitespace and convert to lowercase for comparison
    cleaned = name.strip().lower()
    
    # Remove common prefixes
    prefixes_to_remove = ['dhr.', 'mevr.', 'meneer', 'mevrouw', 'dhr', 'mevr']
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    
    return cleaned

def analyze_names(csv_file):
    """
    Analyze the most common names and their items
    """
    print(f"Analyzing {csv_file}...")
    
    name_counter = Counter()
    name_items = defaultdict(list)
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            naam = row.get('naam', '').strip()
            artikelen = row.get('artikelen', '').strip()
            
            if naam and naam != '':
                cleaned_name = clean_name(naam)
                if cleaned_name:
                    name_counter[cleaned_name] += 1
                    
                    if artikelen and artikelen != '':
                        # Clean up the items description
                        items_clean = artikelen.replace(';', ', ').strip()
                        name_items[cleaned_name].append(items_clean)
    
    print(f"\n📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    # Get top 5 names
    top_5_names = name_counter.most_common(5)
    
    print(f"\n🏆 TOP 5 MEEST VOORKOMENDE NAMEN:")
    print("-" * 40)
    
    for i, (name, count) in enumerate(top_5_names, 1):
        print(f"{i}. {name.title()} - {count} keer")
    
    print(f"\n📦 ARTIKELEN PER NAAM:")
    print("=" * 50)
    
    for i, (name, count) in enumerate(top_5_names, 1):
        print(f"\n{i}. {name.title()} ({count} entries):")
        print("-" * 30)
        
        # Get all items for this name
        all_items = name_items[name]
        
        if all_items:
            # Count item frequency
            item_counter = Counter()
            for items in all_items:
                # Split items and count each
                item_list = [item.strip() for item in items.split(',') if item.strip()]
                for item in item_list:
                    if item:
                        item_counter[item] += 1
            
            # Show most common items
            print("   Meest voorkomende artikelen:")
            for item, freq in item_counter.most_common(10):
                print(f"   • {item} ({freq}x)")
            
            # Show some examples of full entries
            print(f"\n   Voorbeelden van entries:")
            for j, items in enumerate(all_items[:3], 1):
                print(f"   {j}. {items}")
            
            if len(all_items) > 3:
                print(f"   ... en {len(all_items) - 3} meer entries")
        else:
            print("   Geen artikelen gevonden")
    
    # Additional statistics
    print(f"\n📈 ALGEMENE STATISTIEKEN:")
    print("-" * 30)
    print(f"Totaal aantal unieke namen: {len(name_counter)}")
    print(f"Totaal aantal entries: {sum(name_counter.values())}")
    
    # Show some interesting patterns
    print(f"\n🔍 INTERESSANTE PATRONEN:")
    print("-" * 30)
    
    # Names with most variety in items
    name_variety = [(name, len(set(name_items[name]))) for name, _ in top_5_names]
    name_variety.sort(key=lambda x: x[1], reverse=True)
    
    print("Namen met meeste variatie in artikelen:")
    for name, variety in name_variety[:3]:
        print(f"• {name.title()}: {variety} verschillende soorten artikelen")

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_final.csv"
    analyze_names(csv_file)
