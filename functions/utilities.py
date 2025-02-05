from datetime import datetime
import os


def setup_folders(subject_id, task_name):
    base_dir = "/Users/wiegerscheurer/repos/physicspred/data"
    
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    subject_dir = os.path.join(base_dir, subject_id)
    task_dir = os.path.join(subject_dir, task_name)
    
    # Create directories if they don't exist
    os.makedirs(task_dir, exist_ok=True)
    
    return task_dir

def save_performance_data(subject_id, task_name, data):
    task_dir = setup_folders(subject_id, task_name)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{date_str}.csv"
    filepath = os.path.join(task_dir, filename)
    
    # Save the DataFrame to a CSV file
    data.to_csv(filepath, index=False)