#!/usr/bin/env python3
import csv
import smtplib
import ssl
import time
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional

class EmailSender:
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.smtp_server = self.config["smtp_server"]
        self.smtp_port = self.config["smtp_port"]
        self.sender_email = self.config["sender_email"]
        self.sender_password = self.config["sender_password"]
        self.sender_name = self.config.get("sender_name", "Your Name")
        
    def load_config(self, config_file: str) -> Dict:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file {config_file} not found")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def load_csv_data(self, csv_file: str) -> List[Dict]:
        companies = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append(row)
        return companies
    
    def load_email_template(self, template_file: str) -> tuple:
        with open(template_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            subject = lines[0].replace("Subject: ", "").strip()
            body = ''.join(lines[2:])  # Skip subject line and empty line
        return subject, body
    
    def personalize_message(self, template: str, company_data: Dict) -> str:
        message = template
        for key, value in company_data.items():
            placeholder = f"{{{{{key}}}}}"
            message = message.replace(placeholder, str(value))
        return message
    
    def send_email(self, recipient_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email  # Websupport requires simple email format
            message["To"] = recipient_email
            message["Reply-To"] = self.sender_email
            
            if is_html:
                part = MIMEText(body, "html")
            else:
                part = MIMEText(body, "plain")
            
            message.attach(part)
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")
            return False
    
    def send_bulk_emails(self, csv_file: str, template_file: str, 
                        delay_seconds: float = 1.0, test_mode: bool = False,
                        max_emails: Optional[int] = None):
        
        companies = self.load_csv_data(csv_file)
        subject_template, body_template = self.load_email_template(template_file)
        
        sent_count = 0
        failed_count = 0
        
        if test_mode:
            print("🧪 TEST MODE - Emails will not be sent")
            print("-" * 50)
        
        total_to_send = min(len(companies), max_emails) if max_emails else len(companies)
        
        for i, company in enumerate(companies):
            if max_emails and i >= max_emails:
                break
            
            email = company.get("Email", "").strip()
            
            if not email:
                print(f"⚠️  Skipping {company.get('Company Name', 'Unknown')} - No email address")
                continue
            
            personalized_subject = self.personalize_message(subject_template, company)
            personalized_body = self.personalize_message(body_template, company)
            
            if test_mode:
                print(f"📧 Would send to: {email}")
                print(f"   Company: {company.get('Company Name', 'Unknown')}")
                print(f"   Subject: {personalized_subject}")
                sent_count += 1
            else:
                print(f"📤 Sending email {i+1}/{total_to_send} to {email}...", end=" ")
                
                if self.send_email(email, personalized_subject, personalized_body):
                    print("✅ Sent")
                    sent_count += 1
                else:
                    print("❌ Failed")
                    failed_count += 1
                
                if i < total_to_send - 1:
                    time.sleep(delay_seconds)
        
        print("\n" + "=" * 50)
        print(f"📊 Summary:")
        print(f"   Total companies: {len(companies)}")
        print(f"   Emails sent: {sent_count}")
        print(f"   Failed: {failed_count}")
        print(f"   Skipped: {len(companies) - sent_count - failed_count}")
        
        return sent_count, failed_count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Send bulk emails to companies')
    parser.add_argument('--csv', default='companies.csv', help='CSV file with company data')
    parser.add_argument('--template', default='email_template.txt', help='Email template file')
    parser.add_argument('--config', default='config.json', help='Configuration file')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between emails (seconds)')
    parser.add_argument('--test', action='store_true', help='Test mode - don\'t actually send emails')
    parser.add_argument('--max', type=int, help='Maximum number of emails to send')
    
    args = parser.parse_args()
    
    try:
        print("🚀 Email Sender Started")
        print("=" * 50)
        
        sender = EmailSender(args.config)
        sender.send_bulk_emails(
            csv_file=args.csv,
            template_file=args.template,
            delay_seconds=args.delay,
            test_mode=args.test,
            max_emails=args.max
        )
        
        print("\n✨ Email sending complete!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please ensure all required files exist:")
        print("  - config.json (email configuration)")
        print("  - companies.csv (company data)")
        print("  - email_template.txt (email template)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()