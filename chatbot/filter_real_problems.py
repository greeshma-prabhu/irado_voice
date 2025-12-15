#!/usr/bin/env python3
"""
Filter out entries with 'nb', 'niet buiten' and similar reasons to keep only real problems
"""

import csv
from datetime import datetime

def filter_real_problems(input_file, output_file):
    """
    Filter out entries with 'nb', 'niet buiten' and similar reasons
    """
    print(f"Filtering real problems from {input_file}...")
    
    # Reasons to exclude (these are not real problems)
    exclude_reasons = [
        'nb',
        'niet buiten',
        'staat niet buiten',
        'niet aangeboden',
        'niet goed aangeboden',
        'n.a',
        'niet gedaan',
        'niks',
        'niet bereikbaar',
        'straat niet bereikbaar',
        'niet bereikbaar door auto',
        'adres niet bereikbaar',
        'te smal',
        'niet toegankelijk'
    ]
    
    filtered_count = 0
    excluded_count = 0
    total_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Process header
        header = next(reader)
        writer.writerow(header)
        
        # Find column indices
        try:
            reden_index = header.index('niet_uitgevoerd_reden')
            commentaar_index = header.index('niet_uitgevoerd_commentaar')
        except ValueError as e:
            print(f"Error: Column not found - {e}")
            return
        
        print(f"Found 'niet_uitgevoerd_reden' column at index {reden_index}")
        print(f"Found 'niet_uitgevoerd_commentaar' column at index {commentaar_index}")
        
        # Process each row
        for row in reader:
            total_count += 1
            
            reden = row[reden_index].strip() if len(row) > reden_index else ''
            commentaar = row[commentaar_index].strip() if len(row) > commentaar_index else ''
            
            # Check if this entry should be excluded
            should_exclude = False
            
            # Check reden
            if reden:
                reden_lower = reden.lower()
                for exclude_reason in exclude_reasons:
                    if exclude_reason in reden_lower:
                        should_exclude = True
                        break
            
            # Check commentaar
            if not should_exclude and commentaar:
                commentaar_lower = commentaar.lower()
                for exclude_reason in exclude_reasons:
                    if exclude_reason in commentaar_lower:
                        should_exclude = True
                        break
            
            if should_exclude:
                excluded_count += 1
            else:
                # This is a real problem - keep it
                writer.writerow(row)
                filtered_count += 1
            
            if total_count % 5000 == 0:
                print(f"Processed {total_count} rows, kept {filtered_count}, excluded {excluded_count}...")
    
    print(f"\nFiltering complete!")
    print(f"Total rows processed: {total_count}")
    print(f"Real problems kept: {filtered_count}")
    print(f"Excluded (nb/niet buiten/etc): {excluded_count}")
    print(f"Percentage kept: {(filtered_count/total_count)*100:.1f}%")
    print(f"Output saved to: {output_file}")

def create_backup(original_file):
    """
    Create a backup of the original file with timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{original_file}.backup_{timestamp}"
    import shutil
    shutil.copy2(original_file, backup_file)
    print(f"Backup created: {backup_file}")
    return backup_file

if __name__ == "__main__":
    input_file = "/opt/irado/chatbot/bali_niet_uitgevoerd.csv"
    output_file = "/opt/irado/chatbot/bali_real_problems.csv"
    
    # Create backup first
    backup_file = create_backup(input_file)
    
    # Filter the entries
    filter_real_problems(input_file, output_file)
    
    print(f"\nOriginal file: {input_file}")
    print(f"Backup file: {backup_file}")
    print(f"Filtered file: {output_file}")
