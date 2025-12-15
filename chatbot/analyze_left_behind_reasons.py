#!/usr/bin/env python3
"""
Analyze specific reasons why items are left behind (not picked up)
"""

import csv
from collections import Counter, defaultdict
import re

def analyze_left_behind_reasons(csv_file):
    """
    Analyze specific reasons why items are left behind
    """
    print(f"🔍 ANALYZING REASONS WHY ITEMS ARE LEFT BEHIND in {csv_file}...")
    
    # Categories of reasons for leaving items behind
    reason_categories = {
        'stolen_taken': [],  # Items that were stolen/taken by others
        'not_outside': [],   # Items not placed outside
        'too_heavy': [],     # Items too heavy for normal pickup
        'not_found': [],     # Items not found at location
        'wrong_placement': [], # Items placed incorrectly
        'technical_issues': [], # Technical/logistical issues
        'other': []          # Other reasons
    }
    
    # Keywords for each category
    stolen_keywords = ['gejat', 'gestolen', 'weggehaald', 'al weg', 'niet meer', 'verdwenen', 'opgehaald door anderen']
    not_outside_keywords = ['niet buiten', 'staat niet buiten', 'niet aangeboden', 'niet goed aangeboden']
    too_heavy_keywords = ['grofvuil', 'kraanwagen', 'te zwaar', 'te groot', 'knijpwagen', 'kraanwagen nodig']
    not_found_keywords = ['niets aangetroffen', 'niet aangetroffen', 'niet gevonden', 'niet te vinden']
    wrong_placement_keywords = ['niet op de juiste plek', 'verkeerde plek', 'niet bereikbaar', 'niet toegankelijk']
    technical_keywords = ['einde dienst', 'niet gedaan', 'n.a', 'niet bereikbaar', 'adres niet bereikbaar']
    
    # Read all data
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            reden = row.get('niet_uitgevoerd_reden', '').strip()
            commentaar = row.get('niet_uitgevoerd_commentaar', '').strip()
            artikelen = row.get('artikelen', '').strip()
            naam = row.get('naam', '').strip()
            
            if not reden or 'Niet uitgevoerd' not in reden:
                continue
            
            # Combine reden and commentaar for analysis
            full_reason = f"{reden} {commentaar}".lower()
            
            # Categorize the reason
            categorized = False
            
            # Check for stolen/taken items
            for keyword in stolen_keywords:
                if keyword in full_reason:
                    reason_categories['stolen_taken'].append({
                        'naam': naam,
                        'artikelen': artikelen,
                        'reden': reden,
                        'commentaar': commentaar,
                        'keyword': keyword
                    })
                    categorized = True
                    break
            
            if not categorized:
                # Check for not outside
                for keyword in not_outside_keywords:
                    if keyword in full_reason:
                        reason_categories['not_outside'].append({
                            'naam': naam,
                            'artikelen': artikelen,
                            'reden': reden,
                            'commentaar': commentaar,
                            'keyword': keyword
                        })
                        categorized = True
                        break
            
            if not categorized:
                # Check for too heavy
                for keyword in too_heavy_keywords:
                    if keyword in full_reason:
                        reason_categories['too_heavy'].append({
                            'naam': naam,
                            'artikelen': artikelen,
                            'reden': reden,
                            'commentaar': commentaar,
                            'keyword': keyword
                        })
                        categorized = True
                        break
            
            if not categorized:
                # Check for not found
                for keyword in not_found_keywords:
                    if keyword in full_reason:
                        reason_categories['not_found'].append({
                            'naam': naam,
                            'artikelen': artikelen,
                            'reden': reden,
                            'commentaar': commentaar,
                            'keyword': keyword
                        })
                        categorized = True
                        break
            
            if not categorized:
                # Check for wrong placement
                for keyword in wrong_placement_keywords:
                    if keyword in full_reason:
                        reason_categories['wrong_placement'].append({
                            'naam': naam,
                            'artikelen': artikelen,
                            'reden': reden,
                            'commentaar': commentaar,
                            'keyword': keyword
                        })
                        categorized = True
                        break
            
            if not categorized:
                # Check for technical issues
                for keyword in technical_keywords:
                    if keyword in full_reason:
                        reason_categories['technical_issues'].append({
                            'naam': naam,
                            'artikelen': artikelen,
                            'reden': reden,
                            'commentaar': commentaar,
                            'keyword': keyword
                        })
                        categorized = True
                        break
            
            if not categorized:
                # Other reasons
                reason_categories['other'].append({
                    'naam': naam,
                    'artikelen': artikelen,
                    'reden': reden,
                    'commentaar': commentaar,
                    'keyword': 'other'
                })
    
    # Analyze each category
    print(f"\n📊 ANALYSIS OF REASONS FOR LEAVING ITEMS BEHIND:")
    print("=" * 70)
    
    total_categorized = sum(len(items) for items in reason_categories.values())
    
    for category, items in reason_categories.items():
        if items:
            percentage = (len(items) / total_categorized) * 100
            print(f"\n🔍 {category.upper().replace('_', ' ')}: {len(items)} items ({percentage:.1f}%)")
            print("-" * 50)
            
            # Show examples
            for i, item in enumerate(items[:5], 1):
                print(f"{i}. {item['naam']}: {item['artikelen']}")
                print(f"   Reden: {item['reden']}")
                if item['commentaar']:
                    print(f"   Commentaar: {item['commentaar']}")
                print(f"   Keyword: {item['keyword']}")
                print()
            
            if len(items) > 5:
                print(f"   ... en {len(items) - 5} meer items")
    
    # Specific analysis for electrical appliances
    print(f"\n⚡ ELECTRICAL APPLIANCES LEFT BEHIND:")
    print("=" * 50)
    
    electrical_keywords = ['wasmachine', 'koelkast', 'oven', 'droger', 'vaatwasser', 'magnetron', 'stofzuiger', 'gasfornuis', 'fornuis']
    
    electrical_reasons = defaultdict(list)
    
    for category, items in reason_categories.items():
        for item in items:
            artikelen_lower = item['artikelen'].lower()
            for appliance in electrical_keywords:
                if appliance in artikelen_lower:
                    electrical_reasons[category].append(item)
    
    for category, items in electrical_reasons.items():
        if items:
            print(f"\n{category.upper().replace('_', ' ')} - Electrical appliances: {len(items)}")
            for item in items[:3]:
                print(f"• {item['naam']}: {item['artikelen']}")
                print(f"  Reden: {item['reden']}")
    
    # Analyze "nb" reasons specifically
    print(f"\n🔍 DETAILED ANALYSIS OF 'NB' REASONS:")
    print("=" * 50)
    
    nb_reasons = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            reden = row.get('niet_uitgevoerd_reden', '').strip()
            commentaar = row.get('niet_uitgevoerd_commentaar', '').strip()
            artikelen = row.get('artikelen', '').strip()
            naam = row.get('naam', '').strip()
            
            if reden and 'Niet uitgevoerd: nb' in reden:
                nb_reasons.append({
                    'naam': naam,
                    'artikelen': artikelen,
                    'reden': reden,
                    'commentaar': commentaar
                })
    
    print(f"Total 'nb' reasons: {len(nb_reasons)}")
    
    # Analyze patterns in nb reasons
    nb_patterns = {
        'with_time': 0,
        'without_time': 0,
        'electrical_appliances': 0,
        'furniture': 0,
        'other': 0
    }
    
    for item in nb_reasons:
        if item['commentaar'] and re.search(r'\d{1,2}:\d{2}', item['commentaar']):
            nb_patterns['with_time'] += 1
        else:
            nb_patterns['without_time'] += 1
        
        artikelen_lower = item['artikelen'].lower()
        if any(appliance in artikelen_lower for appliance in electrical_keywords):
            nb_patterns['electrical_appliances'] += 1
        elif any(furniture in artikelen_lower for furniture in ['kast', 'tafel', 'stoel', 'bank', 'bed']):
            nb_patterns['furniture'] += 1
        else:
            nb_patterns['other'] += 1
    
    print(f"\nNB reason patterns:")
    for pattern, count in nb_patterns.items():
        percentage = (count / len(nb_reasons)) * 100
        print(f"• {pattern.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    # Show examples of nb reasons
    print(f"\n📋 EXAMPLES OF 'NB' REASONS:")
    print("-" * 40)
    
    for i, item in enumerate(nb_reasons[:10], 1):
        print(f"{i:2d}. {item['naam']}: {item['artikelen']}")
        print(f"    Reden: {item['reden']}")
        if item['commentaar']:
            print(f"    Commentaar: {item['commentaar']}")
        print()

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_final.csv"
    analyze_left_behind_reasons(csv_file)
