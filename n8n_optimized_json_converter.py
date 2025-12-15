#!/usr/bin/env python3
"""
n8n Optimized JSON Converter
Konvertiert die Irado Knowledge Base in ein n8n-optimiertes Format
"""

import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_n8n_documents(knowledge_base):
    """Erstellt n8n-optimierte Dokumente mit kleineren Chunks"""
    logger.info("Creating n8n-optimized documents...")
    
    documents = []
    
    for category, pages in knowledge_base.items():
        logger.info(f"Processing category: {category} ({len(pages)} pages)")
        
        for page in pages:
            # Jede FAQ als separates Dokument
            for faq in page.get('faqs', []):
                if faq.get('question') and faq.get('answer'):
                    # FAQ-Dokument erstellen
                    doc = {
                        "json": {
                            "content": f"Frage: {faq['question']}\n\nAntwort: {faq['answer']}",
                            "metadata": {
                                "type": "faq",
                                "category": category,
                                "url": page.get('url', ''),
                                "title": page.get('title', ''),
                                "question": faq['question'],
                                "answer_length": len(faq['answer'])
                            }
                        }
                    }
                    documents.append(doc)
            
            # Jede Sektion als separates Dokument (wenn nicht zu lang)
            for section in page.get('sections', []):
                if section.get('heading') and section.get('content'):
                    content = section['content']
                    
                    # Wenn Content zu lang ist, in kleinere Chunks aufteilen
                    if len(content) > 500:
                        # Teile in 500-Zeichen-Chunks auf
                        chunks = [content[i:i+500] for i in range(0, len(content), 400)]
                        for i, chunk in enumerate(chunks):
                            doc = {
                                "json": {
                                    "content": f"{section['heading']}\n\n{chunk}",
                                    "metadata": {
                                        "type": "section",
                                        "category": category,
                                        "url": page.get('url', ''),
                                        "title": page.get('title', ''),
                                        "heading": section['heading'],
                                        "chunk": i + 1,
                                        "total_chunks": len(chunks)
                                    }
                                }
                            }
                            documents.append(doc)
                    else:
                        # Normale Sektion
                        doc = {
                            "json": {
                                "content": f"{section['heading']}\n\n{content}",
                                "metadata": {
                                    "type": "section",
                                    "category": category,
                                    "url": page.get('url', ''),
                                    "title": page.get('title', ''),
                                    "heading": section['heading']
                                }
                            }
                        }
                        documents.append(doc)
    
    logger.info(f"Created {len(documents)} n8n-optimized documents")
    return documents

def create_faq_only_documents(knowledge_base):
    """Erstellt nur FAQ-Dokumente für bessere Präzision"""
    logger.info("Creating FAQ-only documents...")
    
    documents = []
    
    for category, pages in knowledge_base.items():
        for page in pages:
            for faq in page.get('faqs', []):
                if faq.get('question') and faq.get('answer'):
                    # FAQ als separates Dokument
                    doc = {
                        "json": {
                            "content": f"Frage: {faq['question']}\n\nAntwort: {faq['answer']}",
                            "metadata": {
                                "type": "faq",
                                "category": category,
                                "url": page.get('url', ''),
                                "title": page.get('title', ''),
                                "question": faq['question'],
                                "answer_length": len(faq['answer'])
                            }
                        }
                    }
                    documents.append(doc)
    
    logger.info(f"Created {len(documents)} FAQ-only documents")
    return documents

