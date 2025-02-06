import numpy as np
import math
import matplotlib.pyplot as plt

def check_collision(ball_pos, line_angle, ball):
    """Returns True if the ball's edge intersects the diagonal line."""
    x, y = ball_pos
    if line_angle == "45":  
        return abs(y - x) <= ball.radius  # Ball touches y = x
    elif line_angle == "135":
        return abs(y + x) <= ball.radius  # Ball touches y = -x
    return False  # No line

def collide(start_direction: str, line_angle: int, ball_speed: float):
    """Returns the new direction vector of the ball after a collision."""
    direction_angles = {
        "up": 270,
        "down": 90,
        "left": 0,
        "right": 180
    }
    
    # Get the initial angle of the ball's movement
    initial_angle = direction_angles[start_direction]

    # Calculate the angle of incidence
    if line_angle in [45, 135]:
        normal_angle = line_angle
    else:
        return start_direction
    
    # Calculate the angle of reflection
    angle_of_reflection = (2 * normal_angle - initial_angle) % 360
    
    # Convert the angle of reflection back to a direction vector
    new_direction = (
        math.cos(math.radians(angle_of_reflection)) * ball_speed,
        math.sin(math.radians(angle_of_reflection)) * ball_speed
    )
    
    return new_direction

def velocity_to_direction(velocity):
    """Converts a velocity vector to a direction string."""
    x, y = velocity
    if abs(x) > abs(y):
        return "left" if x < 0 else "right"
    else:
        return "down" if y < 0 else "up"  # Vertical axis is inverted
    
    
def _dir_to_vec(direction:str) -> tuple:
    """Turn direction string into vector representation
    Args:
        direction (str): The direction string
    Returns:
        tuple: The vector representation in row,column (y,x)
    """    
    directions = {"up": (1, 0),
              "right": (0, 1), 
              "down": (-1, 0),
              "left": (0, -1)}
    
    return directions[direction]

def _vec_to_dir(vector:tuple) -> str:
    """Turn vector representation into direction string
    Args:
        vector (tuple): The vector representation in row,column (y,x)
    Returns:
        str: The direction string
    """    
    vectors = {(1, 0): "up",
              (0, 1): "right", 
              (-1, 0): "down",
              (0, -1): "left"}
    
    return vectors[vector]

## Not really needed though, locations are on a 3x3 grid
def _dir_to_loc(direction:str) -> tuple:
    """Turn direction string into location representation
    Args:
        direction (str): The direction string
    Returns:
        tuple: The location representation in row,column (y,x)
    """    
    locations = {"up": (0, 1),
              "right": (1, 2), 
              "down": (2, 1),
              "left": (1, 0)}
    
    return locations[direction]

def _rotate_90(start_direction, left_or_right):
    """
    Rotate a 2D vector by 90 degrees in the specified direction.
    
    Args:
        start_direction (tuple): The initial direction vector as a tuple of two elements.
        left_or_right (str): The direction to rotate, either "left" or "right".
    
    Returns:
        tuple: The rotated direction vector as a tuple of two elements (y, x) or (row, column).
    """
    if type(start_direction) != tuple:
        start_direction = _dir_to_vec(start_direction)
    
    # Define the rotation matrix for 90 degrees
    rotation_matrix_90 = np.array([[0, -1], [1, 0]])
    rotation_matrix_270 = np.array([[0, 1], [-1, 0]])

    towards = {"left": rotation_matrix_270,
               "right": rotation_matrix_90}

    # Convert the direction tuple to a numpy array
    direction_vector = np.array(start_direction)
    
    # Perform the matrix multiplication to rotate the vector
    rotated_vector = np.dot(towards[left_or_right], direction_vector)
    # Convert the result back to a tuple and return
    return tuple(rotated_vector)

def _flip_dir(direction: str | tuple) -> str | tuple:
    """Where does the ball end up, given a direction? Assuming a continuous path, so no collision anymore.
        This basically just flips the direction value to the opposite on the relevant axis.

    Args:
        direction (str | tuple): Where does the ball go?

    Returns:
        str | tuple: The opposite point of the field.
    """    
    if isinstance(direction, str):
        flipped_dir = _vec_to_dir(tuple(dir_axis * -1 for dir_axis in _dir_to_vec(direction)))
    elif isinstance(direction, tuple):
        flipped_dir = tuple(dir_axis * -1 for dir_axis in direction)
    else:
        raise ValueError("Direction must be either a string or a tuple")
    
    return flipped_dir

