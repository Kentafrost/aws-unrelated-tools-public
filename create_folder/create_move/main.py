import concurrent
import pandas as pd
import time
import os, sys
import boto3
import logging
import upload_local
import common_tool

# parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import common

def read_config(config_path):
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key.strip()] = value.strip()
    return config


def main(sheet_name, workbook, remote_chk):
    
    sheet = workbook.worksheet(sheet_name)
    data = sheet.get_all_values()
    df = pd.DataFrame(data)
    extension = ".mp4"

    for index, row in df.iterrows():
        if remote_chk == "y":
            base_path = base_path.replace("D:", "Z:")
        if not row[1] == "BasePath":

            chara_name = row[0].replace(" ","")
            base_path = row[1]
     
            # case 1: local files
            destination_folder = upload_local.folder_path_create(sheet_name, chara_name, base_path, workbook) # define destination folder path
            print(f"Creating local folder: {destination_folder}")

            upload_local.create_folder(destination_folder)
            result = upload_local.move_to_folder(destination_folder, chara_name, extension, sheet_name)
            common_tool.delete_path(destination_folder) # to delete unnecessary folder

    if result == "Success":
        msg = f"{sheet_name}: 処理完了"
        logging.info(f"Sheet name({sheet_name}): 処理完了")
    else:
        msg = f"{sheet_name}' 処理失敗"
        logging.info(f"Sheet name({sheet_name}): 処理失敗")
    return msg, base_path


def parallel_process_sheet(sheet):

    result = main(sheet, workbook, remote_chk)
    logging.info(f"Processing {sheet} is complete.")
    
    return result


if __name__ == "__main__":

    script_name = "Create_Folder"    
    common.import_log(script_name)
    
    current_time = time.strftime("%Y%m%d_%H%M%S")
    logging.info(f"{current_time}: Script({script_name}) started.")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config = read_config(f'{current_dir}\\config.txt')

    if config.get("flg_filepath"):
        flg_filepath = config.get("flg_filepath")
    else:
        flg_filepath = input("Do you want to list file path? (y/n): ")
    
    if config.get("remote_chk"):
        remote_chk = config.get("remote_chk")
    else:
        remote_chk = input("Are you accessing remotely? (y/n): ")
    
    gc = common.authorize_gsheet() # google Authorizations
    workbook = gc.open("chara_name_list")
    
    sheet_name_list = []
    sheets = workbook.worksheets()
    
    if not sheets:
        logging.error("No sheets found in the workbook.")
        print("No sheets found in the workbook.")
        os._exit(1)
    
    # make list with all sheet names
    for sheet in sheets:
        sheet_name_list.append(sheet.title)
    logging.info(f"Sheet names: {sheet_name_list}")

    msg_list = []
    folder_list = []

    #for sheet in sheet_name_list:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result  = list(executor.map(parallel_process_sheet, sheet_name_list))
        # Get the result from the future
        logging.info(f"Processing sheets in parallel.")
        
    logging.info(f"Processing results: {result}")
    
    msg_list.extend(r[0] for r in result)
    folder_list.extend(r[1] for r in result)
    
    print(f"Processing results: {msg_list}")
    
    # save files path in google spreadsheet
    file_workbook = gc.open("file_list")
    i = 0
    
    if flg_filepath == "y":
        for sheet_name in sheet_name_list:
            print(f"sheet_name: {sheet_name}")

            try:
                # check if the sheet exists
                common_tool.check_sheet_exists(sheet_name, file_workbook)
                sheet = file_workbook.worksheet(sheet_name)
            except Exception as e:
                print(f"Error: {e}")
                logging.error(f"Error: {e}")
            
            common_tool.listup_all_files(folder_list[i], sheet)
            i = i + 1
    
    try:
        ssm_client = boto3.client('ssm', region_name='ap-southeast-2')
        common_tool.send_mail(ssm_client, msg_list)
    except Exception as e:
        print(f"Error sending email: {e}")
        logging.error(f"Error sending email: {e}")

    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"{current_time}: All processes are complete.")
    logging.info(f"{current_time}: All processes are complete.")

    # os.system("shutdown /s /t 1800")
    # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # logging.info(f"{current_time}: Shutdown command executed. The system will shut down in 30 minutes.")