def create_small_chunk_documents(knowledge_base, chunk_size=300):
    """Erstellt sehr kleine Chunks für maximale Präzision"""
    logger.info(f"Creating small chunk documents (max {chunk_size} characters)...")
    
    documents = []
    
    for category, pages in knowledge_base.items():
        for page in pages:
            # FAQs
            for faq in page.get('faqs', []):
                if faq.get('question') and faq.get('answer'):
                    question = faq['question']
                    answer = faq['answer']
                    
                    # Wenn Antwort zu lang, in Chunks aufteilen
                    if len(answer) > chunk_size:
                        chunks = [answer[i:i+chunk_size] for i in range(0, len(answer), chunk_size-50)]
                        for i, chunk in enumerate(chunks):
                            doc = {
                                "json": {
                                    "content": f"Frage: {question}\n\nAntwort: {chunk}",
                                    "metadata": {
                                        "type": "faq_chunk",
                                        "category": category,
                                        "url": page.get('url', ''),
                                        "title": page.get('title', ''),
                                        "question": question,
                                        "chunk": i + 1,
                                        "total_chunks": len(chunks)
                                    }
                                }
                            }
                            documents.append(doc)
                    else:
                        doc = {
                            "json": {
                                "content": f"Frage: {question}\n\nAntwort: {answer}",
                                "metadata": {
                                    "type": "faq",
                                    "category": category,
                                    "url": page.get('url', ''),
                                    "title": page.get('title', ''),
                                    "question": question
                                }
                            }
                        }
                        documents.append(doc)
            
            # Sektionen
            for section in page.get('sections', []):
                if section.get('heading') and section.get('content'):
                    heading = section['heading']
                    content = section['content']
                    
                    # Content in kleine Chunks aufteilen
                    if len(content) > chunk_size:
                        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size-50)]
                        for i, chunk in enumerate(chunks):
                            doc = {
                                "json": {
                                    "content": f"{heading}\n\n{chunk}",
                                    "metadata": {
                                        "type": "section_chunk",
                                        "category": category,
                                        "url": page.get('url', ''),
                                        "title": page.get('title', ''),
                                        "heading": heading,
                                        "chunk": i + 1,
                                        "total_chunks": len(chunks)
                                    }
                                }
                            }
                            documents.append(doc)
                    else:
                        doc = {
                            "json": {
                                "content": f"{heading}\n\n{content}",
                                "metadata": {
                                    "type": "section",
                                    "category": category,
                                    "url": page.get('url', ''),
                                    "title": page.get('title', ''),
                                    "heading": heading
                                }
                            }
                        }
                        documents.append(doc)
    
    logger.info(f"Created {len(documents)} small chunk documents")
    return documents

def convert_to_n8n_format(input_file, output_file, mode="small_chunks"):
    """Konvertiert die Knowledge Base in n8n-Format"""
    logger.info(f"Loading JSON file: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return
    
    knowledge_base = data.get('knowledge_base', {})
    logger.info(f"Loaded {sum(len(pages) for pages in knowledge_base.values())} pages")
    
    # Erstelle Dokumente basierend auf Modus
    if mode == "faq_only":
        documents = create_faq_only_documents(knowledge_base)
    elif mode == "small_chunks":
        documents = create_small_chunk_documents(knowledge_base, chunk_size=300)
    else:
        documents = create_n8n_documents(knowledge_base)
    
    # Speichere n8n-optimierte Datei
    logger.info(f"Saving n8n-optimized file: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Conversion completed!")
        logger.info(f"Created {len(documents)} documents for n8n")
        
        # Statistiken
        faq_count = sum(1 for doc in documents if doc['json']['metadata']['type'].startswith('faq'))
        section_count = sum(1 for doc in documents if doc['json']['metadata']['type'].startswith('section'))
        
        logger.info(f"FAQ documents: {faq_count}")
        logger.info(f"Section documents: {section_count}")
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")

def main():
    """Main function"""
    input_file = "/opt/irado/irado_scraper_project/knowledge_vector/smart_irado_knowledge_base.json"
    
    # Verschiedene Modi testen
    modes = [
        ("small_chunks", "n8n_small_chunks_300.json"),
        ("faq_only", "n8n_faq_only.json"),
        ("mixed", "n8n_mixed_optimized.json")
    ]
    
    for mode, output_file in modes:
        logger.info(f"\n=== Converting with mode: {mode} ===")
        convert_to_n8n_format(input_file, output_file, mode)

if __name__ == "__main__":
    main()