def _bounce_ball(start_direction: str, interactor: str):
    """
    Bounces a ball based on the start direction and the type of interactor.

    Parameters:
    start_direction (str): The initial direction of the ball.
    interactor (str): The type of interactor.

    Returns:
    str: The new direction of the ball after bouncing.

    """

    if interactor == "45":
        relative_direction = "left" if start_direction in ["right", "left"] else "right"
        end_loc = _rotate_90(start_direction=start_direction, left_or_right=relative_direction)
    elif interactor == "135":
        relative_direction = "left" if start_direction in ["up", "down"] else "right"
        end_loc = _rotate_90(start_direction=start_direction, left_or_right=relative_direction)
    else:
        end_loc = _dir_to_vec(start_direction) # When no interactor, ball ends up in the same direction
        
    end_direction = _flip_dir(end_loc)
    
    return _vec_to_dir(end_direction)

def plot_positions(start_pos, end_pos, pred_to_input, interactor):
    positions = {"up": (0, 1), "right": (1, 0), "down": (0, -1), "left": (-1, 0)}
    
    fig, ax = plt.subplots()
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Plot start position
    start_coords = positions[start_pos]
    ax.plot(start_coords[0], start_coords[1], 'go', markersize=10, label='Start Position', alpha=.5)
    
    # Plot end position
    end_coords = positions[end_pos]
    ax.plot(end_coords[0], end_coords[1], 'ro', markersize=10, label='End Position', alpha=.5)
    
    # Plot predicted positions
    for pos, value in pred_to_input.items():
        if value[0] == 1:
            pred_coords = positions[pos]
            ax.plot(pred_coords[0], pred_coords[1], 'bo', markersize=10, label='Predicted Position', alpha=.5)
    
    # Add diagonal stripe based on interactor value
    if interactor == "45":
        ax.plot([-.2, .2], [-.2, .2], 'k-', label='45° interactor')
    elif interactor == "135":
        ax.plot([-.2, .2], [.2, -.2], 'k-', label='135° interactor')
    
    ax.legend()
    ax.axis("off")
    plt.show()

def predict_ball_path(hypothesis: str, interactor: str, start_pos: str, end_pos: str, plot: bool = False):
    """
    Predict the path of a ball based on the given parameters.
    
    Args:
        hypothesis (str): The predictor hypothesis, either "abs" or "rel".
        interactor (str): The interactor hypothesis, either "none" or "abs".
        start_pos (str): The starting position of the ball.
        end_pos (str): The ending position of the ball.
        plot (bool): Whether to plot the positions or not.
    
    Returns:
        dict: A dictionary representing the path of the ball.
    """
    pred_to_input = {"up": [0],
                     "right": [0],
                     "down": [0],
                     "left": [0]}
    
    # NOTE: Predictions are about the ball direction AFTER collision, so it's 0 for start positions
    if hypothesis == "abs":
        pred_to_input[_flip_dir(start_pos)] = [1] # Opposite of start position
        
    elif hypothesis == "sim":
        # NOTE: flip_dir is used to get the ball direction based on the start location
        predicted_dir = _bounce_ball(start_direction=_flip_dir(start_pos), interactor=interactor)
        predicted_endloc = _flip_dir(predicted_dir) # Flip direction to get endpoint
        pred_to_input[predicted_endloc] = [1]
        
    for receptive_field in pred_to_input.keys():
        pred_to_input[receptive_field].append(0) # Add column for sensory input
    pred_to_input[end_pos][1] = 1 # Change to 1 for end position

    # Turn the dictionary list values into tuples    
    pred_to_input_tuples = {key: tuple(value) for key, value in pred_to_input.items()}

    if plot:
        plot_positions(start_pos, end_pos, pred_to_input, interactor)
    
    return pred_to_input_tuples