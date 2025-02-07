from psychopy import visual, core, event, gui, data # Perhaps faster to import modules individually?

import numpy as np
import random
import math
import pandas as pd
from datetime import datetime
import os
import sys
from psychopy import gui

sys.path.append(
    "/Users/wiegerscheurer/repos/physicspred"
)  # To enable importing from repository folders

from functions.utilities import setup_folders, save_performance_data
from functions.physics import (
    check_collision,
    collide,
    velocity_to_direction,
    predict_ball_path,
    _flip_dir,
    compute_speed,
    change_speed,
    _rotate_90,
    _dir_to_velocity,
    velocity_to_direction,
)

# win_dims = [1000, 1000]
win_dims = [1920, 1080]
ball_speed = 3  # Used to be 5 when refresh rate was 30
ball_radius = 40  # Used to be 40
interactor_heigth = 180
interactor_width = 5
occluder_radius = 120
verbose = False

keys = [
    "trial", "interactor", "bounce", "bounce_moment", "random_bounce_direction", 
    "target_onset", "speed_change", "ball_change", "abs_congruent", "sim_congruent", 
    "response", "accuracy", "rt", "start_pos", "end_pos", 
    "abs_rfup", "abs_rfright", "abs_rfdown", "abs_rfleft", 
    "sim_rfup", "sim_rfright", "sim_rfdown", "sim_rfleft"
]

exp_data = {key: [] for key in keys}

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
psychopyVersion = '2024.2.4'
expName = 'IPE_SpatTemp_Pred_Behav'  # from the Builder filename that created this script
expInfo = {
    'participant': f"sub-{random.randint(0, 999999):06.0f}",
    'session': '001',
    'run': f"run-{random.randint(0, 10):02.0f}",
}

# --- Show participant info dialog --
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

# Setup the window
# win = visual.Window(win_dims, color='black', units='pix', fullscr=False)

