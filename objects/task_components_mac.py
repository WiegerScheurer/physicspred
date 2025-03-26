import os
import sys
import yaml
import random
import numpy as np
from psychopy import visual, gui, core, data, filters


sys.path.append(
    "/Users/wiegerscheurer/repos/physicspred"
)  # To enable importing from repository folders

from functions.physics import get_bounce_dist

# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(__file__), os.pardir, "config_lumin.yaml")
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

occluder_type = config["occluder_type"]  # "square" or "cross"
# Access parameters from the config dictionary
win_dims = config['win_dims']
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
    size=win_dims,        # The size of the window in pixels (width, height).
    fullscr=config["full_screen"],  # Whether to run in full-screen mode. Overrides size arg
    screen=config["experiment_screen"],  # The screen number to display the window on (0 is usually the primary screen).
    winType="pyglet",  # The backend to use for the window (e.g., 'pyglet', 'pygame').
    allowStencil=False,  # Whether to allow stencil buffer (used for advanced graphics).
    # monitor='testMonitor',    # The name of the monitor configuration to use (defined in the Monitor Center).
    color=[-.25, -.25, -.25],  # [0, 0, 0],          # The background color of the window (in RGB space).
    colorSpace="rgb",  # The color space for the background color (e.g., 'rgb', 'dkl', 'lms').
    backgroundImage="",  # Path to an image file to use as the background.
    backgroundFit="none",  # How to fit the background image ('none', 'fit', 'stretch').
    blendMode="avg",  # The blend mode for drawing (e.g., 'avg', 'add').
    useFBO=True,  # Whether to use Frame Buffer Objects (for advanced graphics).
    units="pix",  # The default units for window operations (e.g., 'pix', 'norm', 'cm', 'deg', 'height').
)

win_dims = win.size

fixation = visual.TextStim(win, text="+", color=config["fixation_color"], pos=(0, 0), height=50)

####################################### MAKING A BETTER BALL #############################
ball = visual.Circle(win, 
                     radius=ball_radius, 
                     fillColor=config["ball_fillcolor"], 
                     lineColor=config["ball_linecolor"], 
                     interpolate=True,
                     opacity=1)

# Create a 2D isotropic Gaussian
gaussian = visual.GratingStim(
    win=win,
    tex='sin',
    mask='gauss',
    size=(ball_radius*1.5, ball_radius),  # Size in pixels
    sf=0,  # Spatial frequency (0 for no grating)
    contrast=1,
    color='white',
    opacity=.8
)

# Create a 2D isotropic Gaussian
ball_tone = visual.GratingStim(
    win=win,
    tex='sin',
    mask='gauss',
    size=(ball_radius*2.1, ball_radius*2.1),  # Size in pixels
    # size=(ball_radius, ball_radius),  # Size in pixels
    sf=0,  # Spatial frequency (0 for no grating)
    contrast=1,
    color='white',
    opacity=.9,
)

# Create a 2D isotropic Gaussian
ball_glimmer = visual.GratingStim(
    win=win,
    tex='sin',
    mask='gauss',
    size=(ball_radius/1.5, ball_radius*1.5),  # Size in pixels
    sf=0,  # Spatial frequency (0 for no grating)
    contrast=1,
    color='white',
)

ball_shade = visual.ImageStim(
    win,
    image="/Users/wiegerscheurer/Stimulus_material/ball_shaded_opaqtop.png",  
    size=(ball_radius*2.05, ball_radius*2.05),
    opacity=.4
)


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

# bounce_dist = get_bounce_dist(ball_radius + (interactor_width / 2))
bounce_dist = get_bounce_dist(ball_radius + (interactor_width / 2 * 1.8)) # 1.8 factor is due to the that now we use an image

# These are the old, plain rectangle interactors 

# Define line_45_top and line_45_bottom
# line_45_bottom = create_interactor(win, interactor_width, interactor_height, "red", "red", 45, ((bounce_dist), -bounce_dist))
# line_45_top = create_interactor(win, interactor_width, interactor_height, "red", "red", 45, (-(bounce_dist), bounce_dist))

# Define line_135_top and line_135_bottom
# line_135_bottom = create_interactor(win, interactor_width, interactor_height, "red", "red", 135, (-bounce_dist, -(bounce_dist)))
# line_135_top = create_interactor(win, interactor_width, interactor_height, "red", "red", 135, (bounce_dist, (bounce_dist)))

line_45_bottom = visual.ImageStim(
    win,
    # image="/Users/wiegerscheurer/Stimulus_material/interactor_45_flat_beige.png", 
    image="/Users/wiegerscheurer/repos/physicspred/objects/interactor_45_flat_beige.png",
    size=(interactor_height, interactor_height),
    pos=(bounce_dist, -(bounce_dist)),
    opacity=1
)

line_45_top = visual.ImageStim(
    win,
    # image="/Users/wiegerscheurer/Stimulus_material/interactor_45_flat_beige.png", 
    image="/Users/wiegerscheurer/repos/physicspred/objects/interactor_45_flat_beige.png",
    size=(interactor_height, interactor_height),
    pos= (-(bounce_dist), bounce_dist),
    opacity=1
)

line_135_bottom = visual.ImageStim(
    win,
    # image="/Users/wiegerscheurer/Stimulus_material/interactor_135_flat_beige.png", 
    image="/Users/wiegerscheurer/repos/physicspred/objects/interactor_135_flat_beige.png",
    size=(interactor_height, interactor_height),
    pos=(-bounce_dist, -(bounce_dist)),
    opacity=1
)

line_135_top = visual.ImageStim(
    win,
    # image="/Users/wiegerscheurer/Stimulus_material/interactor_135_flat_beige.png", 
    image="/Users/wiegerscheurer/repos/physicspred/objects/interactor_135_flat_beige.png",
    size=(interactor_height, interactor_height),
    pos= ((bounce_dist), bounce_dist),
    opacity=1
)


