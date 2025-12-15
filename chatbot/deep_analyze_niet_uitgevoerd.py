#!/usr/bin/env python3
"""
Deep analysis of 'Niet uitgevoerd' entries with advanced pattern recognition
"""

import csv
from collections import Counter, defaultdict
import re
from datetime import datetime

def deep_analyze_niet_uitgevoerd(csv_file):
    """
    Deep analysis of 'Niet uitgevoerd' entries
    """
    print(f"🔍 DEEP ANALYSIS of 'Niet uitgevoerd' entries in {csv_file}...")
    
    # Data structures for analysis
    entries = []
    name_stats = defaultdict(lambda: {'total': 0, 'niet_uitgevoerd': 0, 'reasons': Counter(), 'times': []})
    time_patterns = defaultdict(int)
    reason_patterns = Counter()
    comment_patterns = Counter()
    artikel_patterns = Counter()
    
    # Read all data first
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            entry = {
                'naam': row.get('naam', '').strip(),
                'artikelen': row.get('artikelen', '').strip(),
                'reden': row.get('niet_uitgevoerd_reden', '').strip(),
                'commentaar': row.get('niet_uitgevoerd_commentaar', '').strip(),
                'datum_melding': row.get('datum_melding', '').strip(),
                'datum_uitgevoerd': row.get('datum_uitgevoerd', '').strip(),
                'telefoonnummer': row.get('telefoonnummer', '').strip()
            }
            entries.append(entry)
    
    print(f"📊 LOADED {len(entries):,} 'Niet uitgevoerd' entries for analysis")
    
    # 1. REASON ANALYSIS
    print(f"\n🔍 DETAILED REASON ANALYSIS:")
    print("=" * 60)
    
    for entry in entries:
        if entry['reden']:
            reason_patterns[entry['reden']] += 1
    
    # Categorize reasons
    reason_categories = {
        'nb_variations': 0,
        'niets_aangetroffen': 0,
        'niet_buiten': 0,
        'grofvuil': 0,
        'niet_aangeboden': 0,
        'kraanwagen': 0,
        'niet_bereikbaar': 0,
        'ijzer': 0,
        'einde_dienst': 0,
        'other': 0
    }
    
    for reason, count in reason_patterns.items():
        reason_lower = reason.lower()
        if 'nb' in reason_lower and 'staat niet buiten' not in reason_lower:
            reason_categories['nb_variations'] += count
        elif 'niets aangetroffen' in reason_lower:
            reason_categories['niets_aangetroffen'] += count
        elif 'niet buiten' in reason_lower or 'staat niet buiten' in reason_lower:
            reason_categories['niet_buiten'] += count
        elif 'grofvuil' in reason_lower:
            reason_categories['grofvuil'] += count
        elif 'niet aangeboden' in reason_lower:
            reason_categories['niet_aangeboden'] += count
        elif 'kraanwagen' in reason_lower:
            reason_categories['kraanwagen'] += count
        elif 'niet bereikbaar' in reason_lower:
            reason_categories['niet_bereikbaar'] += count
        elif 'ijzer' in reason_lower:
            reason_categories['ijzer'] += count
        elif 'einde dienst' in reason_lower:
            reason_categories['einde_dienst'] += count
        else:
            reason_categories['other'] += count
    
    print("Reason categories:")
    total_reasons = sum(reason_categories.values())
    for category, count in sorted(reason_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_reasons) * 100
        print(f"• {category.replace('_', ' ').title():<20} - {count:5d}x ({percentage:5.1f}%)")
    
    # 2. TIME ANALYSIS
    print(f"\n⏰ TIME PATTERN ANALYSIS:")
    print("=" * 40)
    
    for entry in entries:
        if entry['commentaar']:
            # Extract times from comments
            times = re.findall(r'\d{1,2}:\d{2}', entry['commentaar'])
            for time in times:
                time_patterns[time] += 1
    
    # Analyze time patterns
    morning_times = [time for time in time_patterns.keys() if time.startswith('08:') or time.startswith('09:')]
    late_morning = [time for time in time_patterns.keys() if time.startswith('10:') or time.startswith('11:')]
    afternoon = [time for time in time_patterns.keys() if time.startswith('12:') or time.startswith('13:') or time.startswith('14:')]
    
    print(f"Morning (08:xx-09:xx): {sum(time_patterns[t] for t in morning_times):4d} entries")
    print(f"Late morning (10:xx-11:xx): {sum(time_patterns[t] for t in late_morning):4d} entries")
    print(f"Afternoon (12:xx-14:xx): {sum(time_patterns[t] for t in afternoon):4d} entries")
    
    print(f"\nTop 20 most problematic times:")
    for time, count in Counter(time_patterns).most_common(20):
        print(f"• {time:<8} - {count:3d}x")
    
    # 3. NAME ANALYSIS
    print(f"\n👥 NAME ANALYSIS:")
    print("=" * 30)
    
    name_failure_rates = {}
    for entry in entries:
        if entry['naam']:
            name_failure_rates[entry['naam']] = name_failure_rates.get(entry['naam'], 0) + 1
    
    # Find names with highest failure rates
    top_failing_names = Counter(name_failure_rates).most_common(20)
    
    print("Names with most 'Niet uitgevoerd' entries:")
    for i, (name, count) in enumerate(top_failing_names, 1):
        print(f"{i:2d}. {name:<30} - {count:3d}x")
    
    # 4. ARTIKEL ANALYSIS
    print(f"\n📦 ARTIKEL ANALYSIS:")
    print("=" * 30)
    
    for entry in entries:
        if entry['artikelen']:
            # Split and clean artikelen
            items = [item.strip() for item in entry['artikelen'].split(',') if item.strip()]
            for item in items:
                if item:
                    artikel_patterns[item.lower()] += 1
    
    print("Most problematic items (most 'Niet uitgevoerd'):")
    for item, count in artikel_patterns.most_common(15):
        print(f"• {item:<30} - {count:3d}x")
    
    # 5. CORRELATION ANALYSIS
    print(f"\n🔗 CORRELATION ANALYSIS:")
    print("=" * 40)
    
    # Analyze correlations between reasons and times
    reason_time_correlations = defaultdict(lambda: defaultdict(int))
    
    for entry in entries:
        if entry['reden'] and entry['commentaar']:
            times = re.findall(r'\d{1,2}:\d{2}', entry['commentaar'])
            for time in times:
                reason_time_correlations[entry['reden']][time] += 1
    
    print("Reason-Time correlations (top 10):")
    for reason, times in sorted(reason_time_correlations.items(), 
                               key=lambda x: sum(x[1].values()), reverse=True)[:10]:
        total = sum(times.values())
        print(f"\n{reason} (total: {total}):")
        for time, count in sorted(times.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {time:<8} - {count:3d}x")
    
    # 6. SEASONAL ANALYSIS
    print(f"\n📅 SEASONAL ANALYSIS:")
    print("=" * 30)
    
    monthly_stats = defaultdict(int)
    for entry in entries:
        if entry['datum_melding']:
            try:
                # Extract month from date
                date_obj = datetime.strptime(entry['datum_melding'], '%Y-%m-%d %H:%M:%S')
                month = date_obj.strftime('%Y-%m')
                monthly_stats[month] += 1
            except:
                pass
    
    print("Monthly distribution of 'Niet uitgevoerd' entries:")
    for month, count in sorted(monthly_stats.items()):
        print(f"• {month:<10} - {count:4d}x")
    
    # 7. PATTERN RECOGNITION
    print(f"\n🧠 PATTERN RECOGNITION:")
    print("=" * 40)
    
    # Find recurring patterns
    patterns = {
        'same_reason_multiple_times': 0,
        'same_time_multiple_times': 0,
        'same_name_multiple_times': 0,
        'empty_artikelen': 0,
        'phone_number_in_artikelen': 0
    }
    
    for entry in entries:
        if entry['reden'] and 'nb' in entry['reden'].lower():
            patterns['same_reason_multiple_times'] += 1
        
        if not entry['artikelen'] or entry['artikelen'].strip() == '':
            patterns['empty_artikelen'] += 1
        
        if re.search(r'\d{10,}', entry['artikelen']):  # Phone number pattern
            patterns['phone_number_in_artikelen'] += 1
    
    print("Pattern analysis:")
    for pattern, count in patterns.items():
        percentage = (count / len(entries)) * 100
        print(f"• {pattern.replace('_', ' ').title():<30} - {count:4d}x ({percentage:4.1f}%)")
    
    # 8. DETAILED EXAMPLES
    print(f"\n📋 DETAILED EXAMPLES BY CATEGORY:")
    print("=" * 50)
    
    # Show examples for each major reason category
    examples_by_reason = defaultdict(list)
    for entry in entries:
        if entry['reden']:
            reason_lower = entry['reden'].lower()
            if 'nb' in reason_lower and 'staat niet buiten' not in reason_lower:
                examples_by_reason['nb_variations'].append(entry)
            elif 'niets aangetroffen' in reason_lower:
                examples_by_reason['niets_aangetroffen'].append(entry)
            elif 'niet buiten' in reason_lower:
                examples_by_reason['niet_buiten'].append(entry)
    
    for category, examples in examples_by_reason.items():
        if examples:
            print(f"\n{category.replace('_', ' ').title()} examples:")
            for i, example in enumerate(examples[:5], 1):
                print(f"{i}. {example['naam']}: {example['artikelen']}")
                print(f"   Reden: {example['reden']}")
                print(f"   Commentaar: {example['commentaar']}")
                print()

if __name__ == "__main__":
    csv_file = "/opt/irado/chatbot/bali_niet_uitgevoerd.csv"
    deep_analyze_niet_uitgevoerd(csv_file)
