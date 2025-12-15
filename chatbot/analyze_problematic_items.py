#!/usr/bin/env python3
"""
Analyze why specific items are most problematic (most 'Niet uitgevoerd')
"""

import csv
from collections import Counter, defaultdict
import re

def analyze_problematic_items(csv_file):
    """
    Analyze why specific items are most problematic
    """
    print(f"🔍 ANALYZING PROBLEMATIC ITEMS in {csv_file}...")
    
    # Top 5 most problematic items from previous analysis
    problematic_items = ['matras', 'hout', 'wasmachine', 'koelkast', 'laminaat']
    
    # Data structures for analysis
    item_analysis = {}
    
    for item in problematic_items:
        item_analysis[item] = {
            'total_entries': 0,
            'niet_uitgevoerd_entries': 0,
            'reasons': Counter(),
            'comments': Counter(),
            'names': Counter(),
            'times': Counter(),
            'examples': []
        }
    
    # Read all data
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            artikelen = row.get('artikelen', '').strip().lower()
            reden = row.get('niet_uitgevoerd_reden', '').strip()
            commentaar = row.get('niet_uitgevoerd_commentaar', '').strip()
            naam = row.get('naam', '').strip()
            
            # Check if this entry contains any of our problematic items
            for item in problematic_items:
                if item in artikelen:
                    item_analysis[item]['total_entries'] += 1
                    
                    # If it's a 'Niet uitgevoerd' entry, analyze it
                    if reden and 'Niet uitgevoerd' in reden:
                        item_analysis[item]['niet_uitgevoerd_entries'] += 1
                        item_analysis[item]['reasons'][reden] += 1
                        item_analysis[item]['comments'][commentaar] += 1
                        item_analysis[item]['names'][naam] += 1
                        
                        # Extract time from comment
                        if commentaar:
                            times = re.findall(r'\d{1,2}:\d{2}', commentaar)
                            for time in times:
                                item_analysis[item]['times'][time] += 1
                        
                        # Store examples
                        if len(item_analysis[item]['examples']) < 10:
                            item_analysis[item]['examples'].append({
                                'naam': naam,
                                'artikelen': row.get('artikelen', ''),
                                'reden': reden,
                                'commentaar': commentaar
                            })
    
    # Analyze each problematic item
    for item in problematic_items:
        analysis = item_analysis[item]
        
        print(f"\n🔍 ANALYSIS FOR: {item.upper()}")
        print("=" * 60)
        
        print(f"📊 STATISTICS:")
        print(f"• Total entries with '{item}': {analysis['total_entries']:,}")
        print(f"• 'Niet uitgevoerd' entries: {analysis['niet_uitgevoerd_entries']:,}")
        
        if analysis['total_entries'] > 0:
            failure_rate = (analysis['niet_uitgevoerd_entries'] / analysis['total_entries']) * 100
            print(f"• Failure rate: {failure_rate:.1f}%")
        
        print(f"\n🔍 TOP REASONS FOR '{item.upper()}' NOT BEING EXECUTED:")
        print("-" * 50)
        
        for reason, count in analysis['reasons'].most_common(10):
            percentage = (count / analysis['niet_uitgevoerd_entries']) * 100 if analysis['niet_uitgevoerd_entries'] > 0 else 0
            print(f"• {reason:<40} - {count:3d}x ({percentage:4.1f}%)")
        
        print(f"\n👥 TOP NAMES WITH '{item.upper()}' PROBLEMS:")
        print("-" * 40)
        
        for name, count in analysis['names'].most_common(10):
            print(f"• {name:<30} - {count:2d}x")
        
        print(f"\n⏰ TOP TIMES WHEN '{item.upper()}' FAILS:")
        print("-" * 40)
        
        for time, count in analysis['times'].most_common(10):
            print(f"• {time:<8} - {count:2d}x")
        
        print(f"\n📋 EXAMPLES OF '{item.upper()}' FAILURES:")
        print("-" * 50)
        
        for i, example in enumerate(analysis['examples'][:5], 1):
            print(f"{i}. {example['naam']}: {example['artikelen']}")
            print(f"   Reden: {example['reden']}")
            print(f"   Commentaar: {example['commentaar']}")
            print()
    
    # Comparative analysis
    print(f"\n📊 COMPARATIVE ANALYSIS:")
    print("=" * 60)
    
    print("Failure rates by item:")
    for item in problematic_items:
        analysis = item_analysis[item]
        if analysis['total_entries'] > 0:
            failure_rate = (analysis['niet_uitgevoerd_entries'] / analysis['total_entries']) * 100
            print(f"• {item:<15} - {failure_rate:5.1f}% ({analysis['niet_uitgevoerd_entries']:3d}/{analysis['total_entries']:3d})")
    
    # Common patterns across all problematic items
    print(f"\n🔍 COMMON PATTERNS ACROSS ALL PROBLEMATIC ITEMS:")
    print("-" * 60)
    
    all_reasons = Counter()
    all_times = Counter()
    
    for item in problematic_items:
        analysis = item_analysis[item]
        for reason, count in analysis['reasons'].items():
            all_reasons[reason] += count
        for time, count in analysis['times'].items():
            all_times[time] += count
    
    print("Most common reasons across all problematic items:")
    for reason, count in all_reasons.most_common(10):
        print(f"• {reason:<40} - {count:3d}x")
    
    print(f"\nMost common failure times across all problematic items:")
    for time, count in all_times.most_common(10):
        print(f"• {time:<8} - {count:2d}x")
    
    # Specific item characteristics
    print(f"\n🎯 SPECIFIC ITEM CHARACTERISTICS:")
    print("-" * 50)
    
    for item in problematic_items:
        analysis = item_analysis[item]
        
        print(f"\n{item.upper()} characteristics:")
        
        # Check for specific patterns
        nb_count = sum(count for reason, count in analysis['reasons'].items() if 'nb' in reason.lower())
        niets_count = sum(count for reason, count in analysis['reasons'].items() if 'niets aangetroffen' in reason.lower())
        buiten_count = sum(count for reason, count in analysis['reasons'].items() if 'niet buiten' in reason.lower())
        grofvuil_count = sum(count for reason, count in analysis['reasons'].items() if 'grofvuil' in reason.lower())
        
        print(f"• 'nb' reasons: {nb_count} ({nb_count/analysis['niet_uitgevoerd_entries']*100:.1f}%)")
        print(f"• 'niets aangetroffen': {niets_count} ({niets_count/analysis['niet_uitgevoerd_entries']*100:.1f}%)")
        print(f"• 'niet buiten': {buiten_count} ({buiten_count/analysis['niet_uitgevoerd_entries']*100:.1f}%)")
        print(f"• 'grofvuil': {grofvuil_count} ({grofvuil_count/analysis['niet_uitgevoerd_entries']*100:.1f}%)")

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_niet_uitgevoerd.csv"
    analyze_problematic_items(csv_file)
