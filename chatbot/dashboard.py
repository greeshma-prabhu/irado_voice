#!/usr/bin/env python3
"""
Irado Chatbot Dashboard
Web-based dashboard for managing KOAD blacklist and system configuration
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import csv
import os
import pandas as pd
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'irado_chatbot_dashboard_secret_key_2024'

# Configuration
KOAD_FILE = '/opt/irado/chatbot/koad.csv'
BACKUP_DIR = '/opt/irado/chatbot/backups'

def ensure_backup_dir():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_backup():
    """Create backup of KOAD file"""
    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"koad_backup_{timestamp}.csv")
    
    if os.path.exists(KOAD_FILE):
        import shutil
        shutil.copy2(KOAD_FILE, backup_file)
        return backup_file
    return None

def load_koad_data():
    """Load KOAD data from CSV file"""
    try:
        df = pd.read_csv(KOAD_FILE)
        return df
    except Exception as e:
        print(f"Error loading KOAD data: {e}")
        return pd.DataFrame()

def save_koad_data(df):
    """Save KOAD data to CSV file"""
    try:
        # Create backup before saving
        create_backup()
        
        # Save the dataframe
        df.to_csv(KOAD_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving KOAD data: {e}")
        return False

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/koad')
def api_koad_list():
    """API endpoint to get KOAD list"""
    try:
        df = load_koad_data()
        
        # Convert to list of dictionaries for JSON response
        koad_list = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': koad_list,
            'total': len(koad_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/search')
def api_koad_search():
    """API endpoint to search KOAD list"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'data': [], 'total': 0})
        
        df = load_koad_data()
        
        # Search in multiple columns
        search_columns = ['KOAD-str', 'KOAD-pc', 'KOAD-huisnr', 'KOAD-naam']
        mask = df[search_columns].astype(str).apply(
            lambda x: x.str.contains(query, case=False, na=False)
        ).any(axis=1)
        
        filtered_df = df[mask]
        koad_list = filtered_df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': koad_list,
            'total': len(koad_list),
            'query': query
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/add', methods=['POST'])
def api_koad_add():
    """API endpoint to add new KOAD entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['KOAD-str', 'KOAD-pc', 'KOAD-huisnr']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Field {field} is required'
                }), 400
        
        # Load existing data
        df = load_koad_data()
        
        # Check if entry already exists
        postcode = data['KOAD-pc']
        huisnummer = data['KOAD-huisnr']
        existing = df[(df['KOAD-pc'] == postcode) & (df['KOAD-huisnr'] == huisnummer)]
        
        if not existing.empty:
            return jsonify({
                'success': False,
                'error': 'Entry already exists with this postcode and house number'
            }), 400
        
        # Add new entry
        new_entry = {
            'KOAD-nummer': data.get('KOAD-nummer', ''),
            'KOAD-str': data['KOAD-str'],
            'KOAD-pc': data['KOAD-pc'],
            'KOAD-huisaand': data.get('KOAD-huisaand', ''),
            'KOAD-huisnr': data['KOAD-huisnr'],
            'KOAD-etage': data.get('KOAD-etage', ''),
            'KOAD-naam': data.get('KOAD-naam', ''),
            'KOAD-actief': data.get('KOAD-actief', '1'),
            'KOAD-inwoner': data.get('KOAD-inwoner', '1')
        }
        
        # Add to dataframe
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        
        # Save
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': 'Entry added successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/update', methods=['POST'])
def api_koad_update():
    """API endpoint to update KOAD entry"""
    try:
        data = request.get_json()
        entry_id = data.get('id')
        
        if not entry_id:
            return jsonify({
                'success': False,
                'error': 'Entry ID is required'
            }), 400
        
        # Load existing data
        df = load_koad_data()
        
        # Update entry
        for key, value in data.items():
            if key != 'id' and key in df.columns:
                df.loc[df.index == entry_id, key] = value
        
        # Save
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': 'Entry updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/delete', methods=['POST'])
def api_koad_delete():
    """API endpoint to delete KOAD entry"""
    try:
        data = request.get_json()
        entry_id = data.get('id')
        
        if not entry_id:
            return jsonify({
                'success': False,
                'error': 'Entry ID is required'
            }), 400
        
        # Load existing data
        df = load_koad_data()
        
        # Delete entry
        df = df.drop(df.index[entry_id])
        df = df.reset_index(drop=True)
        
        # Save
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': 'Entry deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/koad/upload', methods=['POST'])
def api_koad_upload():
    """API endpoint to upload new KOAD CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'File must be a CSV file'
            }), 400
        
        # Read the uploaded file
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['KOAD-str', 'KOAD-pc', 'KOAD-huisnr']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Save the new data
        if save_koad_data(df):
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {len(df)} entries',
                'total': len(df)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save uploaded data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint to get system statistics"""
    try:
        df = load_koad_data()
        
        stats = {
            'total_entries': len(df),
            'active_entries': len(df[df['KOAD-actief'] == '1']) if 'KOAD-actief' in df.columns else 0,
            'inactive_entries': len(df[df['KOAD-actief'] == '0']) if 'KOAD-actief' in df.columns else 0,
            'unique_postcodes': df['KOAD-pc'].nunique() if 'KOAD-pc' in df.columns else 0,
            'unique_streets': df['KOAD-str'].nunique() if 'KOAD-str' in df.columns else 0
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure backup directory exists
    ensure_backup_dir()
    
    # Run the dashboard
    app.run(host='0.0.0.0', port=5000, debug=True)
