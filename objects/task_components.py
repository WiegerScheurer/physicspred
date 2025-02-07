import os
import sys
import yaml
import random
from psychopy import visual, gui, core, data
sys.path.append(
    "/Users/wiegerscheurer/repos/physicspred"
)  # To enable importing from repository folders

# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Access parameters from the config dictionary
win_dims = config['win_dims']
ball_speed = config['ball_speed']
ball_radius = config['ball_radius']
interactor_height = config['interactor_height']
interactor_width = config['interactor_width']
occluder_radius = config['occluder_radius']
verbose = config['verbose']
exp_parameters = config['exp_parameters']

exp_data = {par: [] for par in exp_parameters}

win = visual.Window(
    size=win_dims,        # The size of the window in pixels (width, height).
    fullscr=False,             # Whether to run in full-screen mode. Overrides size arg
    screen=0,                 # The screen number to display the window on (0 is usually the primary screen).
    winType='pyglet',         # The backend to use for the window (e.g., 'pyglet', 'pygame').
    allowStencil=False,       # Whether to allow stencil buffer (used for advanced graphics).
    # monitor='testMonitor',    # The name of the monitor configuration to use (defined in the Monitor Center).
    color="black", #[0, 0, 0],          # The background color of the window (in RGB space).
    colorSpace='rgb',         # The color space for the background color (e.g., 'rgb', 'dkl', 'lms').
    backgroundImage='',       # Path to an image file to use as the background.
    backgroundFit='none',     # How to fit the background image ('none', 'fit', 'stretch').
    blendMode='avg',          # The blend mode for drawing (e.g., 'avg', 'add').
    useFBO=True,              # Whether to use Frame Buffer Objects (for advanced graphics).
    units='pix'            # The default units for window operations (e.g., 'pix', 'norm', 'cm', 'deg', 'height').
)


fixation = visual.TextStim(win, text="+", color="white", pos=(0, 0), height=50)

ball = visual.Circle(win, radius=ball_radius, fillColor="white", lineColor="white")

# Calculate the offset
offset_y = interactor_width / 2

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
line_135.ori = 135 # Rotate the line by 135 degrees
line_135.pos = (0, -offset_y)  # Adjust position


# occluder = visual.Circle(
#     win, radius=occluder_radius, fillColor="grey", lineColor="grey", pos=(0, 0)
# )

# Add opacity = .5 to make see-through
occluder = visual.Rect(
    win, width=2*occluder_radius, height=2*occluder_radius, fillColor="grey", lineColor="grey", pos=(0, 0)
)

### Create borders to maintain square task screen
# Calculate the size of the square field
square_size = min(win_dims)

# Create the grey borders
left_border = visual.Rect(
    win=win,
    width=(win_dims[0] - square_size) / 2,
    height=win_dims[1],
    fillColor='grey',
    lineColor='grey',
    pos=[-(win_dims[0] - square_size) / 4 - square_size / 2, 0]
)

right_border = visual.Rect(
    win=win,
    width=(win_dims[0] - square_size) / 2,
    height=win_dims[1],
    fillColor='grey',
    lineColor='grey',
    pos=[(win_dims[0] - square_size) / 4 + square_size / 2, 0]
)

top_border = visual.Rect(
    win=win,
    width=win_dims[0],
    height=(win_dims[1] - square_size) / 2,
    fillColor='grey',
    lineColor='grey',
    pos=[0, (win_dims[1] - square_size) / 4 + square_size / 2]
)

bottom_border = visual.Rect(
    win=win,
    width=win_dims[0],
    height=(win_dims[1] - square_size) / 2,
    fillColor='grey',
    lineColor='grey',
    pos=[0, -(win_dims[1] - square_size) / 4 - square_size / 2]
)