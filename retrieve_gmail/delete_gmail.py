import pandas as pd
import boto3
import logging
import os, sys
import base64
import search_words as search_words

# parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import common

def get_message_body(payload):
    
    """Extract message body from Gmail API payload"""
    body = ""
    
    if 'parts' in payload:
        # Multi-part message
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                if 'data' in part['body']:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        # Single part message
        if payload['mimeType'] == 'text/plain' or payload['mimeType'] == 'text/html':
            if 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
    return body


def main():
    
    logging.info("Gmail deletion process started.")
    deleted_messages = []
    skipped_messages = []
    script_title = "Delete_gmail"

    common.import_log(script_title)
    gmail_service = common.authorize_gmail()
    messages = []
    
    # Get messages from Gmail
    response = gmail_service.users().messages().list(
        userId='me',
        maxResults=20000
    ).execute()
    
    if 'messages' in response:
        messages = response.get('messages', [])

    for message in messages:
        msg = gmail_service.users().messages().get(
            userId='me', 
            id=message['id']
        ).execute()
        
        # Get message body content
        message_body = get_message_body(msg['payload'])
        message_snippet = msg.get('snippet', '')

        search_subjects = search_words.delete_words()[0]
        search_content = search_words.delete_words()[1]
        search_sender = search_words.delete_words()[2]
        
        if not search_subjects:
            logging.error("No search terms provided. Exiting.")
            os._exit(1)

        # Search in both subject and content
        subject = ""
        for header in msg['payload'].get('headers', []):
            if header['name'] == 'Subject':
                subject = header['value']
                print(f"Subject: {subject}")
                break
        
        found_in_subject = any(term in subject for term in search_subjects)
        # found_in_content = any(term in message_snippet or term in message_body for term in search_content)
        
        # sender e-mail address
        # sender = ""
        # for header in msg['payload'].get('headers', []):
        #     if header['name'] == 'Sender':
        #         sender = header['value']
        #         print(f"Sender: {sender}")
        #         break
        
        # found_in_sender = any(term in sender for term in search_sender)

        if found_in_subject:
            # Get subject for logging
            subject = ""
            for header in msg['payload'].get('headers', []):
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            
            # Display message info
            print(f"\n--- Found Message ---")
            print(f"Subject: {subject}")
            print(f"Snippet: {message_snippet[:100]}...")
            print(f"Body preview: {message_body[:200]}...")
            print(f"Message ID: {message['id']}")
            
            logging.info(f"Found message with search terms. ID: {message['id']}, Subject: {subject}")
            
            # if input("Delete this message? (y/n): ").strip().lower() == 'y':

            try:
                gmail_service.users().messages().delete(userId='me', id=message['id']).execute()
                logging.info(f"Deleted message with ID: {message['id']}")
                print(f"Deleted message with ID: {message['id']}")
                deleted_messages.append(subject if subject else f"No Subject (ID: {message['id']})")
            except Exception as e:
                logging.error(f"Error deleting message with ID: {message['id']}. Error: {e}")
                print(f"Error deleting message with ID: {message['id']}. Error: {e}")
                deleted_messages.append(f"Failed to delete (ID: {message['id']})")

            # else:
            #     logging.info(f"Skipped deletion for message with ID: {message['id']}")
            #     print(f"Skipped deletion for message with ID: {message['id']}")
            #     skipped_messages.append(message['id'])
    
    # Send summary email
    summary_msg = [
        f"Gmail deletion process completed.",
        f"",
        f"Number of deleted messages: {len(deleted_messages)}",
        f"",
        f"Deleted messages subjects:",
    ]
    
    # Add each subject as a separate line for better readability
    for i, subject in enumerate(deleted_messages, 1):
        summary_msg.append(f"{i}. {subject}")
    
    summary_msg.extend([
        f"",
        f"The number of skipped messages: {len(skipped_messages)}",
        f"The number of total processed: {len(deleted_messages) + len(skipped_messages)}"
    ])
    
    logging.info("\n".join(summary_msg))
    
    try:
        ssm_client = boto3.client('ssm', region_name='ap-southeast-2')
        common.send_mail(ssm_client, script_title, summary_msg)
    except Exception as e:
        logging.error(f"Error sending summary email: {e}")
        print(f"Error sending summary email: {e}")

    logging.info("Gmail deletion process completed.")

if __name__ == '__main__':
    main()