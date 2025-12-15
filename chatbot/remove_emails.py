#!/usr/bin/env python3
"""
Script to remove email addresses from the melding_informatie column in bali.csv
The email addresses are embedded in the data separated by semicolons.
Pattern: name;email;phone;description;...
"""

import csv
import re
import shutil
from datetime import datetime

def remove_email_from_melding_info(text):
    """
    Remove email addresses from the melding_informatie field.
    The field contains data separated by semicolons where the second field is typically an email.
    """
    if not text or text.strip() == '':
        return text
    
    # Split by semicolon to get individual parts
    parts = text.split(';')
    
    if len(parts) < 2:
        return text
    
    # Check if the second part (index 1) looks like an email
    potential_email = parts[1].strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(email_pattern, potential_email):
        # Remove the email part (second element) and rejoin
        parts.pop(1)  # Remove the email
        return ';'.join(parts)
    
    return text

def process_csv_file(input_file, output_file):
    """
    Process the CSV file to remove email addresses from melding_informatie column.
    """
    print(f"Processing {input_file}...")
    
    processed_rows = 0
    emails_removed = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Process header
        header = next(reader)
        writer.writerow(header)
        
        # Find the melding_informatie column index
        try:
            melding_index = header.index('melding_informatie')
        except ValueError:
            print("Error: 'melding_informatie' column not found!")
            return
        
        print(f"Found 'melding_informatie' column at index {melding_index}")
        
        # Process each row
        for row in reader:
            if len(row) > melding_index:
                original_text = row[melding_index]
                cleaned_text = remove_email_from_melding_info(original_text)
                
                if original_text != cleaned_text:
                    emails_removed += 1
                
                row[melding_index] = cleaned_text
            
            writer.writerow(row)
            processed_rows += 1
            
            if processed_rows % 10000 == 0:
                print(f"Processed {processed_rows} rows...")
    
    print(f"Processing complete!")
    print(f"Total rows processed: {processed_rows}")
    print(f"Emails removed: {emails_removed}")
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
    input_file = "/opt/irado/chatbot/bali.csv"
    output_file = "/opt/irado/chatbot/bali_no_emails.csv"
    
    # Create backup first
    backup_file = create_backup(input_file)
    
    # Process the file
    process_csv_file(input_file, output_file)
    
    print(f"\nOriginal file: {input_file}")
    print(f"Backup file: {backup_file}")
    print(f"Processed file: {output_file}")






