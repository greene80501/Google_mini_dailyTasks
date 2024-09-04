import json
from datetime import datetime
from todoist_api_python.api import TodoistAPI

api = TodoistAPI("no")

# Helper function to convert non-serializable objects
def serialize_task(task):
    task_dict = task.__dict__.copy()
    if hasattr(task, 'due') and task.due is not None:
        task_dict['due'] = task.due.__dict__  # Convert Due object to dict
    return task_dict

# Helper function to check if task is due today
def is_task_due_today(task):
    if task.due and task.due.date:
        due_date_str = task.due.date.split('T')[0]  # Get the date part
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return due_date == datetime.now().date()
    return False

try:
    tasks = api.get_tasks()
    
    # Filter tasks due today
    today_tasks = [task for task in tasks if is_task_due_today(task)]
    
    if today_tasks:
        # Create a human-readable message for tasks due today
        tasks_message = "You have to do the following tasks today:\n"
        tasks_message += "\n".join([f"- {task.content}" for task in today_tasks])
        
        # Append to a text file named "today_events.txt"
        with open("today_events.txt", "a") as file:
            file.write(tasks_message + "\n")  # Add a newline for separation
        
        print("Today's tasks appended to today_events.txt")
    else:
        print("No tasks due today.")
except Exception as error:
    print(error)
