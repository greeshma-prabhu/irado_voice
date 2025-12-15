#!/usr/bin/env python3
"""
Script to process the CSV file by:
1. Removing the route_omschrijving column (since it's mostly NULL)
2. Splitting the melding_informatie column into separate fields
"""

import csv
import re
import shutil
from datetime import datetime

def split_melding_informatie(text):
    """
    Split the melding_informatie field into separate components.
    Pattern: name;phone;articles;not_executed_reason;not_executed_comment;...
    """
    if not text or text.strip() == '':
        return {
            'naam': '',
            'telefoonnummer': '',
            'artikelen': '',
            'niet_uitgevoerd_reden': '',
            'niet_uitgevoerd_commentaar': '',
            'overige_info': ''
        }
    
    # Split by semicolon to get individual parts
    parts = [part.strip() for part in text.split(';')]
    
    # Initialize result dictionary
    result = {
        'naam': '',
        'telefoonnummer': '',
        'artikelen': '',
        'niet_uitgevoerd_reden': '',
        'niet_uitgevoerd_commentaar': '',
        'overige_info': ''
    }
    
    if len(parts) >= 1:
        result['naam'] = parts[0]
    
    if len(parts) >= 2:
        # Check if second part looks like a phone number
        potential_phone = parts[1]
        phone_pattern = r'^0\d{9}$'  # Dutch phone number pattern
        if re.match(phone_pattern, potential_phone):
            result['telefoonnummer'] = potential_phone
            # Articles start from index 2
            if len(parts) >= 3:
                result['artikelen'] = parts[2]
        else:
            # No phone number, articles start from index 1
            result['artikelen'] = parts[1]
    
    # Look for "Niet uitgevoerd" patterns
    niet_uitgevoerd_parts = []
    other_parts = []
    
    for i, part in enumerate(parts):
        if part.startswith('Niet uitgevoerd:'):
            niet_uitgevoerd_parts.append(part)
        elif part and not part.startswith('Niet uitgevoerd:'):
            other_parts.append(part)
    
    if niet_uitgevoerd_parts:
        result['niet_uitgevoerd_reden'] = niet_uitgevoerd_parts[0]
        if len(niet_uitgevoerd_parts) > 1:
            result['niet_uitgevoerd_commentaar'] = niet_uitgevoerd_parts[1]
    
    # Combine remaining parts as overige_info
    if other_parts:
        # Remove empty parts and join
        non_empty_parts = [p for p in other_parts if p.strip()]
        if non_empty_parts:
            result['overige_info'] = ';'.join(non_empty_parts)
    
    return result

def process_csv_file(input_file, output_file):
    """
    Process the CSV file to remove route_omschrijving and split melding_informatie.
    """
    print(f"Processing {input_file}...")
    
    processed_rows = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Process header
        header = next(reader)
        
        # Find column indices
        try:
            melding_index = header.index('melding_informatie')
            route_index = header.index('route_omschrijving')
        except ValueError as e:
            print(f"Error: Column not found - {e}")
            return
        
        # Create new header without route_omschrijving and with split melding_informatie
        new_header = []
        for i, col in enumerate(header):
            if i == route_index:
                continue  # Skip route_omschrijving
            elif i == melding_index:
                # Replace melding_informatie with split columns
                new_header.extend(['naam', 'telefoonnummer', 'artikelen', 'niet_uitgevoerd_reden', 'niet_uitgevoerd_commentaar', 'overige_info'])
            else:
                new_header.append(col)
        
        writer.writerow(new_header)
        
        print(f"Found 'melding_informatie' column at index {melding_index}")
        print(f"Found 'route_omschrijving' column at index {route_index}")
        print(f"New header: {new_header}")
        
        # Process each row
        for row in reader:
            new_row = []
            
            for i, cell in enumerate(row):
                if i == route_index:
                    continue  # Skip route_omschrijving column
                elif i == melding_index:
                    # Split melding_informatie
                    split_data = split_melding_informatie(cell)
                    new_row.extend([
                        split_data['naam'],
                        split_data['telefoonnummer'],
                        split_data['artikelen'],
                        split_data['niet_uitgevoerd_reden'],
                        split_data['niet_uitgevoerd_commentaar'],
                        split_data['overige_info']
                    ])
                else:
                    new_row.append(cell)
            
            writer.writerow(new_row)
            processed_rows += 1
            
            if processed_rows % 10000 == 0:
                print(f"Processed {processed_rows} rows...")
    
    print(f"Processing complete!")
    print(f"Total rows processed: {processed_rows}")
    print(f"Output saved to: {output_file}")

def create_backup(original_file):
    """
    Create a backup of the original file with timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{original_file}.backup_{timestamp}"
    shutil.copy2(original_file, backup_file)
    print(f"Backup created: {backup_file}")
    return backup_file

if __name__ == "__main__":
    input_file = "/opt/irado/chatbot/bali_no_emails.csv"
    output_file = "/opt/irado/chatbot/bali_final.csv"
    
    # Create backup first
    backup_file = create_backup(input_file)
    
    # Process the file
    process_csv_file(input_file, output_file)
    
    print(f"\nOriginal file: {input_file}")
    print(f"Backup file: {backup_file}")
    print(f"Processed file: {output_file}")
