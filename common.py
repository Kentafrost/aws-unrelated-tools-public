import gspread
import pickle
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, logging, time
import json

with open("secret_path.json", "r") as f:
    secret_path = json.load(f)

base_path = secret_path[0]["gdrive_credentials"]

def authorize_gmail():

    gmail_cred = os.path.join(base_path, "OAuth_credentials.json")

    try:
        scope = secret_path[0]["mail_scope"]

        creds = None
        token_file = os.path.join(base_path, "token.pickle")

        # Load existing credentials if available
        if os.path.exists(token_file):
            with open(token_file, "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing expired credentials.")
                creds.refresh(Request())
            else:
                logging.info("No existing token found, starting new authentication flow.")
                flow = InstalledAppFlow.from_client_secrets_file(gmail_cred, scope)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(token_file, "wb") as token:
                pickle.dump(creds, token)
        
        gmail_service = build('gmail', 'v1', credentials=creds)
        logging.info("Gmail service authorized successfully.")
        
        return gmail_service
            
    except Exception as e:
        logging.error('Googleの認証処理でエラーが発生しました。{}'.format(e))
        print(f"Error: {e}")
        os._exit(1)


def authorize_gsheet():
    gsheet_cred = os.path.join(base_path, "credentials.json")

    try:
        scope = secret_path[0]["sheet_scope"]
        
        credentials = Credentials.from_service_account_file(
            gsheet_cred, scopes=scope
        )
        
        # Authorize the gspread client
        gspread_client = gspread.authorize(credentials)
        logging.info("Google Sheets service authorized successfully.")

        return gspread_client

    except Exception as e:
        logging.error('Googleの認証処理でエラーが発生しました。{}'.format(e))
        print(f"Error: {e}")
        os._exit(1)
    
def import_log(script_name):

    current_time = time.strftime("%Y%m%d_%H%M%S")
    this_dir = os.path.dirname(os.path.abspath(__file__))

    log_dir = f"{this_dir}\\log\\{script_name}\\"
    os.makedirs(log_dir, exist_ok=True)
    log_file = f"{log_dir}\\{current_time}_task.log"

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='shift_jis'
    )


def send_mail(ssm_client, script_title, msg_list):
    
    import logging
    import smtplib

    logging.info('メール送信処理を開始します。')
    try:
        subject = f"Script : {script_title}"
        bodyText = "Here's the report:\n" + "\n" + "\n".join(map(str, msg_list))
        # メールの内容(SSMから取得)
        from_address = ssm_client.get_parameter(Name='my_main_gmail_address', WithDecryption=True)['Parameter']['Value']
        from_pw = ssm_client.get_parameter(Name='my_main_gmail_password', WithDecryption=True)['Parameter']['Value']
        to_address = from_address
    except Exception as e:
        logging.error('メールの内容をSSMから取得できませんでした。{}'.format(e))
        return

    try:
        message = f"Subject: {subject}\nTo: {to_address}\nFrom: {from_address}\n\n{bodyText}".encode('utf-8')
        if "gmail.com" in to_address:
            port = 465
            with smtplib.SMTP_SSL('smtp.gmail.com', port) as smtp_server:
                smtp_server.login(from_address, from_pw)
                smtp_server.sendmail(from_address, to_address, message)
            print("gmail送信処理完了。")
            logging.info('正常にgmail送信完了')
        elif "outlook.com" in to_address:
            port = 587
            with smtplib.SMTP('smtp.office365.com', port) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(from_address, from_pw)
                smtp_server.sendmail(from_address, to_address, message)
            print("Outlookメール送信処理完了。")
            logging.info('Outlookメール送信完了')
        else:
            logging.error(f"未対応のメールアドレスドメイン: {to_address}")
            print(f"未対応のメールアドレスドメイン: {to_address}")
    except Exception as e:
        logging.error('メール送信処理でエラーが発生しました。{}'.format(e))
        print(f"メール送信処理でエラーが発生しました: {e}")
        
