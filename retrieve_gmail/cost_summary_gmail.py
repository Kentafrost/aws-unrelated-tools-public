import re
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import send_mail
import logging
import os, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import common
base_dir = os.path.abspath(os.path.dirname(__file__))

def main():
    
    common.import_log("Retrieve_gmail")
    gmail_service = common.authorize_gmail()
    messages = []

    page_token = None
    while len(messages) < 200:  # Set your limit
        response = gmail_service.users().messages().list(
            userId='me',
            maxResults=200,  # Adjust batch size
            pageToken=page_token
        ).execute()

        if 'messages' in response:
            messages.extend(response.get('messages', []))

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    cost_list = []
    date_list = []
    online_learning_list = []
    online_learning_enrolled_list = []

    for message in messages:
        msg = gmail_service.users().messages().get(
            userId='me', 
            id=message['id']
        ).execute()
        
        # msg = gmail_service.users().messages().list(userId='me', id=message['id']).execute()
        if "楽天カード" and "カードのご利用があったことを迅速にお知らせ" in msg['snippet']:
            
            pattern = r'本人 *([\d,]+) 円'
            matches = re.findall(pattern, msg['snippet'])
            if matches:
                cost = int(matches[0].replace(',', ''))
                cost_list.append(cost)
            
            # date
            pattern = r'ご利用金額 (\d{4}/\d{2}/\d{2}) 本人'
            matches = re.findall(pattern, msg['snippet'])
            if matches:
                # to date type
                # date = datetime.strptime(matches[0], '%Y/%m/%d').date()
                date_list.append(matches[0])
            
        # Coursera certificate
        elif "Coursera" and "Congratulations! Your Certificate is Ready"in msg['snippet']:
            # print(msg['snippet'])
            online_learning_list.append(msg['snippet'])
            
        elif "Coursera" and "Welcome to the Specialization!" or "We’re thrilled you enrolled" in msg['snippet']:

            # print(msg['snippet'])
            pattern = r'you enrolled in (.+?) on Coursera'
            matches = re.findall(pattern, msg['snippet'])
            if matches:
                online_learning_enrolled_list.append(matches[0])
    
    msg = (
        f"Total cost I spent in Rakuten Card: {sum(cost_list)}円" +
        f"\nNumbers of course completed in Coursera: {len(online_learning_list)}" +
        f"\nNumbers of course enrolled in Coursera: {len(online_learning_enrolled_list)}"
    )
    logging.info(msg)

    with open(f"{base_dir}\\Retrieve_gmail\\rakuten_cost.txt", "w") as f:
        f.write(msg)
    
    cost_list = sorted(cost_list)
    date_list = sorted(date_list)
    
    gc = common.authorize_gsheet()
    workbook = gc.open("gmail_summary")
    sheet_name = "cost-summary"
    sheet = workbook.worksheet(sheet_name)
    sheet.clear()

    if cost_list:
        data = [['Card Date', 'Card Cost']]
        data.extend(zip(date_list, cost_list))
        
        sheet.update(values=data, range_name='A1')

        # for date, cost in zip(date_list, cost_list):
        #     print(date, cost)
        
        df = pd.DataFrame({
            'Card Date': date_list,
            'Card Cost': cost_list
        })
        
        # 2025/01/01 ⇒ 2025/01(all sum up)
        df['Month'] = pd.to_datetime(df['Card Date']).dt.strftime('%Y/%m')
        
        pivot_table = pd.pivot_table(
            df, 
            index=['Month'],
            values=['Rakuten Card Cost'],
            aggfunc='sum'
            )
        print(pivot_table)
        
        graph_title = "Rakuten Card Cost by Month"
        png_title = graph_title.replace(" ", "_") + ".png"

        # make a bar plot
        pivot_table.plot(kind='bar', title=graph_title)
        plt.xlabel('Month')
        plt.ylabel('Cost')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        plt.savefig(f'{base_dir}\\Retrieve_gmail\\{png_title}', 
                    dpi=300, bbox_inches='tight')
        pivot_png_path = f"{base_dir}\\Retrieve_gmail\\{png_title}"
        sheet_name = "Pivot_tbl"    
       
        # insert pivot table to google sheet
        sheet = workbook.worksheet(sheet_name)
        sheet.clear()
        
        pivot_reset = pivot_table.reset_index()
        pivot_data = [pivot_reset.columns.tolist()] + pivot_reset.values.tolist()

        sheet.update(values=pivot_data, range_name='A1')

        ssm_client = boto3.client('ssm', region_name='ap-southeast-2')
        send_mail(ssm_client, pivot_png_path)
        
    # get most recent data from date_list
    if date_list:
        most_recent_date = date_list[1]
        min_recent_date = min(date_list)
        print(f"Most recent date of Rakuten Card usage: {most_recent_date}")
        print(f"Most old date of Rakuten Card usage: {min_recent_date}")
    else:
        print("No Rakuten Card usage data found.")
        
if __name__ == '__main__':
    main()
    
    