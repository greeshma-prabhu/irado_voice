#!/usr/bin/env python3
"""
Clean JSON Knowledge Base
Entfernt Duplikate und bereinigt die JSON-Datei.
"""

import json
import hashlib
from collections import defaultdict
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_content_hash(content):
    """Generate a hash for content to detect duplicates"""
    # Create a simplified version for comparison
    simplified = {
        'title': content.get('title', ''),
        'meta_description': content.get('meta_description', ''),
        'sections': []
    }
    
    # Add section content (only headings and first 100 chars of content)
    for section in content.get('sections', []):
        simplified['sections'].append({
            'heading': section.get('heading', ''),
            'content_preview': section.get('content', '')[:100]
        })
    
    text = json.dumps(simplified, sort_keys=True)
    return hashlib.md5(text.encode()).hexdigest()

def clean_content(content):
    """Clean and normalize content"""
    # Clean title
    if content.get('title'):
        content['title'] = content['title'].strip()
    
    # Clean meta description
    if content.get('meta_description'):
        content['meta_description'] = content['meta_description'].strip()
    
    # Clean sections
    cleaned_sections = []
    for section in content.get('sections', []):
        if section.get('heading') and section.get('content'):
            # Remove extra whitespace
            heading = section['heading'].strip()
            content_text = section['content'].strip()
            
            # Only keep sections with meaningful content
            if len(content_text) > 20:
                cleaned_sections.append({
                    'heading': heading,
                    'content': content_text,
                    'heading_level': section.get('heading_level', 'h1')
                })
    
    content['sections'] = cleaned_sections
    
    # Clean FAQs
    cleaned_faqs = []
    for faq in content.get('faqs', []):
        if faq.get('question') and faq.get('answer'):
            question = faq['question'].strip()
            answer = faq['answer'].strip()
            if len(answer) > 20:
                cleaned_faqs.append({
                    'question': question,
                    'answer': answer
                })
    
    content['faqs'] = cleaned_faqs
    
    return content

def remove_duplicates(knowledge_base):
    """Remove duplicate content from knowledge base"""
    logger.info("Starting duplicate removal...")
    
    seen_hashes = set()
    cleaned_knowledge_base = defaultdict(list)
    total_removed = 0
    
    for category, pages in knowledge_base.items():
        logger.info(f"Processing category: {category} ({len(pages)} pages)")
        
        for page in pages:
            # Clean the content first
            cleaned_page = clean_content(page)
            
            # Generate hash
            content_hash = get_content_hash(cleaned_page)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                cleaned_knowledge_base[category].append(cleaned_page)
            else:
                total_removed += 1
                logger.debug(f"Removed duplicate: {page.get('url', 'unknown')}")
        
        logger.info(f"Category {category}: {len(knowledge_base[category])} -> {len(cleaned_knowledge_base[category])} pages")
    
    logger.info(f"Total duplicates removed: {total_removed}")
    return dict(cleaned_knowledge_base)

def merge_similar_content(knowledge_base):
    """Merge similar content sections"""
    logger.info("Starting content merging...")
    
    for category, pages in knowledge_base.items():
        logger.info(f"Merging similar content in category: {category}")
        
        # Group pages by similar titles
        title_groups = defaultdict(list)
        for page in pages:
            title = page.get('title', '').lower()
            # Create a simplified title for grouping
            simple_title = ' '.join(word for word in title.split() if len(word) > 3)
            title_groups[simple_title].append(page)
        
        # Merge similar pages
        merged_pages = []
        for title, similar_pages in title_groups.items():
            if len(similar_pages) == 1:
                merged_pages.append(similar_pages[0])
            else:
                # Merge multiple similar pages
                merged_page = similar_pages[0].copy()
                all_sections = []
                all_faqs = []
                
                for page in similar_pages:
                    all_sections.extend(page.get('sections', []))
                    all_faqs.extend(page.get('faqs', []))
                
                # Remove duplicate sections
                unique_sections = []
                section_texts = set()
                for section in all_sections:
                    section_text = f"{section.get('heading', '')}: {section.get('content', '')[:100]}"
                    if section_text not in section_texts:
                        section_texts.add(section_text)
                        unique_sections.append(section)
                
                # Remove duplicate FAQs
                unique_faqs = []
                faq_texts = set()
                for faq in all_faqs:
                    faq_text = f"{faq.get('question', '')}: {faq.get('answer', '')[:100]}"
                    if faq_text not in faq_texts:
                        faq_texts.add(faq_text)
                        unique_faqs.append(faq)
                
                merged_page['sections'] = unique_sections
                merged_page['faqs'] = unique_faqs
                merged_page['merged_from'] = len(similar_pages)
                
                merged_pages.append(merged_page)
                logger.info(f"Merged {len(similar_pages)} similar pages into one")
        
        knowledge_base[category] = merged_pages

def clean_json_file(input_file, output_file):
    """Clean the JSON knowledge base file"""
    logger.info(f"Loading JSON file: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return
    
    original_total = sum(len(pages) for pages in data['knowledge_base'].values())
    logger.info(f"Original total pages: {original_total}")
    
    # Remove duplicates
    cleaned_knowledge_base = remove_duplicates(data['knowledge_base'])
    
    # Merge similar content
    merge_similar_content(cleaned_knowledge_base)
    
    # Update metadata
    final_total = sum(len(pages) for pages in cleaned_knowledge_base.values())
    data['knowledge_base'] = cleaned_knowledge_base
    data['metadata']['cleaned_at'] = datetime.now().isoformat()
    data['metadata']['original_pages'] = original_total
    data['metadata']['final_pages'] = final_total
    data['metadata']['pages_removed'] = original_total - final_total
    
    # Save cleaned file
    logger.info(f"Saving cleaned JSON file: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Cleaning completed!")
        logger.info(f"Original pages: {original_total}")
        logger.info(f"Final pages: {final_total}")
        logger.info(f"Pages removed: {original_total - final_total}")
        
        # Show category breakdown
        for category, pages in cleaned_knowledge_base.items():
            logger.info(f"{category}: {len(pages)} pages")
            
    except Exception as e:
        logger.error(f"Error saving JSON file: {e}")

def main():
    """Main function"""
    input_file = "knowledge_vector/smart_irado_knowledge_base.json"
    output_file = "knowledge_vector/cleaned_irado_knowledge_base.json"
    
    logger.info("Starting JSON cleaning process...")
    clean_json_file(input_file, output_file)
    logger.info("JSON cleaning completed!")

if __name__ == "__main__":
    main()



