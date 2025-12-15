#!/usr/bin/env python3
"""
Analyze top 20 most problematic items in the FULL dataset
"""

import csv
from collections import Counter, defaultdict
import re

def analyze_top20_problematic_items(csv_file):
    """
    Analyze top 20 most problematic items in the full dataset
    """
    print(f"🔍 ANALYZING TOP 20 PROBLEMATIC ITEMS in FULL DATASET: {csv_file}...")
    
    # Data structures for analysis
    item_stats = defaultdict(lambda: {
        'total_entries': 0,
        'successful_entries': 0,
        'niet_uitgevoerd_entries': 0,
        'reasons': Counter(),
        'examples': []
    })
    
    # Read all data from the full dataset
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            artikelen = row.get('artikelen', '').strip().lower()
            reden = row.get('niet_uitgevoerd_reden', '').strip()
            commentaar = row.get('niet_uitgevoerd_commentaar', '').strip()
            naam = row.get('naam', '').strip()
            
            if not artikelen:
                continue
            
            # Split artikelen into individual items
            items = [item.strip() for item in re.split(r'[,;]', artikelen) if item.strip()]
            
            for item in items:
                if len(item) > 2:  # Filter out very short items
                    item_stats[item]['total_entries'] += 1
                    
                    # Check if it's a 'Niet uitgevoerd' entry
                    if reden and 'Niet uitgevoerd' in reden:
                        item_stats[item]['niet_uitgevoerd_entries'] += 1
                        item_stats[item]['reasons'][reden] += 1
                        
                        # Store examples
                        if len(item_stats[item]['examples']) < 5:
                            item_stats[item]['examples'].append({
                                'naam': naam,
                                'artikelen': row.get('artikelen', ''),
                                'reden': reden,
                                'commentaar': commentaar
                            })
                    else:
                        # This is a successful entry
                        item_stats[item]['successful_entries'] += 1
    
    # Calculate failure rates and filter items with minimum entries
    item_failure_rates = []
    
    for item, stats in item_stats.items():
        if stats['total_entries'] >= 50:  # Minimum 50 entries to be considered
            failure_rate = (stats['niet_uitgevoerd_entries'] / stats['total_entries']) * 100
            item_failure_rates.append((item, stats, failure_rate))
    
    # Sort by failure rate (highest first)
    item_failure_rates.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n🏆 TOP 20 MEEST PROBLEMATISCHE ITEMS:")
    print("=" * 80)
    
    for i, (item, stats, failure_rate) in enumerate(item_failure_rates[:20], 1):
        success_rate = 100 - failure_rate
        print(f"{i:2d}. {item:<25} - Failure: {failure_rate:5.1f}% | Success: {success_rate:5.1f}% | Total: {stats['total_entries']:4d}")
    
    # Detailed analysis of top 20
    print(f"\n📊 DETAILED ANALYSIS OF TOP 20:")
    print("=" * 80)
    
    for i, (item, stats, failure_rate) in enumerate(item_failure_rates[:20], 1):
        print(f"\n{i:2d}. {item.upper()}")
        print("-" * 50)
        
        print(f"📈 STATISTICS:")
        print(f"• Total entries: {stats['total_entries']:,}")
        print(f"• Successful: {stats['successful_entries']:,}")
        print(f"• Failed: {stats['niet_uitgevoerd_entries']:,}")
        print(f"• Success rate: {100-failure_rate:.1f}%")
        print(f"• Failure rate: {failure_rate:.1f}%")
        
        if stats['niet_uitgevoerd_entries'] > 0:
            print(f"\n🔍 TOP REASONS FOR FAILURE:")
            for reason, count in stats['reasons'].most_common(5):
                percentage = (count / stats['niet_uitgevoerd_entries']) * 100
                print(f"• {reason:<40} - {count:3d}x ({percentage:4.1f}%)")
            
            print(f"\n📋 EXAMPLES OF FAILURES:")
            for j, example in enumerate(stats['examples'][:3], 1):
                print(f"{j}. {example['naam']}: {example['artikelen']}")
                print(f"   Reden: {example['reden']}")
                if example['commentaar']:
                    print(f"   Commentaar: {example['commentaar']}")
                print()
    
    # Summary statistics
    print(f"\n📈 SUMMARY STATISTICS:")
    print("=" * 50)
    
    total_entries = sum(stats['total_entries'] for _, stats, _ in item_failure_rates[:20])
    total_successful = sum(stats['successful_entries'] for _, stats, _ in item_failure_rates[:20])
    total_failed = sum(stats['niet_uitgevoerd_entries'] for _, stats, _ in item_failure_rates[:20])
    
    print(f"Total entries (top 20): {total_entries:,}")
    print(f"Total successful: {total_successful:,}")
    print(f"Total failed: {total_failed:,}")
    
    if total_entries > 0:
        overall_success_rate = (total_successful / total_entries) * 100
        overall_failure_rate = (total_failed / total_entries) * 100
        print(f"Overall success rate: {overall_success_rate:.1f}%")
        print(f"Overall failure rate: {overall_failure_rate:.1f}%")
    
    # Common failure reasons across top 20
    print(f"\n🔍 COMMON FAILURE REASONS ACROSS TOP 20:")
    print("-" * 50)
    
    all_reasons = Counter()
    for _, stats, _ in item_failure_rates[:20]:
        for reason, count in stats['reasons'].items():
            all_reasons[reason] += count
    
    print("Most common reasons across top 20 items:")
    for reason, count in all_reasons.most_common(10):
        print(f"• {reason:<40} - {count:3d}x")
    
    # Items with highest absolute failure numbers
    print(f"\n📊 ITEMS WITH HIGHEST ABSOLUTE FAILURE NUMBERS:")
    print("-" * 50)
    
    absolute_failures = [(item, stats['niet_uitgevoerd_entries']) for item, stats, _ in item_failure_rates]
    absolute_failures.sort(key=lambda x: x[1], reverse=True)
    
    for i, (item, failures) in enumerate(absolute_failures[:10], 1):
        print(f"{i:2d}. {item:<25} - {failures:3d} failures")
    
    # Success stories (items with lowest failure rates)
    print(f"\n✅ SUCCESS STORIES (LOWEST FAILURE RATES):")
    print("-" * 50)
    
    success_stories = [(item, stats, failure_rate) for item, stats, failure_rate in item_failure_rates if stats['total_entries'] >= 100]
    success_stories.sort(key=lambda x: x[2])  # Sort by failure rate (lowest first)
    
    for i, (item, stats, failure_rate) in enumerate(success_stories[:10], 1):
        success_rate = 100 - failure_rate
        print(f"{i:2d}. {item:<25} - Success: {success_rate:5.1f}% | Total: {stats['total_entries']:3d}")

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_final.csv"
    analyze_top20_problematic_items(csv_file)
