#!/usr/bin/env python3
"""
Script to filter only entries that contain 'Niet uitgevoerd' for further analysis
"""

import csv
from datetime import datetime

def filter_niet_uitgevoerd_entries(input_file, output_file):
    """
    Filter entries that contain 'Niet uitgevoerd' in any of the relevant columns
    """
    print(f"Filtering 'Niet uitgevoerd' entries from {input_file}...")
    
    filtered_count = 0
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
            niet_uitgevoerd_reden_index = header.index('niet_uitgevoerd_reden')
            niet_uitgevoerd_commentaar_index = header.index('niet_uitgevoerd_commentaar')
        except ValueError as e:
            print(f"Error: Column not found - {e}")
            return
        
        print(f"Found 'niet_uitgevoerd_reden' column at index {niet_uitgevoerd_reden_index}")
        print(f"Found 'niet_uitgevoerd_commentaar' column at index {niet_uitgevoerd_commentaar_index}")
        
        # Process each row
        for row in reader:
            total_count += 1
            
            # Check if either niet_uitgevoerd column has content
            niet_uitgevoerd_reden = row[niet_uitgevoerd_reden_index].strip() if len(row) > niet_uitgevoerd_reden_index else ''
            niet_uitgevoerd_commentaar = row[niet_uitgevoerd_commentaar_index].strip() if len(row) > niet_uitgevoerd_commentaar_index else ''
            
            # Check if either column contains 'Niet uitgevoerd'
            if 'Niet uitgevoerd' in niet_uitgevoerd_reden or 'Niet uitgevoerd' in niet_uitgevoerd_commentaar:
                writer.writerow(row)
                filtered_count += 1
            
            if total_count % 10000 == 0:
                print(f"Processed {total_count} rows, found {filtered_count} 'Niet uitgevoerd' entries...")
    
    print(f"\nFiltering complete!")
    print(f"Total rows processed: {total_count}")
    print(f"'Niet uitgevoerd' entries found: {filtered_count}")
    print(f"Percentage: {(filtered_count/total_count)*100:.1f}%")
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
    input_file = "/opt/irado/chatbot/bali_final.csv"
    output_file = "/opt/irado/chatbot/bali_niet_uitgevoerd.csv"
    
    # Create backup first
    backup_file = create_backup(input_file)
    
    # Filter the entries
    filter_niet_uitgevoerd_entries(input_file, output_file)
    
    print(f"\nOriginal file: {input_file}")
    print(f"Backup file: {backup_file}")
    print(f"Filtered file: {output_file}")
