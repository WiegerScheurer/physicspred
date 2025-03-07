from datetime import datetime
import random
import os
from scipy.stats import truncexpon
import matplotlib.pyplot as plt
import numpy as np

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


def get_pos_and_dirs(ball_speed, square_size, ball_spawn_spread, ball_speed_change, ball_radius):
    # Possible starting positions
    # start_positions = {
    #     "up": (0, square_size // ball_spawn_spread),
    #     "down": (0, -square_size // ball_spawn_spread),
    #     "left": (-square_size // ball_spawn_spread, 0),
    #     "right": (square_size // ball_spawn_spread, 0),
    # }
    out_of_bounds = (square_size // 2) + (ball_radius)
    
    start_positions = {
        "up": (0, out_of_bounds),
        "down": (0, -out_of_bounds),
        "left": (-out_of_bounds, 0),
        "right": (out_of_bounds, 0),
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


def truncated_exponential_decay(min_iti, truncation_cutoff, size=1000):
    """
    Generate a truncated exponential decay distribution.

    Parameters:
        min_iti (float): The minimum ITI (lower bound of the distribution).
        truncation_cutoff (float): The upper bound of the distribution.
        size (int): Number of samples to generate.

    Returns:
        samples (numpy.ndarray): Random samples from the truncated exponential distribution.
    """
    # Define the scale parameter for the exponential decay
    scale = 1.0  # Adjust this to control the steepness of decay
    b = (truncation_cutoff - min_iti) / scale  # Shape parameter for truncation

    # Generate random samples
    samples = truncexpon(b=b, loc=min_iti, scale=scale).rvs(size=size)
    return samples

def two_sided_truncated_exponential(center, min_jitter, max_jitter, scale=1.0, size=1000):
    """
    Generate a two-sided truncated exponential decay distribution that peaks at the center.

    Parameters:
        center (float): The central point of the distribution (e.g., critical event time).
        min_jitter (float): The minimum jitter value (left bound).
        max_jitter (float): The maximum jitter value (right bound).
        scale (float): The scale parameter controlling steepness of the decay.
        size (int): Number of samples to generate.

    Returns:
        samples (numpy.ndarray): Random samples from the two-sided truncated exponential distribution.
    """
    # Create an array of possible jitter values
    x = np.linspace(min_jitter, max_jitter, 1000)
    
    # Define left and right exponential decays
    left_decay = np.exp(-(center - x[x <= center]) / scale)
    right_decay = np.exp(-(x[x > center] - center) / scale)
    
    # Combine left and right sides
    pdf = np.concatenate([left_decay, right_decay])
    
    # Normalize PDF so it integrates to 1
    pdf /= np.sum(pdf)
    
    # Sample from this custom PDF using inverse transform sampling
    cdf = np.cumsum(pdf)  # Compute cumulative density function
    cdf /= cdf[-1]  # Ensure CDF ends at 1
    random_values = np.random.rand(size)  # Uniform random values between 0 and 1
    samples = np.interp(random_values, cdf, x)  # Map random values to jitter times
    
    return samples

def plot_distribution(samples, min_iti, truncation_cutoff):
    """
    Plot the histogram of the truncated exponential distribution.

    Parameters:
        samples (numpy.ndarray): Random samples from the truncated exponential distribution.
        min_iti (float): The minimum ITI.
        truncation_cutoff (float): The upper bound of the distribution.
    """
    plt.figure(figsize=(8, 5))
    plt.hist(samples, bins=30, density=True, alpha=0.6, color='blue', label="Sampled Data")

    # Plot theoretical PDF for comparison
    scale = 1.0
    b = (truncation_cutoff - min_iti) / scale
    x = np.linspace(min_iti, truncation_cutoff, 100)
    pdf = truncexpon(b=b, loc=min_iti, scale=scale).pdf(x)
    plt.plot(x, pdf, 'r-', lw=2, label="Theoretical PDF")

    plt.title("Truncated Exponential Decay Distribution")
    plt.xlabel("Interval")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_two_sided_distribution(samples, center_time, min_jitter, max_jitter, scale=1.0):
    # Plot histogram of sampled data
    plt.hist(samples, bins=30, density=True, alpha=0.6, color='blue', label="Sampled Data")

    # Plot theoretical PDF for visualization
    x = np.linspace(min_jitter, max_jitter, 1000)
    left_decay = np.exp(-(center_time - x[x <= center_time]) / scale)
    right_decay = np.exp(-(x[x > center_time] - center_time) / scale)
    pdf = np.concatenate([left_decay, right_decay])
    pdf /= np.sum(pdf) * (x[1] - x[0])  # Normalize for plotting purposes
    plt.plot(x, pdf, 'r-', lw=2, label="Theoretical PDF")

    plt.title("Two-Sided Truncated Exponential Decay")
    plt.xlabel("Time relative to center (s)")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True)
    plt.show()

def balance_over_bool(boolean_list:list, value_options:list, randomised:bool=True) -> list:
    """Map one list of value options onto the True values of a boolean list.

    Args:
        boolean_list (list): List that indicates which trials should get a value.
        value_options (list): List of the value options
    """    
    
    val_seq = determine_sequence(np.sum(boolean_list), value_options, randomised=randomised)
    
    result = []
    value_index = 0
    for item in boolean_list:
        if item:
            result.append(val_seq[value_index])
            value_index += 1
        else:
            result.append(False)
    return result