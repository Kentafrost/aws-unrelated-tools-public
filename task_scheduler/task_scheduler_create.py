import os
import win32com.client
import tkinter as tk
from tkinter import filedialog
import time
import logging
logging.basicConfig(level=logging.INFO)


# current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
current_time = time.strftime("%Y%m%d_%H%M%S")
current_day_zero = time.strftime("%Y-%m-%dT00:00:00", time.localtime())

# connect to the task scheduler
scheduler = win32com.client.Dispatch('Schedule.Service')
scheduler.Connect()

root_folder = scheduler.GetFolder('\\')
tasks = root_folder.GetTasks(0)
tasks_names = [task.Name for task in tasks]

# create shutdown task scheduler on weekdays and weekends
task_create_names = ["PCShutdownTaskWeekdays", "PCShutdownTaskWeekends"]
action_path = r"C:\\Windows\\System32\\shutdown.exe -s -t 3600"

def disable_task_scheduler(tasks_name):

    task = root_folder.GetTask(tasks_name)
    task.Enabled = False
    root_folder.RegisterTaskDefinition(tasks_name, task.Definition, 6, None, None, 3, None)
    logging.info(f"Disabled Task: '{tasks_name}'")


def enable_task_scheduler(tasks_name):
    
    task = root_folder.GetTask(tasks_name)
    task.Enabled = True
    root_folder.RegisterTaskDefinition(tasks_name, task.Definition, 6, None, None, 3, None)
    logging.info(f"Enabled Task: '{tasks_name}'")


current_day = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


# python automation script to create a task scheduler
def create_task_scheduler_selected_script(file_path, file_name):
    
    task_create_name = f"PythonScriptScheduler_{file_name}"

    # Create task scheduler if not exist
    if task_create_name not in tasks_names:
        task_def = scheduler.NewTask(0)
        task_def.RegistrationInfo.Description = f"Task scheduler to run a python file [{file_name}]"
        
        script_path = file_path

        task_def.Actions.Create(0).Path = script_path
        task_def.Settings.Enabled = True
        task_def.Settings.StopIfGoingOnBatteries = False

        # Task def
        trigger = task_def.Triggers.Create(2)  # 2: daily trigger
        trigger.StartBoundary = current_day
        trigger.DaysInterval = 1  # 毎日

        root_folder.RegisterTaskDefinition(
            task_create_name,
            task_def,
            6,  # create or update
            "", "",  # run as current user
            3  # logon type: interactive
        )

        print("Task Schedules creation completed")
        os.system("taskschd.msc")
    else:
        print(f"This task schedule already exists. Script name: {task_create_name}")


# Create shutdown task scheduler on weekdays and weekends if not exist
def shutdown_task_scheduler():
    scheduler = win32com.client.Dispatch('Schedule.Service')

    weekdays_task = "PCShutdownTaskWeekdays"
    weekends_task = "PCShutdownTaskWeekends"

    # Create task scheduler(weekdays) if not exist
    if not weekdays_task in tasks_names:
        print(f"Task '{weekdays_task}' doesn't exist.")
        print("Creating task scheduler for weekdays...")

        weekdays_task_def = scheduler.NewTask(0)
        weekdays_task_def.RegistrationInfo.Description = "PC Shutdown Task."

        weekdays_task_def.Actions.Create(0).Path = action_path
        weekdays_task_def.Settings.Enabled = True
        weekdays_task_def.Settings.StopIfGoingOnBatteries = False
        
        weekdays_trigger = weekdays_task_def.Triggers.Create(2)  # 2: daily trigger
        weekdays_trigger.StartBoundary = current_day_zero # Set start time to today at 00:00:00

        print(f"Task '{weekdays_task}' doesn't exist.")
        weekdays_trigger.DaysOfWeek = 62  # 62: Monday to Friday (binary 111110)
        
        root_folder.RegisterTaskDefinition(
            weekdays_task,
            weekdays_task_def,
            6,  # create or update
            "", "",  # run as current user
            3  # logon type: interactive
        )
        
    # Create task scheduler(weekends) if not exist
    if not weekends_task in tasks_names:
        print(f"Task '{weekends_task}' doesn't exist.")
        print("Creating task scheduler for weekends...")

        weekends_task_def = scheduler.NewTask(0)
        weekends_task_def.RegistrationInfo.Description = "PC Shutdown Task."

        weekends_task_def.Actions.Create(0).Path = action_path
        weekends_task_def.Settings.Enabled = True
        weekends_task_def.Settings.StopIfGoingOnBatteries = False
        
        weekends_trigger = weekends_task_def.Triggers.Create(2)  # 2: daily trigger
        weekends_trigger.StartBoundary = current_day_zero # Set start time to today at 00:00:00
        
        weekends_trigger.DaysOfWeek = 65  # 65: Saturday and Sunday (binary 1000001)

        root_folder.RegisterTaskDefinition(
            weekends_task,
            weekends_task_def,
            6,  # create or update
            "", "",  # run as current user
            3  # logon type: interactive
        )

if __name__ == "__main__":
    
    print("1: Enable or disable existing task scheduler")
    print("2: Create a task scheduler for a selected Python script")
    print("3: Set task scheduler to shutdown PC at a specified time")
    
    choice = input("Please select 3 choices")
    
    if choice == '1':
        
        task_dict = {}
        disable_chk = True  # disable or enable
        
        # input number to every task_name
        for i, task_name in enumerate(tasks_names, start=1):
            task_dict[i] = task_name
        task_number = int(input("Enter the number of the task scheduler to enable/disable:"))
        target_task_name = task_dict.get(task_number)
        
        if not target_task_name:
            logging.error(f"Task '{target_task_name}' not found.")
            os._exit(1)
            
        check_enable = input("Enter 'd' or 'disable' to disable or 'e' or 'enable' to enable the task scheduler:")
        
        if check_enable in ['d', 'disable']:
            disable_task_scheduler(target_task_name)
        else:
            enable_task_scheduler(target_task_name)
        
        logging.info("Task scheduler switch operation completed.")
        logging.shutdown()
    
    
    if choice == '2':
    
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.askopenfilename(
            title="Select a Python script to create a task scheduler",
            filetypes=[("Python Files", "*.py")]
        )
        
        if not file_path:
            print("No file selected. Exiting.")
            os._exit(0)
        elif not file_path.endswith('.py'):
            print("Selected file is not a Python script. Exiting.")
            os._exit(0)
            
        file_name = os.path.basename(file_path)
        print(f"Selected file: {file_name}")
            
        create_task_scheduler_selected_script(file_path, file_name)
        
    if choice == '3':
        shutdown_task_scheduler()