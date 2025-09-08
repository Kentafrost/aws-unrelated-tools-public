import os
import logging
import gspread
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def send_mail(client, attachment_path):
    logging.info('メール送信処理を開始します。')
    try:
        from_address = client.get_parameter(Name='my_main_gmail_address', 
                                            WithDecryption=True)['Parameter']['Value']
        from_pw = client.get_parameter(Name='my_main_gmail_password', 
                                       WithDecryption=True)['Parameter']['Value']  
        to_address = from_address

        # Create MIME message
        msg = MIMEMultipart()
        msg['Subject'] = "Rakuten cards fee summary"
        msg['From'] = from_address
        msg['To'] = to_address

        body = "This is the report of cost used in Rakuten card"
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment
        with open(attachment_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', 
                           filename=os.path.basename(attachment_path))
            msg.attach(img)

    except Exception as e:
        logging.error('メールの内容をSSMから取得できませんでした。{}'.format(e))
    
    try:
        # message = f"Subject: {subject}\nTo: {to_address}\nFrom: {from_address}\n\n{bodyText}".encode('utf-8') # メールの内容をUTF-8でエンコード

        if "gmail.com" in to_address:
            port = 465
            mail_type = 'gmail'
            with smtplib.SMTP_SSL('smtp.gmail.com', port) as smtp_server:
                smtp_server.login(from_address, from_pw)
                smtp_server.send_mail(from_address, to_address, msg)

        elif "outlook.com" in to_address:
            port = 587
            mail_type = 'outlook'
            with smtplib.SMTP('smtp.office365.com', port) as smtp_server:
                smtp_server.starttls()  # Enable security FIRST            
                smtp_server.login(from_address, from_pw)
                smtp_server.send_mail(from_address, to_address, msg)
        
        logging.info(f'{mail_type}メール送信完了')
        
            
    except Exception as e:
        logging.error('メール送信処理でエラーが発生しました。{}'.format(e))
    else:
        logging.info('メール送信処理を中止します。')
        return None
    