################### OCCLUDER ######################

cross_factor = occluder_radius / 65
# Define the vertices for a cross shape
cross_vertices = [
    (-occluder_radius, -occluder_radius / cross_factor), (-occluder_radius, occluder_radius / cross_factor),
    (-occluder_radius / cross_factor, occluder_radius / cross_factor), (-occluder_radius / cross_factor, occluder_radius),
    (occluder_radius / cross_factor, occluder_radius), (occluder_radius / cross_factor, occluder_radius / cross_factor),
    (occluder_radius, occluder_radius / cross_factor), (occluder_radius, -occluder_radius / cross_factor),
    (occluder_radius / cross_factor, -occluder_radius / cross_factor), (occluder_radius / cross_factor, -occluder_radius),
    (-occluder_radius / cross_factor, -occluder_radius), (-occluder_radius / cross_factor, -occluder_radius / cross_factor)
]

outer_cross_factor = (occluder_radius / 65 ) - .2
# Define the vertices for a cross shape
outer_cross_vertices = [
    (-occluder_radius, -occluder_radius / outer_cross_factor), (-occluder_radius, occluder_radius / outer_cross_factor),
    (-occluder_radius / outer_cross_factor, occluder_radius / outer_cross_factor), (-occluder_radius / outer_cross_factor, occluder_radius),
    (occluder_radius / outer_cross_factor, occluder_radius), (occluder_radius / outer_cross_factor, occluder_radius / outer_cross_factor),
    (occluder_radius, occluder_radius / outer_cross_factor), (occluder_radius, -occluder_radius / outer_cross_factor),
    (occluder_radius / outer_cross_factor, -occluder_radius / outer_cross_factor), (occluder_radius / outer_cross_factor, -occluder_radius),
    (-occluder_radius / outer_cross_factor, -occluder_radius), (-occluder_radius / outer_cross_factor, -occluder_radius / outer_cross_factor)
]

# Create the cross shape
occluder = visual.ShapeStim(
    win,
    vertices=cross_vertices,
    fillColor=np.array(config["occluder_color"], dtype=float),
    lineColor=np.array(config["occluder_color"], dtype=float),
    pos=(0, 0),
    opacity=occluder_opacity if occluder_type[:5] == "cross" else 0,
)

# Add opacity = .5 to make see-through
occluder_square = visual.Rect(
    win,
    width=occluder_radius * 1.1 if occluder_type == "cross_smooth" else occluder_radius * 1.5,
    height=occluder_radius * 1.1 if occluder_type == "cross_smooth" else occluder_radius * 1.5,
    fillColor=np.array(config["occluder_color"], dtype=float),
    lineColor=np.array(config["occluder_color"], dtype=float),
    pos=(0, 0),
    opacity=occluder_opacity if occluder_type != "cross" else 0,
    ori=45 if occluder_type == "cross_smooth" else 0
)



# Create the inner outline shape
inner_outline = visual.ShapeStim(
    win,
    vertices=outer_cross_vertices,
    fillColor=[-0.5, -0.5, -0.5],  # Set fill color to dark grey using RGB values
    lineColor=[-0.5, -0.5, -0.5],  # Set line color to dark grey using RGB values
    pos=(0, 0),
    opacity=occluder_opacity,
)

# Draw the cross shape
# occluder.draw()

# occluder = visual.Circle(
#     win, radius=occluder_radius, fillColor="grey", lineColor="grey", pos=(0, 0)
# )



# # Add opacity = .5 to make see-through
# occluder_square = visual.Rect(
#     win,
#     width=occluder_radius * 1.5,
#     height=occluder_radius * 1.5,
#     fillColor="grey",
#     lineColor="grey",
#     pos=(0, 0),
#     opacity=occluder_opacity,
#     ori=0
# )

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

# Create the grey borders
left_border = visual.Rect(
    win=win,
    width=(win_dims[0] - square_size) / 2,
    height=win_dims[1],
    fillColor="black",
    lineColor="black",
    pos=[-(win_dims[0] - square_size) / 4 - square_size / 2, 0],
)

right_border = visual.Rect(
    win=win,
    width=(win_dims[0] - square_size) / 2,
    height=win_dims[1],
    fillColor="black",
    lineColor="black",
    pos=[(win_dims[0] - square_size) / 4 + square_size / 2, 0],
)

top_border = visual.Rect(
    win=win,
    width=win_dims[0],
    height=(win_dims[1] - square_size) / 2,
    fillColor="black",
    lineColor="black",
    pos=[0, (win_dims[1] - square_size) / 4 + square_size / 2],
)

bottom_border = visual.Rect(
    win=win,
    width=win_dims[0],
    height=(win_dims[1] - square_size) / 2,
    fillColor="black",
    lineColor="black",
    pos=[0, -(win_dims[1] - square_size) / 4 - square_size / 2],
)

##### DRAW GRID TO ALIGN INTERACTOR WITH
# Define the grid lines
line_length = 800  # Length of the lines to cover the window
line_width = 1  # Width of the lines
num_lines = 10  # Number of lines on each side of the center

# Create horizontal lines
horizontal_lines = []
for i in range(-num_lines, num_lines + 1):
    y = i * (line_length / (2 * num_lines))
    horizontal_lines.append(visual.Line(win, start=(-line_length / 2, y), end=(line_length / 2, y), lineWidth=line_width))

# Create vertical lines
vertical_lines = []
for i in range(-num_lines, num_lines + 1):
    x = i * (line_length / (2 * num_lines))
    vertical_lines.append(visual.Line(win, start=(x, -line_length / 2), end=(x, line_length / 2), lineWidth=line_width))