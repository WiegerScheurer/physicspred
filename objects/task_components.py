import os
import sys
import yaml
import random
from psychopy import visual, gui, core, data

sys.path.append(
    "/Users/wiegerscheurer/repos/physicspred"
)  # To enable importing from repository folders

from functions.physics import get_bounce_dist

# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(__file__), os.pardir, "config.yaml")
with open(config_path, "r") as file:
    config = yaml.safe_load(file)


# Access parameters from the config dictionary
# win_dims = config['win_dims']
# ball_speed = config['ball_speed']
ball_radius = config["ball_radius"]
interactor_height = config["interactor_height"]
interactor_width = config["interactor_width"]
occluder_radius = config["occluder_radius"]
verbose = config["verbose"]
exp_parameters = config["exp_parameters"]
square_size = config["square_size"]
occluder_opacity = config["occluder_opacity"]

exp_data = {par: [] for par in exp_parameters}

win = visual.Window(
    # size=win_dims,        # The size of the window in pixels (width, height).
    fullscr=config["full_screen"],  # Whether to run in full-screen mode. Overrides size arg
    screen=config["experiment_screen"],  # The screen number to display the window on (0 is usually the primary screen).
    winType="pyglet",  # The backend to use for the window (e.g., 'pyglet', 'pygame').
    allowStencil=False,  # Whether to allow stencil buffer (used for advanced graphics).
    # monitor='testMonitor',    # The name of the monitor configuration to use (defined in the Monitor Center).
    color="black",  # [0, 0, 0],          # The background color of the window (in RGB space).
    colorSpace="rgb",  # The color space for the background color (e.g., 'rgb', 'dkl', 'lms').
    backgroundImage="",  # Path to an image file to use as the background.
    backgroundFit="none",  # How to fit the background image ('none', 'fit', 'stretch').
    blendMode="avg",  # The blend mode for drawing (e.g., 'avg', 'add').
    useFBO=True,  # Whether to use Frame Buffer Objects (for advanced graphics).
    units="pix",  # The default units for window operations (e.g., 'pix', 'norm', 'cm', 'deg', 'height').
)

win_dims = win.size

fixation = visual.TextStim(win, text="+", color="white", pos=(0, 0), height=50)

ball = visual.Circle(win, radius=ball_radius, fillColor="white", lineColor="white")

# Calculate the offset
offset_y = interactor_width / 2

####################################### Defining the interactor lining #####################################
############################################### Original ###################################################
# Define line_45
line_45 = visual.Rect(
    win,
    width=interactor_width,
    height=interactor_height,
    fillColor="red",
    lineColor="red",
)
line_45.ori = 45  # Rotate the line by 45 degrees
line_45.pos = (offset_y, 0)  # Adjust position

# Define line_135
line_135 = visual.Rect(
    win,
    width=interactor_width,
    height=interactor_height,
    fillColor="red",
    lineColor="red",
)
line_135.ori = 135  # Rotate the line by 135 degrees
line_135.pos = (0, -offset_y)  # Adjust position

############################################### New one ###################################################

# # Define line_45
# line_45_top = visual.Rect(
#     win,
#     width=interactor_width,
#     height=interactor_height,
#     fillColor="red",
#     lineColor="red",
# )
# line_45_top.ori = 45  # Rotate the line by 45 degrees

# # Create line_45_bottom with the same properties
# line_45_bottom = visual.Rect(
#     win,
#     width=interactor_width,
#     height=interactor_height,
#     fillColor="red",
#     lineColor="red",
# )
# line_45_bottom.ori = 45  # Rotate the line by 45 degrees

# bounce_dist = get_bounce_dist(ball_radius)

# line_45_top.pos = ((bounce_dist + offset_y), -bounce_dist)  # Adjust position
# line_45_bottom.pos = (-(bounce_dist + offset_y), bounce_dist)  # Adjust position

# # Define line_135
# line_135_top = visual.Rect(
#     win,
#     width=interactor_width,
#     height=interactor_height,
#     fillColor="red",
#     lineColor="red",
# )
# line_135_top.ori = 135  # Rotate the line by 135 degrees

# # Create line_135_bottom with the same properties
# line_135_bottom = visual.Rect(
#     win,
#     width=interactor_width,
#     height=interactor_height,
#     fillColor="red",
#     lineColor="red",
# )
# line_135_bottom.ori = 135  # Rotate the line by 135 degrees

# line_135_top.pos = (-bounce_dist, -offset_y)  # Adjust position
# line_135_bottom.pos = (bounce_dist, offset_y)  # Adjust position

def create_interactor(win, width, height, fill_color, line_color, ori, pos):
    rect = visual.Rect(
        win,
        width=width,
        height=height,
        fillColor=fill_color,
        lineColor=line_color,
    )
    rect.ori = ori
    rect.pos = pos
    return rect

bounce_dist = get_bounce_dist(ball_radius)

# Define line_45_top and line_45_bottom
line_45_bottom = create_interactor(win, interactor_width, interactor_height, "red", "red", 45, ((bounce_dist + offset_y), -bounce_dist))
line_45_top = create_interactor(win, interactor_width, interactor_height, "red", "red", 45, (-(bounce_dist + offset_y), bounce_dist))

# Define line_135_top and line_135_bottom
line_135_bottom = create_interactor(win, interactor_width, interactor_height, "red", "red", 135, (-bounce_dist, -(bounce_dist + offset_y)))
line_135_top = create_interactor(win, interactor_width, interactor_height, "red", "red", 135, (bounce_dist, (bounce_dist + offset_y)))




# occluder = visual.Circle(
#     win, radius=occluder_radius, fillColor="grey", lineColor="grey", pos=(0, 0)
# )

# Add opacity = .5 to make see-through
occluder = visual.Rect(
    win,
    width=2 * occluder_radius,
    height=2 * occluder_radius,
    fillColor="grey",
    lineColor="grey",
    pos=(0, 0),
    opacity=occluder_opacity,
)

occluder_glass = visual.Rect(
    win,
    width=2 * occluder_radius,
    height=2 * occluder_radius,
    fillColor="grey",
    lineColor="grey",
    pos=(0, 0),
    opacity=.5,
)


### Create borders to maintain square task screen
# Calculate the size of the square field
# square_size = min(win_dims)
# square_size = 1000

# Create the grey borders
left_border = visual.Rect(
    win=win,
    width=(win_dims[0] - square_size) / 2,
    height=win_dims[1],
    fillColor="grey",
    lineColor="grey",
    pos=[-(win_dims[0] - square_size) / 4 - square_size / 2, 0],
)

right_border = visual.Rect(
    win=win,
    width=(win_dims[0] - square_size) / 2,
    height=win_dims[1],
    fillColor="grey",
    lineColor="grey",
    pos=[(win_dims[0] - square_size) / 4 + square_size / 2, 0],
)

top_border = visual.Rect(
    win=win,
    width=win_dims[0],
    height=(win_dims[1] - square_size) / 2,
    fillColor="grey",
    lineColor="grey",
    pos=[0, (win_dims[1] - square_size) / 4 + square_size / 2],
)

bottom_border = visual.Rect(
    win=win,
    width=win_dims[0],
    height=(win_dims[1] - square_size) / 2,
    fillColor="grey",
    lineColor="grey",
    pos=[0, -(win_dims[1] - square_size) / 4 - square_size / 2],
)
