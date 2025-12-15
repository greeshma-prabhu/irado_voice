#!/usr/bin/env python3
"""
Update system prompt in database from file
"""
import sys
import os
sys.path.append('/opt/irado/chatbot')

from system_prompt_service import SystemPromptService
from config import Config

def main():
    print("📝 Updating system prompt in database...")
    
    # Read prompt from file
    prompt_file = '/opt/irado/chatbot/prompts/system_prompt.txt'
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Read prompt from file: {len(content)} characters, {len(content.splitlines())} lines")
        
        # Update in database
        service = SystemPromptService()
        
        # Create new version
        result = service.create_prompt(
            content=content,
            version='v1.1',
            created_by='system',
            notes='Updated from system_prompt.txt file'
        )
        
        if result:
            print(f"✅ Prompt created in database with ID: {result}")
            
            # Set as active
            if service.set_active_prompt(result):
                print(f"✅ Prompt set as active")
            else:
                print(f"⚠️  Warning: Could not set as active")
        else:
            print("❌ Failed to create prompt")
            return 1
        
        # Verify
        active = service.get_active_prompt()
        if active:
            print(f"✅ Verification: Active prompt has {len(active)} characters")
            print(f"   First 100 chars: {active[:100]}...")
        else:
            print("❌ Verification failed: No active prompt")
            return 1
        
        print("\n🎉 System prompt successfully updated in database!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
