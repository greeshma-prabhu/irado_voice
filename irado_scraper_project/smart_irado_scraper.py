#!/usr/bin/env python3
"""
Smart Irado.nl Web Scraper
Ein intelligenter Scraper der sich auf die wichtigsten Inhaltsseiten konzentriert.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import hashlib
from collections import defaultdict
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartIradoScraper:
    def __init__(self, base_url="https://www.irado.nl"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"'
        })
        self.visited_urls = set()
        self.content_hash = set()
        self.knowledge_base = defaultdict(list)
        self.stats = {
            'total_pages': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'duplicates_found': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Pre-defined important URLs to scrape
        self.important_urls = [
            "https://www.irado.nl/",
            "https://www.irado.nl/afvalsoorten",
            "https://www.irado.nl/afvalsoorten/grofvuil",
            "https://www.irado.nl/afvalsoorten/grofvuil/afspraak-maken",
            "https://www.irado.nl/afvalsoorten/grofvuil/aanbiedregels",
            "https://www.irado.nl/afvalsoorten/oud-papier",
            "https://www.irado.nl/afvalsoorten/glas",
            "https://www.irado.nl/afvalsoorten/plastic-afval-scheiden-voor-het-milieu",
            "https://www.irado.nl/afvalsoorten/elektrische-apparaten",
            "https://www.irado.nl/bewoners/milieustraat",
            "https://www.irado.nl/milieustraat",
            "https://www.irado.nl/milieustraat/aanhanger-lenen",
            "https://www.irado.nl/containerlocaties",
            "https://www.irado.nl/afvalkalender",
            "https://www.irado.nl/contact",
            "https://www.irado.nl/over-irado",
            "https://www.irado.nl/over-irado/werken-bij-irado",
            "https://www.irado.nl/over-irado/wie-zijn-wij",
            "https://www.irado.nl/nieuws",
            "https://www.irado.nl/melding-maken",
            "https://www.irado.nl/afvalapp-irado",
            "https://www.irado.nl/meer-informatie-over-afvalpas-bestellen",
            "https://www.irado.nl/algemene-voorwaarden-irado-shop",
            "https://www.irado.nl/privacyverklaring",
            "https://www.irado.nl/disclaimer",
            "https://www.irado.nl/schiedam/milieustraat",
            "https://www.irado.nl/vlaardingen/milieustraat",
            "https://www.irado.nl/capelle/milieustraat",
            "https://www.irado.nl/zakelijk/milieustraat",
            "https://www.irado.nl/zakelijk/container-huren/bouwcontainer-huren",
            "https://www.irado.nl/ongediertebestrijding",
            "https://www.irado.nl/educatie",
            "https://www.irado.nl/educatie/partner-kindergemeenteraad",
            "https://www.irado.nl/productoverzicht",
            "https://www.irado.nl/product/zakelijke-milieupas-voor-milieustraat-schiedam",
            "https://www.irado.nl/product/zakelijke-milieupas-voor-reinigingsrecht-en-milieustraat-schiedam"
        ]
        
    def is_smart_url(self, url):
        """Smart URL validation - focus on content pages, avoid duplicates"""
        if not url or 'irado.nl' not in url:
            return False
        
        # Exclude external domains
        parsed = urlparse(url)
        if parsed.netloc not in ['www.irado.nl', 'irado.nl']:
            return False
        
        # Exclude unwanted patterns
        exclude_patterns = [
            'twitter.com', 'facebook.com', 'linkedin.com', 'whatsapp.com',
            'api.whatsapp.com', 'mailto:', 'tel:', 'javascript:',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar',
            'share', 'sharer', 'intent', 'signup', 'login', 'logout',
            'admin', 'wp-admin', 'wp-content', 'wp-includes',
            'search', 'zoeken', 'filter', 'sort', 'tag', 'category',
            'feed', 'rss', 'atom', 'xml', 'json', '#environment-selection',
            '?attachment_id=', 'attachment_id='
        ]
        
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        
        # Skip query parameter pages that are just variations
        if '?' in url:
            # Only allow specific query parameters that add value
            allowed_params = ['page=', 'p=']
            if not any(param in url for param in allowed_params):
                return False
        
        # Skip taxonomy and postcode pages (too many duplicates)
        skip_patterns = [
            '?gemeente_zipcode=',
            '?app_gemeente=',
            '?taxonomy=',
            '?term=',
            'tag/',
            'category/',
            'author/',
            'product-tag/',
            'product-categorie/',
            'nieuws-categorie/',
            'vgv_cats/'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            time.sleep(random.uniform(1, 2))
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Non-HTML content for {url}: {content_type}")
                return None
                
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            self.stats['failed_scrapes'] += 1
            return None
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted elements
        unwanted_patterns = [
            r'Delen:',
            r'Let op.*?bedoeld',
            r'Cookie.*?accepteren',
            r'JavaScript.*?browser',
            r'Continue.*?Chat',
            r'Inloggen.*?Registreren',
            r'Menu.*?Sluiten',
            r'Zoeken.*?Submit',
            r'Social.*?media',
            r'Footer.*?content',
            r'Breadcrumb',
            r'Skip content'
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        
        return text.strip()
    
    def extract_main_content(self, soup):
        """Extract main content from the page"""
        # Remove unwanted elements
        for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
            element.decompose()
        
        # Remove common unwanted classes
        unwanted_selectors = [
            '.navigation', '.menu', '.sidebar', '.footer', '.header', 
            '.breadcrumb', '.cookie', '.social', '.share', '.search',
            '.login', '.register', '.admin', '.ads', '.banner'
        ]
        
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Find main content area
        main_content = None
        selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '#content',
            '.page-content',
            '.article-content',
            '.post-content',
            '.entry-content',
            'article'
        ]
        
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        return main_content
    
    def extract_structured_content(self, soup, url):
        """Extract structured content from the page"""
        content = {
            'url': url,
            'title': '',
            'meta_description': '',
            'sections': [],
            'faqs': [],
            'contact_info': {},
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = self.clean_text(title_tag.get_text())
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content['meta_description'] = self.clean_text(meta_desc.get('content', ''))
        
        # Extract main content
        main_content = self.extract_main_content(soup)
        if not main_content:
            return content
        
        # Extract sections (headings and their content)
        headings = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for heading in headings:
            section = {
                'heading': self.clean_text(heading.get_text()),
                'content': '',
                'heading_level': heading.name
            }
            
            # Get content until next heading
            current = heading.next_sibling
            heading_level = int(heading.name[1])
            
            while current:
                if hasattr(current, 'name') and current.name:
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if int(current.name[1]) <= heading_level:
                            break
                
                if hasattr(current, 'get_text'):
                    text = self.clean_text(current.get_text())
                    if text:
                        section['content'] += text + ' '
                current = current.next_sibling
            
            # Clean up content
            section['content'] = self.clean_text(section['content'])
            
            if section['content'] and len(section['content']) > 20:
                content['sections'].append(section)
        
        # If no sections found, try to extract paragraphs
        if not content['sections']:
            paragraphs = main_content.find_all('p')
            if paragraphs:
                content['sections'].append({
                    'heading': content['title'] or 'Content',
                    'content': ' '.join([self.clean_text(p.get_text()) for p in paragraphs if self.clean_text(p.get_text())]),
                    'heading_level': 'h1'
                })
        
        # Extract FAQ-like content
        for section in content['sections']:
            if '?' in section['heading'] and len(section['content']) > 50:
                content['faqs'].append({
                    'question': section['heading'],
                    'answer': section['content']
                })
        
        # Extract contact information
        contact_patterns = {
            'phone': r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'address': r'(Postbus \d+[^,]*?,\s*\d{4}\s*[A-Z]{2}\s*[^,]*?,\s*[^,]*?)',
            'kvk': r'(KvK[:\s]*\d+)',
            'btw': r'(BTW[:\s]*[A-Z]{2}\s*\d+\.\d+\.\d+\.\w+)'
        }
        
        full_text = ' '.join([s['content'] for s in content['sections']])
        for info_type, pattern in contact_patterns.items():
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                content['contact_info'][info_type] = list(set(matches))
        
        return content
    
    def get_content_hash(self, content):
        """Generate a hash for content to detect duplicates"""
        simplified = {
            'title': content.get('title', ''),
            'sections': [(s.get('heading', ''), s.get('content', '')) for s in content.get('sections', [])]
        }
        text = json.dumps(simplified, sort_keys=True)
        return hashlib.md5(text.encode()).hexdigest()
    
    def is_duplicate(self, content):
        """Check if content is a duplicate"""
        content_hash = self.get_content_hash(content)
        if content_hash in self.content_hash:
            return True
        self.content_hash.add(content_hash)
        return False
    
    def categorize_content(self, content, url):
        """Categorize content based on URL and content"""
        path = urlparse(url).path.lower()
        
        categories = {
            'afvalsoorten': ['afval', 'papier', 'glas', 'plastic', 'pmd', 'grofvuil', 'restafval', 'oud-papier'],
            'diensten': ['afspraak', 'bestellen', 'ophalen', 'milieustraat', 'container', 'aanhanger', 'melding'],
            'informatie': ['informatie', 'meer', 'over', 'hoe', 'waar', 'wanneer', 'nieuws', 'educatie'],
            'contact': ['contact', 'klantenservice', 'vragen', 'help'],
            'regels': ['regels', 'aanbiedregels', 'voorwaarden', 'disclaimer', 'privacy'],
            'gemeenten': ['schiedam', 'vlaardingen', 'capelle', 'rozenburg'],
            'bedrijfsleven': ['zakelijk', 'bedrijfsafval', 'ondernemer', 'product'],
            'vacatures': ['vacature', 'werken', 'stage', 'job']
        }
        
        # Determine category based on URL path
        for category, keywords in categories.items():
            if any(keyword in path for keyword in keywords):
                return category
        
        # Fallback categorization based on content
        full_text = ' '.join([s['content'] for s in content['sections']]).lower()
        
        for category, keywords in categories.items():
            if any(keyword in full_text for keyword in keywords):
                return category
        
        return 'algemeen'
    
    def scrape_page(self, url):
        """Scrape a single page"""
        if url in self.visited_urls:
            return None
        
        if not self.is_smart_url(url):
            return None
        
        self.visited_urls.add(url)
        self.stats['total_pages'] += 1
        logger.info(f"Scraping: {url}")
        
        html_content = self.get_page_content(url)
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        content = self.extract_structured_content(soup, url)
        
        # Skip if no meaningful content
        if not content['sections'] and not content['title']:
            logger.warning(f"No meaningful content found: {url}")
            return None
        
        # For pages with only title but no sections, create a basic section
        if content['title'] and not content['sections']:
            content['sections'].append({
                'heading': content['title'],
                'content': content['meta_description'] or 'Content available on this page.',
                'heading_level': 'h1'
            })
        
        # Check for duplicates
        if self.is_duplicate(content):
            logger.info(f"Duplicate content found: {url}")
            self.stats['duplicates_found'] += 1
            return None
        
        # Categorize content
        category = self.categorize_content(content, url)
        content['category'] = category
        
        self.stats['successful_scrapes'] += 1
        return content
    
    def find_smart_links(self, url):
        """Find smart links - avoid duplicates and focus on content"""
        html_content = self.get_page_content(url)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            
            # Only include smart irado.nl links
            if (self.is_smart_url(full_url) and 
                full_url not in self.visited_urls):
                links.append(full_url)
        
        return list(set(links))
    
    def scrape_site(self):
        """Scrape the site using smart approach"""
        logger.info("Starting smart scraping process...")
        
        # Start with important URLs
        to_visit = self.important_urls.copy()
        scraped_count = 0
        
        logger.info(f"Starting with {len(to_visit)} important URLs...")
        
        while to_visit:  # No artificial limit - scrape all important pages
            url = to_visit.pop(0)
            
            content = self.scrape_page(url)
            if content:
                category = content['category']
                self.knowledge_base[category].append(content)
                scraped_count += 1
                
                logger.info(f"Scraped {scraped_count} pages. Category: {category}")
            
            # Find smart links (no artificial limit)
            if scraped_count < 100:  # Find links for first 100 pages to avoid infinite loops
                new_links = self.find_smart_links(url)
                # Add only unique links that aren't already planned
                for link in new_links:
                    if link not in to_visit and link not in self.visited_urls:
                        to_visit.append(link)
                logger.info(f"Found {len(new_links)} smart links from {url}")
            
            # Be respectful to the server
            time.sleep(random.uniform(1, 2))
        
        return self.knowledge_base
    
    def save_knowledge_base(self, filename="knowledge_base.json"):
        """Save the knowledge base to a JSON file"""
        knowledge_dict = dict(self.knowledge_base)
        
        # Add metadata
        output_data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'base_url': self.base_url,
                'stats': self.stats,
                'total_categories': len(knowledge_dict),
                'total_pages': sum(len(pages) for pages in knowledge_dict.values()),
                'important_urls_used': len(self.important_urls)
            },
            'knowledge_base': knowledge_dict
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Knowledge base saved to {filename}")
        
        # Print statistics
        total_pages = sum(len(pages) for pages in knowledge_dict.values())
        logger.info(f"=== SMART SCRAPING STATISTICS ===")
        logger.info(f"Total pages visited: {self.stats['total_pages']}")
        logger.info(f"Successful scrapes: {self.stats['successful_scrapes']}")
        logger.info(f"Failed scrapes: {self.stats['failed_scrapes']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Total unique pages: {total_pages}")
        
        for category, pages in knowledge_dict.items():
            logger.info(f"{category}: {len(pages)} pages")
        
        start_time = datetime.fromisoformat(self.stats['start_time'])
        duration = datetime.now() - start_time
        logger.info(f"Total duration: {duration}")

def main():
    """Main function to run the scraper"""
    scraper = SmartIradoScraper()
    
    logger.info("Starting Smart Irado.nl scraper...")
    knowledge_base = scraper.scrape_site()
    
    # Save the knowledge base
    scraper.save_knowledge_base("knowledge_vector/smart_irado_knowledge_base.json")
    
    logger.info("Smart scraping completed successfully!")

if __name__ == "__main__":
    main()
