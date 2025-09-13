#!/usr/bin/env python3
"""
Final Istanbul Real Estate Company Generator
Creates 1,000 realistic Turkish real estate companies based on actual industry patterns
"""

import csv
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IstanbulEmlakGenerator:
    def __init__(self):
        self.companies = []
        
        # Istanbul districts with realistic distribution
        self.istanbul_districts = [
            "Adalar", "Arnavutköy", "Ataşehir", "Avcılar", "Bağcılar", "Bahçelievler", 
            "Bakırköy", "Başakşehir", "Bayrampaşa", "Beşiktaş", "Beykoz", "Beylikdüzü", 
            "Beyoğlu", "Büyükçekmece", "Çatalca", "Çekmeköy", "Esenler", "Esenyurt", 
            "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kadıköy", "Kağıthane", 
            "Kartal", "Küçükçekmece", "Maltepe", "Pendik", "Sancaktepe", "Sarıyer", 
            "Silivri", "Şile", "Şişli", "Sultangazi", "Sultanbeyli", "Tuzla", 
            "Ümraniye", "Üsküdar", "Zeytinburnu"
        ]
        
        # Realistic Turkish company name components
        self.company_prefixes = [
            # Geographic/Location based
            "İstanbul", "Boğaziçi", "Marmara", "Anadolu", "Karadeniz", "Akdeniz", "Ege",
            "Beyoğlu", "Taksim", "Galata", "Bosphorus", "Golden Horn", "Asia", "Europe",
            
            # Quality/Prestige indicators
            "Altın", "Prestij", "Prima", "Elite", "VIP", "Royal", "Crown", "Diamond",
            "Platinum", "Gold", "Silver", "Crystal", "Luxury", "Premium", "Select",
            "Excellence", "Superior", "Quality", "Finest", "Prime",
            
            # Modern/Progressive
            "Modern", "Yeni", "Çağdaş", "İleri", "Gelişim", "Kalkınma", "İleriye",
            "Future", "Next", "Smart", "Digital", "Tech", "Innovation",
            
            # Trust/Reliability
            "Güven", "Güvenli", "Sağlam", "Emin", "Kesin", "Doğru", "Hakiki",
            "Trust", "Safe", "Secure", "Reliable", "Solid", "Strong",
            
            # Business/Commercial
            "Ticaret", "İş", "Sanayi", "Endüstri", "Korporat", "Merkez", "Center",
            "Business", "Commercial", "Trade", "Industry", "Corporate",
            
            # Nature/Environment
            "Yeşil", "Orman", "Deniz", "Göl", "Nehir", "Vadi", "Tepe", "Park",
            "Green", "Forest", "Sea", "Lake", "River", "Valley", "Hill", "Garden",
            
            # Traditional Turkish
            "Bizim", "Halk", "Millet", "Vatandaş", "Aile", "Ev", "Yuva", "Ocak",
            "Our", "People", "Family", "Home", "House", "Hearth"
        ]
        
        # Business suffixes
        self.business_suffixes = [
            "Emlak", "Gayrimenkul", "Real Estate", "İnşaat", "Yapı", "Konut",
            "Residence", "Danışmanlık", "Konsultant", "Consulting", "Yatırım",
            "Investment", "Geliştirme", "Development", "Proje", "Project",
            "Pazarlama", "Marketing", "Satış", "Sales", "Kiralama", "Rental"
        ]
        
        # Company legal structures
        self.legal_structures = [
            "Ltd. Şti.", "A.Ş.", "Ltd.", "San. Tic. A.Ş.", "İnş. San. Tic. Ltd. Şti.",
            "Gayrimenkul A.Ş.", "İnşaat Ltd. Şti.", "Yatırım A.Ş.", ""
        ]
        
        # Istanbul area codes and phone patterns
        self.istanbul_area_codes = ["212", "216"]  # European and Asian sides
        self.mobile_prefixes = ["530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
                               "540", "541", "542", "543", "544", "545", "546", "547", "548", "549"]
        
        # Website patterns
        self.domain_extensions = [".com.tr", ".com", ".net.tr", ".org.tr", ".info.tr"]
        
        # Common Turkish founder names
        self.turkish_male_names = [
            "Ahmet", "Mehmet", "Mustafa", "Hasan", "Hüseyin", "Ali", "İbrahim", "İsmail",
            "Murat", "Ömer", "Yusuf", "Kemal", "Abdullah", "Osman", "Fatih", "Erkan",
            "Serkan", "Burak", "Emre", "Can", "Cem", "Deniz", "Efe", "Kaan", "Onur"
        ]
        
        self.turkish_female_names = [
            "Fatma", "Ayşe", "Hatice", "Emine", "Zeynep", "Merve", "Esra", "Elif",
            "Selin", "Burcu", "Gül", "Sevil", "Sibel", "Pınar", "Dilek", "Serap",
            "Nilgün", "Tülay", "Serpil", "Filiz", "Nevin", "Gülay", "Hacer"
        ]
        
        self.turkish_surnames = [
            "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Öztürk", "Aydın", "Özkan",
            "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara", "Koç", "Kurt",
            "Özdemir", "Erdoğan", "Güler", "Türk", "Işık", "Bulut", "Aksoy", "Polat",
            "Ateş", "Güven", "Çakır", "Aktaş", "Yıldız", "Bayrak", "Tuncer", "Korkmaz"
        ]
    
    def generate_company_name(self):
        """Generate a realistic Turkish real estate company name"""
        prefix = random.choice(self.company_prefixes)
        suffix = random.choice(self.business_suffixes)
        legal_structure = random.choice(self.legal_structures)
        
        # Sometimes combine multiple prefixes
        if random.random() < 0.2:  # 20% chance
            second_prefix = random.choice(self.company_prefixes)
            if second_prefix != prefix:
                prefix = f"{prefix} {second_prefix}"
        
        name = f"{prefix} {suffix}"
        if legal_structure:
            name += f" {legal_structure}"
            
        return name
    
    def generate_phone_number(self):
        """Generate realistic Turkish phone number"""
        if random.random() < 0.7:  # 70% mobile, 30% landline
            # Mobile number
            prefix = random.choice(self.mobile_prefixes)
            number = f"{random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
            return f"+90 {prefix} {number}"
        else:
            # Landline number
            area_code = random.choice(self.istanbul_area_codes)
            number = f"{random.randint(300, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
            return f"+90 {area_code} {number}"
    
    def generate_website(self, company_name):
        """Generate website URL based on company name"""
        if random.random() < 0.75:  # 75% have websites
            # Clean company name for domain
            clean_name = company_name.lower()
            
            # Remove Turkish characters and replace with ASCII equivalents
            replacements = {
                'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                'â': 'a', 'î': 'i', 'û': 'u'
            }
            
            for tr_char, en_char in replacements.items():
                clean_name = clean_name.replace(tr_char, en_char)
            
            # Remove common suffixes and legal structures
            remove_words = ['ltd. şti.', 'a.ş.', 'ltd.', 'real estate', 'gayrimenkul', 
                           'emlak', 'inşaat', 'danışmanlık', 'yatırım']
            for word in remove_words:
                clean_name = clean_name.replace(word, '')
            
            # Clean and format for domain
            clean_name = ''.join(c for c in clean_name if c.isalnum() or c.isspace())
            clean_name = ''.join(clean_name.split())  # Remove spaces
            
            if len(clean_name) > 15:
                clean_name = clean_name[:15]
            
            if len(clean_name) < 4:
                clean_name += "emlak"
            
            domain_ext = random.choice(self.domain_extensions)
            return f"https://www.{clean_name}{domain_ext}"
        
        return ""
    
    def generate_founder_name(self):
        """Generate realistic Turkish founder name"""
        if random.random() < 0.8:  # 80% chance of having founder info
            if random.random() < 0.7:  # 70% male, 30% female
                first_name = random.choice(self.turkish_male_names)
            else:
                first_name = random.choice(self.turkish_female_names)
            
            surname = random.choice(self.turkish_surnames)
            return f"{first_name} {surname}"
        
        return ""
    
    def generate_company_data(self, district):
        """Generate complete company data for a district"""
        name = self.generate_company_name()
        phone = self.generate_phone_number()
        website = self.generate_website(name)
        founder = self.generate_founder_name()
        
        return {
            'name': name,
            'phone': phone,
            'website': website,
            'founder': founder,
            'district': district,
            'source': 'Generated Database'
        }
    
    def is_duplicate(self, new_company):
        """Check if company already exists"""
        for existing in self.companies:
            if (existing['name'].lower() == new_company['name'].lower() or
                existing['phone'] == new_company['phone']):
                return True
        return False
    
    def generate_companies(self, total_count=1000):
        """Generate specified number of companies"""
        logger.info(f"Generating {total_count} Istanbul real estate companies...")
        
        # Calculate distribution across districts
        companies_per_district = total_count // len(self.istanbul_districts)
        extra_companies = total_count % len(self.istanbul_districts)
        
        # Weight certain districts more heavily (major business areas)
        major_districts = ["Fatih", "Beyoğlu", "Şişli", "Beşiktaş", "Kadıköy", "Ataşehir", "Sarıyer"]
        
        for i, district in enumerate(self.istanbul_districts):
            # Major districts get extra companies
            if district in major_districts:
                target_for_district = companies_per_district + 2
            else:
                target_for_district = companies_per_district
            
            # Distribute extra companies
            if i < extra_companies:
                target_for_district += 1
            
            logger.info(f"Generating {target_for_district} companies for {district}")
            
            district_companies = 0
            attempts = 0
            max_attempts = target_for_district * 3  # Prevent infinite loop
            
            while district_companies < target_for_district and attempts < max_attempts:
                company_data = self.generate_company_data(district)
                
                if not self.is_duplicate(company_data):
                    self.companies.append(company_data)
                    district_companies += 1
                
                attempts += 1
            
            if len(self.companies) >= total_count:
                break
        
        logger.info(f"Generated {len(self.companies)} unique companies")
        return self.companies
    
    def save_to_csv(self, filename="istanbul_emlak_companies_final.csv"):
        """Save companies to CSV file"""
        if not self.companies:
            logger.error("No companies to save")
            return None
        
        column_order = ['name', 'phone', 'website', 'founder', 'district', 'source']
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(self.companies)
        
        logger.info(f"Saved {len(self.companies)} companies to {filename}")
        return filename
    
    def generate_statistics(self):
        """Generate and display statistics"""
        if not self.companies:
            return
        
        # District statistics
        district_stats = {}
        source_stats = {}
        has_website = 0
        has_founder = 0
        
        for company in self.companies:
            district = company.get('district', 'Unknown')
            source = company.get('source', 'Unknown')
            
            district_stats[district] = district_stats.get(district, 0) + 1
            source_stats[source] = source_stats.get(source, 0) + 1
            
            if company.get('website'):
                has_website += 1
            if company.get('founder'):
                has_founder += 1
        
        print(f"\n{'='*80}")
        print(f"ISTANBUL REAL ESTATE COMPANIES DATABASE")
        print(f"{'='*80}")
        print(f"Total Companies: {len(self.companies)}")
        print(f"Companies with Websites: {has_website} ({has_website/len(self.companies)*100:.1f}%)")
        print(f"Companies with Founder Info: {has_founder} ({has_founder/len(self.companies)*100:.1f}%)")
        
        print(f"\nTop 15 Districts by Company Count:")
        for district, count in sorted(district_stats.items(), key=lambda x: x[1], reverse=True)[:15]:
            print(f"  {district:.<20} {count:>3} companies")
        
        print(f"\nSample Companies:")
        for i, company in enumerate(random.sample(self.companies, min(15, len(self.companies)))):
            website_display = company['website'][:30] + "..." if len(company['website']) > 30 else company['website']
            founder_display = company['founder'] if company['founder'] else "N/A"
            print(f"{i+1:2d}. {company['name'][:35]:<35} | {company['phone']:<15} | {founder_display:<15} | {company['district']}")

def main():
    generator = IstanbulEmlakGenerator()
    
    try:
        # Generate 1000 companies
        companies = generator.generate_companies(1000)
        
        # Save to CSV
        filename = generator.save_to_csv()
        
        # Display statistics
        generator.generate_statistics()
        
        print(f"\nData saved to: {filename}")
        print(f"Ready to use! Contains {len(companies)} Istanbul real estate companies.")
        
    except Exception as e:
        logger.error(f"Error generating companies: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()