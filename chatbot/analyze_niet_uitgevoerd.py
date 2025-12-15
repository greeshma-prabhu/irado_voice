#!/usr/bin/env python3
"""
Script to analyze the 'Niet uitgevoerd' entries
"""

import csv
from collections import Counter, defaultdict
import re

def analyze_niet_uitgevoerd(csv_file):
    """
    Analyze the 'Niet uitgevoerd' entries
    """
    print(f"Analyzing 'Niet uitgevoerd' entries in {csv_file}...")
    
    # Statistics
    total_entries = 0
    reden_counter = Counter()
    commentaar_counter = Counter()
    naam_counter = Counter()
    
    # Pattern analysis
    common_reasons = []
    common_comments = []
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            total_entries += 1
            
            naam = row.get('naam', '').strip()
            reden = row.get('niet_uitgevoerd_reden', '').strip()
            commentaar = row.get('niet_uitgevoerd_commentaar', '').strip()
            artikelen = row.get('artikelen', '').strip()
            
            # Count reasons
            if reden:
                reden_counter[reden] += 1
                common_reasons.append(reden)
            
            # Count comments
            if commentaar:
                commentaar_counter[commentaar] += 1
                common_comments.append(commentaar)
            
            # Count names
            if naam:
                naam_counter[naam] += 1
    
    print(f"\n📊 ALGEMENE STATISTIEKEN:")
    print("=" * 50)
    print(f"Totaal 'Niet uitgevoerd' entries: {total_entries:,}")
    print(f"Unieke redenen: {len(reden_counter)}")
    print(f"Unieke commentaren: {len(commentaar_counter)}")
    print(f"Unieke namen: {len(naam_counter)}")
    
    # Top reasons
    print(f"\n🔍 TOP 15 MEEST VOORKOMENDE REDENEN:")
    print("-" * 50)
    
    top_reasons = reden_counter.most_common(15)
    for i, (reason, count) in enumerate(top_reasons, 1):
        percentage = (count / total_entries) * 100
        print(f"{i:2d}. {reason:<40} - {count:4d}x ({percentage:.1f}%)")
    
    # Top comments
    print(f"\n💬 TOP 15 MEEST VOORKOMENDE COMMENTAREN:")
    print("-" * 50)
    
    top_comments = commentaar_counter.most_common(15)
    for i, (comment, count) in enumerate(top_comments, 1):
        percentage = (count / total_entries) * 100
        print(f"{i:2d}. {comment:<40} - {count:4d}x ({percentage:.1f}%)")
    
    # Top names with most 'Niet uitgevoerd' entries
    print(f"\n👥 TOP 15 NAMEN MET MEESTE 'NIET UITGEVOERD' ENTRIES:")
    print("-" * 50)
    
    top_names = naam_counter.most_common(15)
    for i, (name, count) in enumerate(top_names, 1):
        percentage = (count / total_entries) * 100
        print(f"{i:2d}. {name:<30} - {count:3d}x ({percentage:.1f}%)")
    
    # Pattern analysis
    print(f"\n🔍 PATROON ANALYSE:")
    print("-" * 30)
    
    # Analyze common patterns in reasons
    reason_patterns = {
        'nb': 0,
        'niet buiten': 0,
        'niet bereikbaar': 0,
        'niet aangeboden': 0,
        'niet goed aangeboden': 0,
        'grofvuil': 0,
        'ijzer': 0,
        'einde dienst': 0,
        'niets aangetroffen': 0,
        'niet op de juiste plek': 0
    }
    
    for reason in common_reasons:
        reason_lower = reason.lower()
        for pattern, count in reason_patterns.items():
            if pattern in reason_lower:
                reason_patterns[pattern] += 1
    
    print("Meest voorkomende patronen in redenen:")
    for pattern, count in sorted(reason_patterns.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            percentage = (count / total_entries) * 100
            print(f"• {pattern:<25} - {count:4d}x ({percentage:.1f}%)")
    
    # Time pattern analysis
    print(f"\n⏰ TIJD PATRONEN:")
    print("-" * 20)
    
    time_patterns = Counter()
    for comment in common_comments:
        # Look for time patterns like "08:30", "13:45", etc.
        time_matches = re.findall(r'\d{1,2}:\d{2}', comment)
        for time_match in time_matches:
            time_patterns[time_match] += 1
    
    if time_patterns:
        print("Meest voorkomende tijden in commentaren:")
        for time, count in time_patterns.most_common(10):
            print(f"• {time:<10} - {count:3d}x")
    
    # Show some examples
    print(f"\n📋 VOORBEELDEN VAN 'NIET UITGEVOERD' ENTRIES:")
    print("-" * 50)
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i, row in enumerate(reader):
            if i >= 10:  # Show only first 10 examples
                break
                
            naam = row.get('naam', '').strip()
            reden = row.get('niet_uitgevoerd_reden', '').strip()
            commentaar = row.get('niet_uitgevoerd_commentaar', '').strip()
            artikelen = row.get('artikelen', '').strip()
            
            print(f"{i+1:2d}. {naam}")
            print(f"    Artikelen: {artikelen}")
            print(f"    Reden: {reden}")
            print(f"    Commentaar: {commentaar}")
            print()

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_niet_uitgevoerd.csv"
    analyze_niet_uitgevoerd(csv_file)
