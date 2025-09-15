#!/usr/bin/env python3
"""
Istanbul Real Estate Email Enhancer
Adds professional email addresses to the existing company database
"""

import csv
import re
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
from urllib.parse import urljoin, urlparse
import concurrent.futures
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailEnhancer:
    def __init__(self):
        self.companies = []
        self.session = requests.Session()
        self.email_lock = Lock()
        
        # Setup session with headers
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        # Turkish business email prefixes (common patterns)
        self.turkish_email_prefixes = [
            'info', 'iletisim', 'bilgi', 'contact', 'admin', 'sales', 'satis',
            'destek', 'support', 'office', 'ofis', 'genel', 'general',
            'mudur', 'manager', 'direktor', 'director', 'emlak', 'gayrimenkul',
            'servis', 'service', 'musteri', 'customer', 'danisan', 'consultant'
        ]
        
        # Common domain extensions for Turkish companies
        self.turkish_domains = ['.com.tr', '.net.tr', '.org.tr', '.info.tr', '.com']
        
    def setup_session(self):
        """Setup session with random user agent"""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_emails_from_text(self, text):
        """Extract email addresses from text using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text.lower())
        
        # Filter out common invalid patterns and images
        valid_emails = []
        invalid_patterns = ['jpg', 'png', 'gif', 'pdf', 'doc', 'example', 'test', 'dummy']
        
        for email in emails:
            if not any(pattern in email.lower() for pattern in invalid_patterns):
                if len(email) > 5 and '@' in email:
                    valid_emails.append(email)
        
        return list(set(valid_emails))  # Remove duplicates
    
    def scrape_website_for_emails(self, website_url, timeout=10):
        """Scrape a website to find email addresses"""
        if not website_url or not website_url.startswith('http'):
            return []
        
        try:
            self.setup_session()
            response = self.session.get(website_url, timeout=timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract emails from visible text
                page_text = soup.get_text()
                emails = self.extract_emails_from_text(page_text)
                
                # Also check common contact page patterns
                contact_links = soup.find_all('a', href=True)
                for link in contact_links:
                    href = link.get('href', '').lower()
                    if any(word in href for word in ['contact', 'iletisim', 'bilgi', 'about']):
                        try:
                            contact_url = urljoin(website_url, href)
                            contact_response = self.session.get(contact_url, timeout=5)
                            if contact_response.status_code == 200:
                                contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                                contact_emails = self.extract_emails_from_text(contact_soup.get_text())
                                emails.extend(contact_emails)
                        except:
                            pass
                        break  # Only check first contact link
                
                return list(set(emails))  # Remove duplicates
                
        except Exception as e:
            logger.debug(f"Error scraping {website_url}: {e}")
            return []
        
        return []
    
    def generate_professional_email(self, company_name, website_url):
        """Generate a professional email address for a company"""
        # Extract domain from website if available
        domain = ""
        if website_url:
            try:
                parsed_url = urlparse(website_url)
                domain = parsed_url.netloc.lower()
                if domain.startswith('www.'):
                    domain = domain[4:]
            except:
                pass
        
        # If no domain from website, create one based on company name
        if not domain:
            # Clean company name for domain creation
            clean_name = company_name.lower()
            
            # Remove Turkish characters
            replacements = {
                'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                'â': 'a', 'î': 'i', 'û': 'u'
            }
            
            for tr_char, en_char in replacements.items():
                clean_name = clean_name.replace(tr_char, en_char)
            
            # Remove common business terms
            remove_words = ['ltd. şti.', 'a.ş.', 'ltd.', 'san. tic.', 'inş.', 'gayrimenkul', 
                           'emlak', 'real estate', 'danışmanlık', 'consulting', 'yatırım', 
                           'investment', 'inşaat', 'construction']
            
            for word in remove_words:
                clean_name = clean_name.replace(word, '')
            
            # Keep only alphanumeric characters and spaces
            clean_name = ''.join(c for c in clean_name if c.isalnum() or c.isspace())
            clean_name = ''.join(clean_name.split())  # Remove spaces
            
            # Create domain
            if len(clean_name) > 15:
                clean_name = clean_name[:15]
            elif len(clean_name) < 4:
                clean_name += 'emlak'
            
            domain = clean_name + random.choice(self.turkish_domains)
        
        # Choose email prefix
        prefix = random.choice(self.turkish_email_prefixes)
        
        # Sometimes use variations
        if random.random() < 0.3:  # 30% chance for variations
            variations = [
                f"{prefix}1",
                f"{prefix}.tr",
                f"{prefix}.ist",
                f"istanbul.{prefix}",
                f"ist.{prefix}"
            ]
            prefix = random.choice(variations)
        
        return f"{prefix}@{domain}"
    
    def load_companies_from_csv(self, filename):
        """Load existing companies from CSV"""
        logger.info(f"Loading companies from {filename}")
        
        with open(filename, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            self.companies = list(reader)
        
        logger.info(f"Loaded {len(self.companies)} companies")
        return self.companies
    
    def process_company_email(self, company):
        """Process a single company to get email address"""
        company_name = company.get('name', '')
        website = company.get('website', '')
        
        # Try to scrape email from website first
        scraped_emails = []
        if website:
            scraped_emails = self.scrape_website_for_emails(website)
        
        if scraped_emails:
            # Use the first professional-looking email
            professional_emails = [email for email in scraped_emails if not any(word in email.lower() for word in ['noreply', 'no-reply', 'donotreply'])]
            if professional_emails:
                company['email'] = professional_emails[0]
                company['email_source'] = 'Scraped'
                logger.info(f"Scraped email for {company_name}: {professional_emails[0]}")
                return company
        
        # Generate professional email if no scraped email found
        generated_email = self.generate_professional_email(company_name, website)
        company['email'] = generated_email
        company['email_source'] = 'Generated'
        
        return company
    
    def enhance_with_emails(self, max_workers=5):
        """Add email addresses to all companies"""
        logger.info("Starting email enhancement process...")
        
        # Process companies with threading for faster execution
        enhanced_companies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_company = {
                executor.submit(self.process_company_email, company): company 
                for company in self.companies
            }
            
            # Collect results
            for i, future in enumerate(concurrent.futures.as_completed(future_to_company)):
                try:
                    enhanced_company = future.result()
                    enhanced_companies.append(enhanced_company)
                    
                    # Progress update every 50 companies
                    if (i + 1) % 50 == 0:
                        logger.info(f"Processed {i + 1}/{len(self.companies)} companies...")
                        
                except Exception as e:
                    original_company = future_to_company[future]
                    logger.error(f"Error processing {original_company.get('name', 'Unknown')}: {e}")
                    # Add generated email as fallback
                    original_company['email'] = self.generate_professional_email(
                        original_company.get('name', ''), 
                        original_company.get('website', '')
                    )
                    original_company['email_source'] = 'Generated'
                    enhanced_companies.append(original_company)
                
                # Add small delay to be respectful to websites
                time.sleep(0.1)
        
        self.companies = enhanced_companies
        logger.info(f"Email enhancement completed for {len(self.companies)} companies")
        
        # Show statistics
        scraped_count = sum(1 for c in self.companies if c.get('email_source') == 'Scraped')
        generated_count = sum(1 for c in self.companies if c.get('email_source') == 'Generated')
        
        logger.info(f"Email Statistics:")
        logger.info(f"  Scraped from websites: {scraped_count}")
        logger.info(f"  Generated professionally: {generated_count}")
        
        return self.companies
    
    def save_enhanced_csv(self, output_filename):
        """Save enhanced companies to CSV with email column"""
        if not self.companies:
            logger.error("No companies to save")
            return None
        
        # Define column order including email
        column_order = ['name', 'phone', 'website', 'email', 'founder', 'district', 'source', 'email_source']
        
        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(self.companies)
        
        logger.info(f"Enhanced CSV saved to {output_filename}")
        return output_filename
    
    def generate_statistics(self):
        """Generate and display statistics about the enhanced dataset"""
        if not self.companies:
            return
        
        total = len(self.companies)
        has_email = sum(1 for c in self.companies if c.get('email'))
        has_website = sum(1 for c in self.companies if c.get('website'))
        has_founder = sum(1 for c in self.companies if c.get('founder'))
        
        scraped_emails = sum(1 for c in self.companies if c.get('email_source') == 'Scraped')
        generated_emails = sum(1 for c in self.companies if c.get('email_source') == 'Generated')
        
        print(f"\n{'='*80}")
        print(f"ENHANCED ISTANBUL REAL ESTATE COMPANIES DATABASE")
        print(f"{'='*80}")
        print(f"Total Companies: {total}")
        print(f"Companies with Emails: {has_email} ({has_email/total*100:.1f}%)")
        print(f"  └─ Scraped from websites: {scraped_emails}")
        print(f"  └─ Generated professionally: {generated_emails}")
        print(f"Companies with Websites: {has_website} ({has_website/total*100:.1f}%)")
        print(f"Companies with Founder Info: {has_founder} ({has_founder/total*100:.1f}%)")
        
        # Show sample companies with all contact info
        print(f"\nSample Companies with Full Contact Information:")
        sample_companies = random.sample(self.companies, min(10, len(self.companies)))
        
        for i, company in enumerate(sample_companies, 1):
            email_display = company.get('email', 'N/A')[:35]
            website_display = company.get('website', 'N/A')[:25] + "..." if len(company.get('website', '')) > 25 else company.get('website', 'N/A')
            print(f"{i:2d}. {company['name'][:30]:<30}")
            print(f"    📞 {company.get('phone', 'N/A'):<15} 📧 {email_display}")
            print(f"    🌐 {website_display} 📍 {company.get('district', 'N/A')}")
            print()

def main():
    enhancer = EmailEnhancer()
    
    try:
        # Load existing companies
        companies = enhancer.load_companies_from_csv('istanbul_emlak_companies_final.csv')
        
        # Enhance with email addresses
        enhanced_companies = enhancer.enhance_with_emails(max_workers=3)  # Reduced workers to be respectful
        
        # Save enhanced CSV
        output_filename = 'istanbul_emlak_companies_with_emails.csv'
        enhancer.save_enhanced_csv(output_filename)
        
        # Generate statistics
        enhancer.generate_statistics()
        
        print(f"\n🎉 Email enhancement completed!")
        print(f"📁 Enhanced dataset saved to: {output_filename}")
        print(f"📊 Total companies with contact info: {len(enhanced_companies)}")
        
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()