win = visual.Window(
    size=win_dims,        # The size of the window in pixels (width, height).
    fullscr=True,             # Whether to run in full-screen mode. Overrides size arg
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

win.mouseVisible = False

# store frame rate of monitor if we can measure it
expInfo["frameRate"] = win.getActualFrameRate()
if expInfo["frameRate"] != None:
    frameDur = 1.0 / round(expInfo["frameRate"])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

#get screen Hz for adjusting animations later
# gets your refresh rate and stores it in the frame rate object
refreshRate = round(expInfo['frameRate'],0)

#init text to display on refresh info screen
refreshText = str()
refreshInformation = visual.TextStim(win=win, name='refreshInformation',
    text='',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0)

# refreshInformation.setAutoDraw(True)
# check_refreshrate_resp = keyboard.Keyboard()

# Define stimuli
fixation = visual.TextStim(win, text="+", color="white", pos=(0, 0), height=50)

# Define a square and rotate it to create a thick line
line_45 = visual.Rect(
    win,
    width=interactor_width,
    height=interactor_heigth,
    fillColor="red",
    lineColor="red",
)
line_45.ori = 45  # Rotate the square by 45 degrees

line_135 = visual.Rect(
    win,
    width=interactor_width,
    height=interactor_heigth,
    fillColor="red",
    lineColor="red",
)
line_135.ori = 135 
occluder = visual.Circle(
    win, radius=occluder_radius, fillColor="grey", lineColor="grey", pos=(0, 0)
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


# Define ball
ball = visual.Circle(win, radius=ball_radius, fillColor="white", lineColor="white")

# Define trial conditions
# trial_conditions = ["45", "135", "none"] * 10
trial_conditions = ["45", "135", "none"] * 2
# trial_conditions = ["none", "none", "none"] * 2
random.shuffle(trial_conditions)

ball_spawn_spread = 1.8  # Margin around fixation where the ball can spawn (smaller = )
# Possible starting positions and movement directions
start_positions = {
    "up": (0, square_size // ball_spawn_spread),
    "down": (0, -square_size // ball_spawn_spread),
    "left": (-square_size // ball_spawn_spread, 0),
    "right": (square_size // ball_spawn_spread, 0),
}
directions = {
    "up": (0, -ball_speed),
    "down": (0, ball_speed),
    "left": (ball_speed, 0),
    "right": (-ball_speed, 0),
}

# Define the start and end colors for the subtle change
start_color = np.array([1.0, 1.0, 1.0])  # White
# end_color = np.array([0.9, 0.9, 0.9])    # Light gray
end_color = np.array([0.75, 0.75, 0.75])  # Light gray


# Function to interpolate between two colors
def interpolate_color(start_color, end_color, factor):
    return start_color + (end_color - start_color) * factor


# **TASK SELECTION MENU**
task_choice = None
ball_change_type = None

while task_choice not in ["F", "B"]:
    instruction_text = visual.TextStim(
        win,
        text="Press 'F' for Fixation Hue Change Task\nPress 'B' for Ball Change Task",
        color="white",
        pos=(0, 0),
        height=20,
    )
    instruction_text.draw()
    win.flip()
    task_choice = event.waitKeys(keyList=["f", "b"])[
        0
    ].upper()  # Ensures only one key is read

if task_choice == "B":
    while ball_change_type not in ["H", "S"]:
        instruction_text = visual.TextStim(
            win,
            text="Press 'H' for Ball Hue Change\nPress 'S' for Ball Speed Change",
            color="white",
            pos=(0, 0),
            height=20,
        )
        instruction_text.draw()
        win.flip()
        ball_change_type = event.waitKeys(keyList=["h", "s"])[
            0
        ].upper()  # Ensures only one key is read

print(
    f"Selected task: {'Fixation Hue Change' if task_choice == 'F' else 'Ball Change'}"
)
if task_choice == "B":
    print(
        f"Ball change type: {'Hue Change' if ball_change_type == 'H' else 'Speed Change'}"
    )

for trial in trial_conditions:
    trial_clock = core.Clock()  # Create a clock for the trial
    
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    refreshInformation.setAutoDraw(True)
    fixation.draw()
    win.flip()
    core.wait(2)  # Fixation display

    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    if trial == "45":
        line_45.draw()
    elif trial == "135":
        line_135.draw()
    fixation.draw()

    win.flip()
    core.wait(2)  # Fixation + diagonal line display
    
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    occluder.draw()
    fixation.draw()
    win.flip()
    # core.wait(0.5)  # Occluder display
    core.wait(1)  # Occluder display

    # Ball movement setup
    edge = random.choice(list(start_positions.keys()))
    ball.pos = np.array(start_positions[edge])
    velocity = np.array(directions[edge])
    bounce = random.choice([True, False])  # 50% chance to bounce
    rand_bounce_direction = random.choice(
        ["left", "right"]
    )  # Random 90° bounce direction
    rand_speed_change = random.choice(
        ["slower", "faster"]
    )  # 50% chance to slow down or speed up
    # ball_change_delay = random.uniform(0, .8)  # Random delay for hue change
    ball_change_delay = 0  # random.uniform(0, 0)  # Random delay for hue change
    bounce_moment = None
    bounced_at = None
    correct_response = None
    crossed_fixation = False
    speed_changed = False
    responded = False
    left_occluder = False
    ball_change_moment = None
    occluder_exit_moment = None
    trial_duration = win_dims[1] // (800 / 10)
    print(f"Trial duration = {trial_duration}") if verbose else None
    # Apply hue change based on selected task
    ball_change = random.random() < 0.25  # 0.2  # 20% probability
    feedback_text = ""

    # Store trial characteristics
    exp_data["trial"].append(len(exp_data["trial"]) + 1)
    exp_data["interactor"].append(trial)
    exp_data["bounce"].append(
        bounce
    )  # Whether the ball will bounce (IMPORTANT TO HAVE IT HERE, as it will change after the bounce) it's like imperative
    exp_data["bounce_moment"].append(
        None
    )  # if bounce else exp_data["bounce_moment"].append(None) # What?????
    (
        exp_data["random_bounce_direction"].append(rand_bounce_direction)
        if bounce and trial == "none"
        else exp_data["random_bounce_direction"].append(None)
    )
    exp_data["target_onset"].append(
        None
    )  # Cannot be done, until the moment of the change is known
    (
        exp_data["speed_change"].append(rand_speed_change)
        if ball_change and task_choice == "B" and ball_change_type == "S"
        else exp_data["speed_change"].append(None)
    )
    exp_data["ball_change"].append(ball_change)
    exp_data["abs_congruent"].append(
        None
    )  # Placeholder for abstraction prediction congruency
    exp_data["sim_congruent"].append(
        None
    )  # Placeholder for simulated prediction congruency
    exp_data["response"].append(None)  # Placeholder for response
    exp_data["accuracy"].append(None)  # Placeholder for accuracy
    exp_data["rt"].append(None)  # Placeholder for reaction time
    exp_data["start_pos"].append(edge)
    exp_data["end_pos"].append(None)  # Placeholder for end position
    exp_data["abs_rfup"].append(None)  # Placeholder for absolute reasoning up RF
    exp_data["abs_rfright"].append(None)  # Placeholder for absolute reasoning right RF
    exp_data["abs_rfdown"].append(None)  # Placeholder for absolute reasoning down RF
    exp_data["abs_rfleft"].append(None)  # Placeholder for absolute reasoning left RF
    exp_data["sim_rfup"].append(None)  # Placeholder for simulated reasoning up RF
    exp_data["sim_rfright"].append(None)  # Placeholder for simulated reasoning right RF
    exp_data["sim_rfdown"].append(None)  # Placeholder for simulated reasoning down RF
    exp_data["sim_rfleft"].append(None)  # Placeholder for simulated reasoning left RF

    # **BALL MOVEMENT LOOP**
    while (
        trial_clock.getTime() < trial_duration
    ):  # Move until 6 seconds (scaled for window size)
        ball.pos += velocity  # Update ball position
        if trial_clock.getTime() % 0.5 < 0.02: #and verbose:
            print(f"Screen refresh rate: {refreshRate}") # At 75 Hz in UB singel
            # print(f"Ball direction: {velocity_to_direction(velocity)}")
        # Check for bounce
        if bounce and check_collision(ball.pos, trial, ball):
            if trial == "45":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 45, ball_speed)  # Reflect off 45°
                bounce_moment = trial_clock.getTime()

            elif trial == "135":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 135, ball_speed)  # Reflect off 135°
                bounce_moment = trial_clock.getTime()

            bounce = False  # Prevent double bouncing
            crossed_fixation = True

        # Draw everything each frame
        ball.draw()
        left_border.draw()
        right_border.draw()
        top_border.draw()
        bottom_border.draw()
        occluder.draw()
        fixation.draw()
        win.flip()
        # core.wait(0.02)  # Smooth animation # I guess 30 hz? I want 60 though
        core.wait(0.01)  # Smooth animation

        # Stop if the ball is near fixation and bounce is True
        if np.linalg.norm(ball.pos) <= 20:
            if bounce and trial == "none":
                print("DOING FUNKY PHANTOM BOUNCE NOW!!!!!!")
                if rand_bounce_direction == "left":

                    (
                        print(f"BOUNCED LEFT at {trial_clock.getTime()}")
                        if verbose
                        else None
                    )
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "left"), ball_speed
                    )  # Reflect off 45°
                    bounced_at = trial_clock.getTime()

                elif rand_bounce_direction == "right":

                    (
                        print(f"BOUNCED RIGHT at {trial_clock.getTime()}")
                        if verbose
                        else None
                    )
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "right"), ball_speed
                    )  # Reflect off 135
                    bounced_at = (
                        trial_clock.getTime()
                    )  # Ugly that this is a double variable, fix at some point

            bounce = False
            crossed_fixation = True

        if (
            np.linalg.norm(ball.pos) > (occluder_radius)
            and crossed_fixation
            and not left_occluder
        ):  # Make sure to start counting after exiting the occluder
            print(f"occluder exit time: {trial_clock.getTime()}")
            occluder_exit_moment = trial_clock.getTime()
            left_occluder = True

        if (
            bounce == False
        ):  # If the ball has bounced, or won't bounce at all (for continuation)
            # if bounce_moment == None and crossed_fixation: # If bounce not yet registered, and ball has crossed fixation
            if (
                crossed_fixation and ball_change_moment == None and left_occluder
            ):  # If bounce not yet registered, and ball has crossed fixation
                # print(f"ball_change_MOMENT: {trial_clock.getTime() + ball_change_delay}") # if verbose else None
                print(
                    f"ball_change_MOMENT: {occluder_exit_moment + ball_change_delay}"
                )  # if verbose else None
                # ball_change_moment = trial_clock.getTime() + ball_change_delay
                ball_change_moment = occluder_exit_moment + ball_change_delay
                exp_data["target_onset"][-1] = (
                    ball_change_moment if ball_change else None
                )
                # bounce_moment = trial_clock.getTime()
            if bounce_moment != None and ball_change_moment != None:

                # if trial_clock.getTime() > ball_change_moment: # Necessary? for wahat?
                elapsed_time = trial_clock.getTime() - ball_change_moment

                duration = 0.5  # Duration of the color change in seconds
                factor = min(
                    elapsed_time / duration, 1.0
                )  # Ensure factor is between 0 and 1

                if task_choice == "F" and ball_change:
                    fixation.color = interpolate_color(start_color, end_color, factor)

                elif task_choice == "B" and ball_change:
                    if ball_change_type == "H":
                        ball.fillColor = interpolate_color(
                            start_color, end_color, factor
                        )
                        ball.lineColor = interpolate_color(
                            start_color, end_color, factor
                        )

                    # Make ball velocity slowly decrease
                    elif ball_change_type == "S" and not speed_changed:

                        print(f"Current speed: {compute_speed(velocity)}")
                        ball_direction = velocity_to_direction(velocity)

                        if rand_speed_change == "slower":
                            velocity = change_speed(
                                compute_speed(velocity), -0.75, ball_direction
                            )
                        elif rand_speed_change == "faster":
                            velocity = change_speed(
                                compute_speed(velocity), +0.75, ball_direction
                            )
                        print(f"New speed: {compute_speed(velocity)}")
                        speed_changed = True

        ball_direction = velocity_to_direction(velocity)
        bounce_moment = bounced_at if bounce_moment == None else bounce_moment
        exp_data["bounce_moment"][-1] = (
            bounce_moment if _flip_dir(ball_direction) != edge else None
        )  # Check whether the ball hasn't just continued
        exp_data["end_pos"][-1] = ball_direction  # log end position

        # toetsen = event.getKeys(['space', 'left', 'right', 'up', 'down'])
        toetsen = event.getKeys(
            ["space", "left", "right", "up", "down", "escape", "r"]
        )  # Construction set

        # **CHECK FOR 'R' TO SKIP TRIAL OR 'ESCAPE' TO QUIT**
        # keys = event.getKeys(["r", "escape"])
        if "escape" in toetsen:
            print("ESCAPE PRESSED")
            win.close()
            core.quit()
        elif "r" in toetsen:
            print("R PRESSED")
            continue  # Skip to the next trial

        if toetsen != [] and not responded:  # If toets pressed and not done so before
            print(f"Response: {toetsen[0]}")
            # if bounce_moment == None: # If too early
            if ball_change_moment == None:  # If too early
                print(f"Wrong, too early")
                feedback_text = "Wrong, too early"
                correct_response = False
                responded = True  # QUIT LOOP
            else:  # If on time
                toets_moment = trial_clock.getTime()  # Get the moment of response
                print(f"This is response: {toetsen[0]}")

                exp_data["response"][-1] = toetsen[0]  # Log the response
                exp_data["rt"][-1] = (
                    toets_moment - ball_change_moment
                )  # Log the reaction time

                if ball_change:  # If there was a target change
                    if task_choice == "F" and "space" in toetsen:
                        if toets_moment < ball_change_moment:
                            feedback_text = f"Wrong, TOO EARLY"
                            print(f"Wrong, TOO EARLY")
                            correct_response = False
                        else:
                            feedback_text = f"Correct! detected a change after {round(toets_moment - ball_change_moment, 3)}s"
                            print(
                                f"Correct! detected a change after {round(toets_moment - ball_change_moment, 3)}s"
                            )
                            correct_response = True

                    if task_choice == "B" and toetsen[0] in [
                        "left",
                        "right",
                        "up",
                        "down",
                    ]:
                        hue_or_speed = "hue" if ball_change_type == "H" else "speed"
                        exp_data["response"][-1] = toetsen[0]
                        exp_data["rt"][-1] = toets_moment - ball_change_moment
                        if toets_moment < ball_change_moment:
                            feedback_text = f"Wrong, TOO EARLY"
                            print(f"Wrong, TOO EARLY")
                            correct_response = False
                        elif ball_direction == toetsen[0]:
                            feedback_text = f"Correct! detected {rand_speed_change} {toetsen[0]}ward ball in {round(toets_moment - ball_change_moment, 3)}s"
                            print(
                                f"Correct! detected {rand_speed_change} {toetsen[0]}ward ball in {round(toets_moment - ball_change_moment, 3)}s"
                            )
                            correct_response = True
                        else:
                            feedback_text = f"Wrong direction, should be a {rand_speed_change} {ball_direction}ward ball"
                            print(
                                f"Wrong direction, should be a {rand_speed_change} {ball_direction}ward ball"
                            )
                            correct_response = False
                else:  # If there was nothing to detect
                    print(f"Wrong, there was no change")
                    feedback_text = "Wrong, there was no change"
                    correct_response = False
                responded = True
        if not responded and ball_change:

            feedback_text = "Undetected ball change"
            correct_response = False

        exp_data["accuracy"][
            -1
        ] = correct_response  # Werkt (misschien nu niet meer, stond eerst hoger)

    feedback = visual.TextStim(
        win, text=feedback_text, color="white", pos=(0, 50), height=25
    )
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    feedback.draw()
    fixation.draw()
    win.flip()
    core.wait(2)

    # Reset ball and fixation color to original after each trial
    ball.fillColor = "white"
    ball.lineColor = "white"
    fixation.color = "white"

    # Figure out how to fill in the RF specific values
    if trial == "none":
        exp_data["abs_congruent"][-1] = 1 if exp_data["bounce"] != None else 0
        exp_data["sim_congruent"][-1] = 1 if exp_data["bounce"] != None else 0

    # Get the predictions and sensory input for ball path per physical reasoning appraoch (hypothesis)
    for hypothesis in ["abs", "sim"]:
        pred_to_input = predict_ball_path(
            hypothesis=hypothesis,
            interactor=trial,
            start_pos=edge,
            end_pos=exp_data["end_pos"][-1],
            plot=False,
        )
        exp_data[f"{hypothesis}_congruent"][-1] = False  # Initialize as False
        for location in pred_to_input.keys():
            exp_data[f"{hypothesis}_rf{location}"][-1] = pred_to_input[location]
            if sum(pred_to_input[location]) == 2:
                exp_data[f"{hypothesis}_congruent"][
                    -1
                ] = True  # Meaning that prediction and input agree (SEEMS TO WORK!!)

win.close()

df = pd.DataFrame(exp_data)

# Save the DataFrame to a CSV file
subject_id = "subject_stront"
task_name = "task_01"
save_performance_data(subject_id, task_name, df)
