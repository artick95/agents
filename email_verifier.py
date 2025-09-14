#!/usr/bin/env python3
"""
Advanced Email Verification System
Tests email deliverability for Istanbul real estate companies
"""

import csv
import dns.resolver
import socket
import smtplib
import re
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailVerifier:
    def __init__(self, sending_domain="gatesweb.top"):
        self.sending_domain = sending_domain
        self.verified_count = 0
        self.bad_count = 0
        self.companies = []
        
        # DNS resolver configuration
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        self.resolver.lifetime = 5
        
        # Common disposable email domains to filter out
        self.disposable_domains = {
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 
            'tempmail.org', 'throwaway.email', 'example.com', 'test.com'
        }
        
        # Turkish ISP and business email domains (more likely to be valid)
        self.trusted_turkish_domains = {
            'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com',
            'turk.net', 'superonline.com', 'mynet.com', 'ttnet.net.tr',
            'com.tr', 'net.tr', 'org.tr', 'info.tr', 'biz.tr'
        }
    
    def validate_email_format(self, email):
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.lower()) is not None
    
    def check_domain_mx_record(self, domain):
        """Check if domain has valid MX record"""
        try:
            mx_records = self.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except Exception as e:
            logger.debug(f"MX record check failed for {domain}: {e}")
            return False
    
    def check_domain_exists(self, domain):
        """Check if domain exists (has A record)"""
        try:
            a_records = self.resolver.resolve(domain, 'A')
            return len(a_records) > 0
        except Exception as e:
            logger.debug(f"Domain check failed for {domain}: {e}")
            return False
    
    def test_smtp_connection(self, email):
        """Test SMTP connection without sending email"""
        domain = email.split('@')[1]
        
        try:
            # Get MX record
            mx_records = self.resolver.resolve(domain, 'MX')
            mx_record = str(mx_records[0].exchange)
            
            # Test SMTP connection
            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)
            
            # Connect to mail server
            server.connect(mx_record, 25)
            server.helo(self.sending_domain)
            
            # Test sender and recipient
            code, message = server.mail(f"test@{self.sending_domain}")
            if code != 250:
                server.quit()
                return False
                
            code, message = server.rcpt(email)
            server.quit()
            
            # 250 = OK, 251 = User not local (but will forward)
            return code in [250, 251]
            
        except Exception as e:
            logger.debug(f"SMTP test failed for {email}: {e}")
            return False
    
    def check_domain_reputation(self, domain):
        """Check basic domain reputation indicators"""
        try:
            # Check if domain is in trusted Turkish domains
            if any(trusted in domain for trusted in self.trusted_turkish_domains):
                return True
            
            # Check if domain is disposable
            if domain in self.disposable_domains:
                return False
            
            # Check domain age (simplified - just check if it resolves)
            return self.check_domain_exists(domain)
            
        except Exception as e:
            logger.debug(f"Reputation check failed for {domain}: {e}")
            return False
    
    def verify_email_comprehensive(self, email):
        """Comprehensive email verification"""
        if not email or '@' not in email:
            return "BAD"
        
        email = email.lower().strip()
        domain = email.split('@')[1]
        
        # Step 1: Format validation
        if not self.validate_email_format(email):
            logger.debug(f"Invalid format: {email}")
            return "BAD"
        
        # Step 2: Domain exists check
        if not self.check_domain_exists(domain):
            logger.debug(f"Domain doesn't exist: {domain}")
            return "BAD"
        
        # Step 3: MX record check
        if not self.check_domain_mx_record(domain):
            logger.debug(f"No MX record: {domain}")
            return "BAD"
        
        # Step 4: Domain reputation
        if not self.check_domain_reputation(domain):
            logger.debug(f"Poor domain reputation: {domain}")
            return "BAD"
        
        # Step 5: SMTP connection test (more thorough but slower)
        try:
            if self.test_smtp_connection(email):
                logger.debug(f"SMTP test passed: {email}")
                return "200"
            else:
                logger.debug(f"SMTP test failed: {email}")
                return "BAD"
        except Exception as e:
            logger.debug(f"SMTP test error for {email}: {e}")
            # If SMTP test fails due to network issues, but other tests pass, consider it OK
            return "200"
    
    def verify_email_batch(self, emails_batch):
        """Verify a batch of emails"""
        results = []
        for email in emails_batch:
            try:
                result = self.verify_email_comprehensive(email)
                results.append(result)
                
                # Add small delay to avoid overwhelming servers
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error verifying {email}: {e}")
                results.append("BAD")
        
        return results
    
    def load_companies_from_csv(self, filename):
        """Load companies from CSV"""
        logger.info(f"Loading companies from {filename}")
        
        with open(filename, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            self.companies = list(reader)
        
        logger.info(f"Loaded {len(self.companies)} companies")
        return self.companies
    
    def verify_all_emails(self, max_workers=3):
        """Verify all emails in the dataset with parallel processing"""
        logger.info("Starting comprehensive email verification...")
        
        # Extract emails
        emails = [company.get('email', '') for company in self.companies]
        
        # Process in batches with threading
        batch_size = 50
        batches = [emails[i:i + batch_size] for i in range(0, len(emails), batch_size)]
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit batches for processing
            future_to_batch = {
                executor.submit(self.verify_email_batch, batch): batch 
                for batch in batches
            }
            
            # Collect results
            for i, future in enumerate(as_completed(future_to_batch)):
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                    
                    logger.info(f"Verified batch {i+1}/{len(batches)} ({len(all_results)}/{len(emails)} emails)")
                    
                except Exception as e:
                    batch = future_to_batch[future]
                    logger.error(f"Batch verification failed: {e}")
                    # Add BAD for failed batch
                    all_results.extend(["BAD"] * len(batch))
        
        # Add verification results to companies
        for i, company in enumerate(self.companies):
            if i < len(all_results):
                company['email_verification'] = all_results[i]
            else:
                company['email_verification'] = "BAD"
        
        # Count results
        self.verified_count = sum(1 for result in all_results if result == "200")
        self.bad_count = sum(1 for result in all_results if result == "BAD")
        
        logger.info(f"Email verification completed:")
        logger.info(f"  Verified (200): {self.verified_count}")
        logger.info(f"  Bad emails: {self.bad_count}")
        logger.info(f"  Success rate: {self.verified_count/len(all_results)*100:.1f}%")
        
        return self.companies
    
    def save_verified_csv(self, filename):
        """Save companies with verification results"""
        if not self.companies:
            logger.error("No companies to save")
            return None
        
        # Define column order including verification
        column_order = ['name', 'phone', 'website', 'email', 'email_verification', 
                       'founder', 'district', 'source', 'email_source']
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(self.companies)
        
        logger.info(f"Verified dataset saved to {filename}")
        return filename
    
    def get_verification_statistics(self):
        """Get detailed verification statistics"""
        if not self.companies:
            return {}
        
        stats = {
            'total_companies': len(self.companies),
            'verified_emails': self.verified_count,
            'bad_emails': self.bad_count,
            'success_rate': self.verified_count / len(self.companies) * 100,
            'needs_expansion': self.verified_count < 1000
        }
        
        return stats
    
    def filter_verified_companies(self):
        """Return only companies with verified emails"""
        return [company for company in self.companies 
                if company.get('email_verification') == "200"]
    
    def generate_verification_report(self):
        """Generate detailed verification report"""
        stats = self.get_verification_statistics()
        
        print(f"\n{'='*80}")
        print(f"EMAIL VERIFICATION REPORT - GATESWEB.TOP DELIVERABILITY TEST")
        print(f"{'='*80}")
        print(f"Total Companies Tested: {stats['total_companies']}")
        print(f"✅ Verified Deliverable (200): {stats['verified_emails']}")
        print(f"❌ Bad/Non-deliverable: {stats['bad_emails']}")
        print(f"📊 Success Rate: {stats['success_rate']:.1f}%")
        
        if stats['needs_expansion']:
            print(f"\n⚠️  EXPANSION NEEDED:")
            print(f"   Current verified emails: {stats['verified_emails']}")
            print(f"   Target: 2,000+ verified emails")
            print(f"   Need to add: {2000 - stats['verified_emails']} more companies")
        else:
            print(f"\n🎉 TARGET ACHIEVED: {stats['verified_emails']} verified emails!")
        
        # Show sample verified emails
        verified_companies = self.filter_verified_companies()
        if verified_companies:
            print(f"\nSample Verified Emails:")
            for i, company in enumerate(verified_companies[:10]):
                print(f"{i+1:2d}. {company['email']:<35} | {company['name'][:30]}")
        
        return stats

def main():
    verifier = EmailVerifier(sending_domain="gatesweb.top")
    
    try:
        # Load existing companies
        companies = verifier.load_companies_from_csv('istanbul_emlak_companies_with_emails.csv')
        
        # Verify all emails
        verified_companies = verifier.verify_all_emails(max_workers=2)  # Reduced for stability
        
        # Save verified dataset
        output_filename = 'istanbul_emlak_verified_emails.csv'
        verifier.save_verified_csv(output_filename)
        
        # Generate report
        stats = verifier.generate_verification_report()
        
        print(f"\n📁 Verified dataset saved to: {output_filename}")
        
        return stats['verified_emails']
        
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    main()