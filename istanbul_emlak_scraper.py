#!/usr/bin/env python3
"""
Istanbul Real Estate Agency Scraper
Scrapes 1,000 real estate companies from Istanbul with contact details, websites, and founder info.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from urllib.parse import urljoin, quote
import logging
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IstanbulEmlakScraper:
    def __init__(self):
        self.companies = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Istanbul districts for comprehensive coverage
        self.istanbul_districts = [
            "Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", 
            "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", 
            "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", 
            "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kağıthane", 
            "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", 
            "Silivri", "Şile", "Şişli", "Sultangazi", "Sultanbeyli", "Tuzla", 
            "Ümraniye", "Üsküdar", "Zeytinburnu"
        ]
        
        # Initialize Selenium driver
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Selenium Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.warning(f"Chrome driver not available: {e}. Will use requests only.")
            self.driver = None
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid being blocked"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def extract_phone_numbers(self, text):
        """Extract Turkish phone numbers from text"""
        # Turkish phone number patterns
        patterns = [
            r'\+90\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}',  # +90 XXX XXX XX XX
            r'0\d{3}\s*\d{3}\s*\d{2}\s*\d{2}',        # 0XXX XXX XX XX
            r'\d{3}\s*\d{3}\s*\d{2}\s*\d{2}',         # XXX XXX XX XX
        ]
        
        phones = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Clean and normalize phone numbers
        cleaned_phones = []
        for phone in phones:
            cleaned = re.sub(r'\s+', '', phone)
            if not cleaned.startswith('+90'):
                if cleaned.startswith('0'):
                    cleaned = '+90' + cleaned[1:]
                else:
                    cleaned = '+90' + cleaned
            cleaned_phones.append(cleaned)
        
        return list(set(cleaned_phones))  # Remove duplicates
    
    def scrape_sahibinden_emlak(self, district):
        """Scrape real estate companies from Sahibinden.com"""
        logger.info(f"Scraping Sahibinden for district: {district}")
        
        try:
            # Search for real estate agencies in the district
            search_url = f"https://www.sahibinden.com/emlak-ofisi/{district.lower()}-istanbul"
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find real estate office listings
                offices = soup.find_all('div', class_='classified')
                
                for office in offices[:10]:  # Limit to prevent overload
                    try:
                        company_data = self.extract_company_info_sahibinden(office, district)
                        if company_data:
                            self.companies.append(company_data)
                            logger.info(f"Found company: {company_data.get('name', 'Unknown')}")
                    except Exception as e:
                        logger.error(f"Error extracting company info: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error scraping Sahibinden for {district}: {e}")
        
        self.random_delay()
    
    def extract_company_info_sahibinden(self, office_element, district):
        """Extract company information from Sahibinden office element"""
        company_data = {
            'name': 'Unknown',
            'phone': '',
            'website': '',
            'founder': '',
            'district': district,
            'source': 'Sahibinden'
        }
        
        try:
            # Extract company name
            name_elem = office_element.find('a', class_='classifiedTitle')
            if name_elem:
                company_data['name'] = name_elem.text.strip()
            
            # Extract phone number from contact info
            contact_elem = office_element.find('div', class_='contact-info')
            if contact_elem:
                phones = self.extract_phone_numbers(contact_elem.text)
                if phones:
                    company_data['phone'] = phones[0]
            
            # Try to find website
            link_elem = office_element.find('a', href=True)
            if link_elem and 'sahibinden' not in link_elem['href']:
                company_data['website'] = link_elem['href']
            
        except Exception as e:
            logger.error(f"Error extracting from Sahibinden element: {e}")
        
        return company_data if company_data['name'] != 'Unknown' else None
    
    def scrape_hepsiemlak(self, district):
        """Scrape real estate companies from Hepsiemlak.com"""
        logger.info(f"Scraping Hepsiemlak for district: {district}")
        
        try:
            # Search for real estate agencies
            search_url = f"https://www.hepsiemlak.com/emlak-ofisleri/{district.lower()}-istanbul"
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find agency listings
                agencies = soup.find_all('div', class_='agency-item')
                
                for agency in agencies[:10]:  # Limit per district
                    try:
                        company_data = self.extract_company_info_hepsiemlak(agency, district)
                        if company_data:
                            self.companies.append(company_data)
                            logger.info(f"Found company: {company_data.get('name', 'Unknown')}")
                    except Exception as e:
                        logger.error(f"Error extracting company info: {e}")
                        continue
            
        except Exception as e:
            logger.error(f"Error scraping Hepsiemlak for {district}: {e}")
        
        self.random_delay()
    
    def extract_company_info_hepsiemlak(self, agency_element, district):
        """Extract company information from Hepsiemlak agency element"""
        company_data = {
            'name': 'Unknown',
            'phone': '',
            'website': '',
            'founder': '',
            'district': district,
            'source': 'Hepsiemlak'
        }
        
        try:
            # Extract agency name
            name_elem = agency_element.find('h3') or agency_element.find('a')
            if name_elem:
                company_data['name'] = name_elem.text.strip()
            
            # Extract contact information
            contact_section = agency_element.find('div', class_='contact')
            if contact_section:
                phones = self.extract_phone_numbers(contact_section.text)
                if phones:
                    company_data['phone'] = phones[0]
            
            # Look for website
            website_elem = agency_element.find('a', class_='website')
            if website_elem and website_elem.get('href'):
                company_data['website'] = website_elem['href']
            
        except Exception as e:
            logger.error(f"Error extracting from Hepsiemlak element: {e}")
        
        return company_data if company_data['name'] != 'Unknown' else None
    
    def scrape_google_maps_selenium(self, district):
        """Use Selenium to scrape Google Maps for real estate agencies"""
        if not self.driver:
            return
        
        logger.info(f"Scraping Google Maps for district: {district}")
        
        try:
            search_query = f"emlak ofisi {district} istanbul"
            maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
            
            self.driver.get(maps_url)
            time.sleep(3)  # Wait for page load
            
            # Find business listings
            results = self.driver.find_elements(By.CSS_SELECTOR, '[data-result-index]')
            
            for i, result in enumerate(results[:15]):  # Limit per district
                try:
                    company_data = self.extract_google_maps_info(result, district)
                    if company_data:
                        self.companies.append(company_data)
                        logger.info(f"Found company: {company_data.get('name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Error extracting Google Maps info: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping Google Maps for {district}: {e}")
        
        self.random_delay()
    
    def extract_google_maps_info(self, result_element, district):
        """Extract company information from Google Maps result"""
        company_data = {
            'name': 'Unknown',
            'phone': '',
            'website': '',
            'founder': '',
            'district': district,
            'source': 'Google Maps'
        }
        
        try:
            # Click on the result to get details
            result_element.click()
            time.sleep(2)
            
            # Extract business name
            name_elem = self.driver.find_element(By.CSS_SELECTOR, 'h1')
            if name_elem:
                company_data['name'] = name_elem.text.strip()
            
            # Look for phone number
            try:
                phone_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="phone"]')
                if phone_elem:
                    phones = self.extract_phone_numbers(phone_elem.text)
                    if phones:
                        company_data['phone'] = phones[0]
            except:
                pass
            
            # Look for website
            try:
                website_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-item-id="authority"]')
                if website_elem:
                    company_data['website'] = website_elem.get_attribute('href')
            except:
                pass
            
        except Exception as e:
            logger.error(f"Error extracting Google Maps details: {e}")
        
        return company_data if company_data['name'] != 'Unknown' else None
    
    def scrape_additional_sources(self, district):
        """Scrape additional Turkish real estate directories"""
        logger.info(f"Scraping additional sources for district: {district}")
        
        # Add more Turkish real estate websites
        additional_urls = [
            f"https://www.zingat.com/emlak-ofisleri/{district.lower()}-istanbul",
            f"https://www.emlakjet.com/ofisler/{district.lower()}-istanbul",
        ]
        
        for url in additional_urls:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Generic extraction logic
                    self.extract_generic_listings(soup, district, url)
                self.random_delay(0.5, 1.5)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
    
    def extract_generic_listings(self, soup, district, source_url):
        """Generic extraction for various real estate websites"""
        # Look for common patterns in real estate listings
        selectors = [
            'div[class*="office"]',
            'div[class*="agency"]',
            'div[class*="emlak"]',
            'div[class*="company"]',
            'article',
            '.listing-item',
            '.company-card'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements[:5]:  # Limit per selector
                try:
                    name = self.extract_text_by_tags(elem, ['h1', 'h2', 'h3', 'h4', '.title', '.name'])
                    if name and 'emlak' in name.lower():
                        company_data = {
                            'name': name,
                            'phone': self.extract_phone_from_element(elem),
                            'website': self.extract_website_from_element(elem),
                            'founder': '',
                            'district': district,
                            'source': source_url.split('/')[2]
                        }
                        
                        if company_data['name'] != 'Unknown':
                            self.companies.append(company_data)
                            logger.info(f"Found company: {company_data['name']}")
                except Exception as e:
                    continue
    
    def extract_text_by_tags(self, element, tag_selectors):
        """Extract text using multiple tag selectors"""
        for selector in tag_selectors:
            try:
                elem = element.select_one(selector)
                if elem and elem.text.strip():
                    return elem.text.strip()
            except:
                continue
        return None
    
    def extract_phone_from_element(self, element):
        """Extract phone number from an element"""
        phones = self.extract_phone_numbers(element.text)
        return phones[0] if phones else ''
    
    def extract_website_from_element(self, element):
        """Extract website from an element"""
        links = element.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('http') and 'sahibinden' not in href and 'hepsiemlak' not in href:
                return href
        return ''
    
    def run_scraper(self, target_count=1000):
        """Main scraping function"""
        logger.info(f"Starting scraping for {target_count} real estate companies in Istanbul")
        
        districts_per_round = len(self.istanbul_districts)
        companies_per_district = max(1, target_count // districts_per_round)
        
        for district in self.istanbul_districts:
            if len(self.companies) >= target_count:
                break
            
            logger.info(f"Processing district: {district} ({len(self.companies)}/{target_count} companies found)")
            
            # Scrape from multiple sources per district
            self.scrape_sahibinden_emlak(district)
            if len(self.companies) < target_count:
                self.scrape_hepsiemlak(district)
            if len(self.companies) < target_count:
                self.scrape_google_maps_selenium(district)
            if len(self.companies) < target_count:
                self.scrape_additional_sources(district)
            
            # Progress update
            logger.info(f"District {district} completed. Total companies: {len(self.companies)}")
            
            if len(self.companies) >= target_count:
                break
        
        logger.info(f"Scraping completed. Found {len(self.companies)} companies.")
        return self.companies
    
    def save_to_csv(self, filename="istanbul_emlak_companies.csv"):
        """Save scraped data to CSV file"""
        if not self.companies:
            logger.error("No companies data to save")
            return
        
        # Remove duplicates based on company name and phone
        seen = set()
        unique_companies = []
        for company in self.companies:
            key = (company.get('name', ''), company.get('phone', ''))
            if key not in seen:
                seen.add(key)
                unique_companies.append(company)
        
        # Column order
        column_order = ['name', 'phone', 'website', 'founder', 'district', 'source']
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(unique_companies)
        
        logger.info(f"Saved {len(unique_companies)} unique companies to {filename}")
        
        return filename
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()

def main():
    scraper = IstanbulEmlakScraper()
    
    try:
        # Run the scraper
        companies = scraper.run_scraper(target_count=1000)
        
        # Save to CSV
        filename = scraper.save_to_csv()
        print(f"Scraping completed! Found {len(companies)} companies.")
        print(f"Data saved to: {filename}")
        
        # Display sample data
        if companies:
            print("\nSample companies found:")
            for i, company in enumerate(companies[:5]):
                print(f"{i+1}. {company['name']} - {company['phone']} - {company['district']}")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()