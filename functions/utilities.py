from datetime import datetime
import random
import os


def count_list_types(list):
    """
    Counts the occurrences of each element in a list and returns a dictionary with the counts.

    Args:
        list (list): The input list.

    Returns:
        dict: A dictionary where the keys are the elements in the list and the values are the counts of each element.
    """
    return {i: list.count(i) for i in list}


def setup_folders(subject_id, task_name):
    """
    Creates the necessary folders for a given subject and task.

    Args:
        subject_id (str): The ID of the subject.
        task_name (str): The name of the task.

    Returns:
        str: The path to the task directory.
    """
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
    """
    Save performance data to a CSV file.

    Args:
        subject_id (str): The ID of the subject.
        task_name (str): The name of the task.
        data (pandas.DataFrame): The performance data to be saved.

    Returns:
        None
    """
    task_dir = setup_folders(subject_id, task_name)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{date_str}.csv"
    filepath = os.path.join(task_dir, filename)

    # Save the DataFrame to a CSV file
    data.to_csv(filepath, index=False)


def interpolate_color(start_color, end_color, factor):
    """
    Interpolates between two colors based on a given factor.

    Args:
        start_color (tuple): The starting color as a tuple of RGB values.
        end_color (tuple): The ending color as a tuple of RGB values.
        factor (float): The interpolation factor between 0 and 1.

    Returns:
        tuple: The interpolated color as a tuple of RGB values.
    """
    return start_color + (end_color - start_color) * factor


def determine_sequence(n_trials: int, options: list, randomised: bool = True) -> list:
    """
    Balances a sequence of trials based on the number of trials and options.

    Parameters:
    n_trials (int): The number of trials to balance.
    options (list): The options to balance.
    randomised (bool): Whether to randomise the sequence.

    Returns:
    list: The balanced sequence of trials.

    """

    n_options = len(options)
    n_per_option = n_trials // n_options
    remainder = n_trials % n_options

    balanced_sequence = options * n_per_option + options[:remainder]

    if randomised:
        random.shuffle(balanced_sequence)

    return balanced_sequence


def get_pos_and_dirs(ball_speed, square_size, ball_spawn_spread, ball_speed_change):
    # Possible starting positions
    start_positions = {
        "up": (0, square_size // ball_spawn_spread),
        "down": (0, -square_size // ball_spawn_spread),
        "left": (-square_size // ball_spawn_spread, 0),
        "right": (square_size // ball_spawn_spread, 0),
    }

    # Base directions
    directions = {
        "up": (0, -ball_speed),
        "down": (0, ball_speed),
        "left": (ball_speed, 0),
        "right": (-ball_speed, 0),
    }

    # Fast directions
    fast_ball_speed = ball_speed * ball_speed_change
    fast_directions = {
        "up": (0, -fast_ball_speed),
        "down": (0, fast_ball_speed),
        "left": (fast_ball_speed, 0),
        "right": (-fast_ball_speed, 0),
    }

    # Slow directions
    slow_ball_speed = ball_speed / ball_speed_change
    slow_directions = {
        "up": (0, -slow_ball_speed),
        "down": (0, slow_ball_speed),
        "left": (slow_ball_speed, 0),
        "right": (-slow_ball_speed, 0),
    }
    
    # Skip directions
    skip_ball_speed = ball_speed * (ball_speed_change * 10)
    skip_directions = {
        "up": (0, -skip_ball_speed),
        "down": (0, skip_ball_speed),
        "left": (skip_ball_speed, 0),
        "right": (-skip_ball_speed, 0),
    }
    
    # Wait directions
    wait_ball_speed = ball_speed * (ball_speed_change / 10)
    wait_directions = {
        "up": (0, -wait_ball_speed),
        "down": (0, wait_ball_speed),
        "left": (wait_ball_speed, 0),
        "right": (-wait_ball_speed, 0),
    }
    

    return start_positions, directions, fast_directions, slow_directions, skip_directions, wait_directions
