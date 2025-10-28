import re
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import send_mail
import logging
import os, sys
import base64
from bs4 import BeautifulSoup
import gspread

# parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import common

def main():
    
    common.import_log("Retrieve_gmail")
    gmail_service = common.authorize_gmail()

    aws_emails = []
    
    try:
        labels_result = gmail_service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        aws_label_id = None
        
        for label in labels:
            if 'AWS' in label['name'] or label['name'].lower() == 'aws':
                aws_label_id = label['id']
                logging.info(f"Found AWS label: {label['name']} with ID: {aws_label_id}")
                break
        
        if not aws_label_id:
            for label in labels:
                if 'aws' in label['name'].lower():
                    aws_label_id = label['id']
                    logging.info(f"Found AWS nested label: {label['name']} with ID: {aws_label_id}")
                    break
        
        default_maxResults = 1000
        maxResults = input("Enter the maximum number of AWS emails to retrieve (e.g., 1000): ")
        
        if maxResults is None or maxResults.strip() == "":
            maxResults = default_maxResults
        elif maxResults.isdigit():
            maxResults = int(maxResults)
        else:
            maxResults = default_maxResults

        if aws_label_id:
            aws_results = gmail_service.users().messages().list(
                userId='me', 
                labelIds=[aws_label_id],
                maxResults=maxResults
            ).execute()
            aws_messages = aws_results.get('messages', [])
            logging.info(f"Found {len(aws_messages)} messages with AWS label")
            
            # Process AWS emails
            for i, message in enumerate(aws_messages):
                try:
                    print(f"Processing email {i+1}/{len(aws_messages)}")
                    msg = gmail_service.users().messages().get(userId='me', id=message['id']).execute()
                    
                    # Get email headers
                    headers = msg['payload'].get('headers', [])
                    subject = ""
                    sender = ""
                    date = ""
                    
                    for header in headers:
                        if header['name'] == 'Subject':
                            subject = header['value']
                        elif header['name'] == 'From':
                            sender = header['value']
                        elif header['name'] == 'Date':
                            date = header['value']
                    
                    # Get email body
                    body_content = ""
                    
                    def extract_body_from_part(part):
                        """メール本文を再帰的に抽出"""
                        if part.get('parts'):
                            for sub_part in part['parts']:
                                body = extract_body_from_part(sub_part)
                                if body:
                                    return body
                        else:
                            if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                                data = part['body']['data']
                                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            elif part['mimeType'] == 'text/html' and part['body'].get('data'):
                                data = part['body']['data']
                                html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                                soup = BeautifulSoup(html_content, 'html.parser')
                                return soup.get_text()
                        return ""
                    
                    if 'parts' in msg['payload']:
                        body_content = extract_body_from_part(msg['payload'])
                    else:
                        if msg['payload']['body'].get('data'):
                            data = msg['payload']['body']['data']
                            body_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    
                    body_content = body_content.replace('\r\n', '\n').replace('\r', '\n').strip()
                    body_content = re.sub(r'\n{3,}', '\n\n', body_content)
                    
                    if len(body_content) > 2000:  # 長すぎる場合は切り詰める（2000文字に拡張）
                        body_content = body_content[:2000] + "..."
                    
                    aws_emails.append({
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'body': body_content
                    })
                    
                except Exception as e:
                    logging.error(f"Error processing AWS email {message['id']}: {e}")
                    continue
        else:
            # if no AWS label found
            logging.warning("AWS label not found")
            print("AWS label not found. Available labels:")
            for label in labels[:100]: 
                print(f"  - {label['name']} (ID: {label['id']})")
    
    except Exception as e:
        logging.error(f"Error accessing Gmail labels: {e}")
        print(f"Error accessing Gmail labels: {e}")
        return

    # if aws emails found, csv update initiated
    if aws_emails:
        try:
            gc = common.authorize_gsheet()
            
            try:
                workbook = gc.open("gmail_summary")
            except gspread.SpreadsheetNotFound:
                print("Not found")
                return
            except Exception as e:
                logging.error(f"Error opening Google Sheets: {e}")
                print(f"Error opening Google Sheets: {e}")
                return

            try:
                sheet = workbook.worksheet("aws-emails")
                sheet.clear()
            except:
                sheet = workbook.add_worksheet(title="aws-emails", rows="1000", cols="4")

            # Prepare data for sheets
            headers = ['Subject', 'Sender', 'Date', 'Body']
            data = [headers]
            
            for email in aws_emails:
                data.append([
                    email['subject'],
                    email['sender'], 
                    email['date'],
                    email['body']
                ])
            
            # Write to sheet
            sheet.update(values=data, range_name='A1')
            
            logging.info(f"Successfully wrote {len(aws_emails)} AWS emails to Google Sheets")
            print(f"Successfully wrote {len(aws_emails)} AWS emails to Google Sheets")
            print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{workbook.id}")
            
            # Show summary
            print(f"\nAWS Emails Summary:")
            print(f"Total emails: {len(aws_emails)}")
            
            # Count by sender
            sender_counts = {}
            for email in aws_emails:
                sender = email['sender'].split('<')[0].strip() if '<' in email['sender'] else email['sender']
                sender_counts[sender] = sender_counts.get(sender, 0) + 1
            
            print("\nTop senders:")
            for sender, count in sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {sender}: {count} emails")
                
        except Exception as e:
            logging.error(f"Error writing to Google Sheets: {e}")
            print(f"Error writing to Google Sheets: {e}")
    else:
        print("No AWS emails found")
        logging.info("No AWS emails found")

if __name__ == '__main__':
    main()
