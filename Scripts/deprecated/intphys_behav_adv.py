from psychopy import visual, core, event, gui, data # Perhaps faster to import modules individually?

import numpy as np
import random
import yaml
import math
import pandas as pd
from datetime import datetime
import os
import sys
from psychopy import gui

sys.path.append(
    "/Users/wiegerscheurer/repos/physicspred"
)  # To enable importing from repository folders

from functions.utilities import (
    setup_folders, 
    save_performance_data, 
    interpolate_color, 
    determine_sequence, 
    count_list_types, 
    get_pos_and_dirs
    )
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
from functions.analysis import (
    get_data, 
    get_precision, 
    get_sensitivity, 
    get_f1_score)

# Load configuration from YAML file (os.par)
config_path = os.path.join(os.path.dirname(__file__), os.pardir, 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Access parameters from the config dictionary
# win_dims = config['win_dims']
avg_ball_speed = config['avg_ball_speed']
ball_radius = config['ball_radius']
interactor_height = config['interactor_height']
interactor_width = config['interactor_width']
occluder_radius = config['occluder_radius']
verbose = config['verbose']
exp_parameters = config['exp_parameters']
timing_factor = config["timing_factor"]
feedback_freq = config["feedback_freq"]

exp_data = {par: [] for par in exp_parameters}

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
psychopyVersion = config["psychopy_version"]
expName = 'IPE_SpatTemp_Pred_Behav'  # from the Builder filename that created this script
expInfo = {
    'participant': f"sub-{random.randint(0, 999999):06.0f}",
    'session': '001',
    # 'run': f"run-{random.randint(0, 10):02.0f}",
    "task": ["Ball Speed Change", "Ball Hiccup", "Fixation Hue Change"],
    "feedback": ["No", "Yes"]
}


give_feedback = True if expInfo["feedback"] == "Yes" else False
# --- Show participant info dialog --
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName
expInfo['psychopyVersion'] = psychopyVersion

from objects.task_components import win, ball, left_border, right_border, top_border, bottom_border, line_45, line_135, occluder, fixation

win_dims = win.size

print(f"Screen dimensions: {win_dims}")

win.mouseVisible = False

# store frame rate of monitor if we can measure it
expInfo["frameRate"] = win.getActualFrameRate()
if expInfo["frameRate"] != None:
    frameDur = 1.0 / round(expInfo["frameRate"])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# get screen Hz for adjusting animations later
# gets your refresh rate and stores it in the frame rate object
refreshRate = round(expInfo['frameRate'], 0) if expInfo["frameRate"] != None else None

# init text to display on refresh info screen
refreshText = str()
refreshInformation = visual.TextStim(win=win, name='refreshInformation',
    text='',
    font='Open Sans',
    pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
    color='white', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=-1.0)

square_size = config["square_size"]

n_trials = config["n_trials"] # Number of trials

# Define the options for trial parameters
trial_options = ["45", "135", "none"]
edge_options = ["up", "down", "left", "right"]
bounce_options = [True, False]
rand_bounce_direction_options = ["left", "right"]
ball_change_options = [True] * 1 + [False] * 1
rand_speed_change_options = ["slower", "faster"]
natural_speed_variance = config["natural_speed_variance"]
ball_speed_options = list(np.arange(avg_ball_speed - natural_speed_variance, avg_ball_speed + (2 * natural_speed_variance), natural_speed_variance))

# Create deterministically randomised; balanced parameter sequences
trials = determine_sequence(n_trials, trial_options, randomised=True)
edges = determine_sequence(n_trials, edge_options, randomised=True)
bounces = determine_sequence(n_trials, bounce_options, randomised=True)
rand_bounce_directions = determine_sequence(n_trials, rand_bounce_direction_options, randomised=True)
ball_changes = determine_sequence(n_trials, ball_change_options, randomised=True)
rand_speed_changes = determine_sequence(n_trials, rand_speed_change_options, randomised=True)
ball_speeds = determine_sequence(n_trials, ball_speed_options, randomised=True)

ball_spawn_spread = config["ball_spawn_spread"]  # Margin around fixation where the ball can spawn (smaller = )

# # Possible starting positions and movement directions
# start_positions = {
#     "up": (0, square_size // ball_spawn_spread),
#     "down": (0, -square_size // ball_spawn_spread),
#     "left": (-square_size // ball_spawn_spread, 0),
#     "right": (square_size // ball_spawn_spread, 0),
# }
# directions = {
#     "up": (0, -ball_speed),
#     "down": (0, ball_speed),
#     "left": (ball_speed, 0),
#     "right": (-ball_speed, 0),
# }

# # Do this more elegantly, in a way or another. 
# fast_ball_speed = ball_speed * config["ball_speed_change"]
# fast_directions = {
#     "up": (0, -fast_ball_speed),
#     "down": (0, fast_ball_speed),
#     "left": (fast_ball_speed, 0),
#     "right": (-fast_ball_speed, 0),
# }

# slow_ball_speed = ball_speed / config["ball_speed_change"]
# slow_directions = {
#     "up": (0, -slow_ball_speed),
#     "down": (0, slow_ball_speed),
#     "left": (slow_ball_speed, 0),
#     "right": (-slow_ball_speed, 0),
# }

# Define the start and end colors for the subtle hue change
start_color = np.array([1.0, 1.0, 1.0])  # White
# end_color = np.array([0.9, 0.9, 0.9])    # Light gray
end_color = np.array([0.75, 0.75, 0.75])  # Light gray

# **TASK SELECTION MENU**
task_choice = None
ball_change_type = None
instruction_read = ""
ready_to_start = ""

welcome_text = visual.TextStim(
    win,
    text=f"Welcome! Today you will perform the {expInfo['task']} task.\n\nPress 'Space' to continue.",
    color="white",
    pos=(0, 0),
    height=30,
)

while instruction_read != "SPACE":
    welcome_text.draw()
    win.flip()
    instruction_read = event.waitKeys(keyList=["space"])[0].upper()  # Ensures only one key is read

explanation_text_speed = visual.TextStim(
    win,
    text=(
        "In this task, you will see a ball moving towards the\n"
        "center of the screen, where it passes behind a circle.\n\n"
        "On top of this circle you'll see a small white cross: +  \n"
        "Keep your eyes focused on this cross during the whole trial.\n\n"
        "In some trials, the ball will change its speed.\n\n"
        "You are challenged to detect these changes.\n\n"
        "When you see a change, press the arrow key to indicate in what\n"
        "direction the ball was moving when it changed speed.\n\n"
        "Be as fast and accurate as possible!\n\n\n"
        
    
        "Press 'Space' to start."
    ),
    color="white",
    pos=(0, 0),
    height=30,  # Adjust the height to a more reasonable value
    wrapWidth=1000  # Set wrap width to ensure text wraps within the window
)

# while ready_to_start not in ["space"]:
while ready_to_start != "SPACE":

    explanation_text_speed.draw()
    win.flip()
    ready_to_start = event.waitKeys(keyList=["space"])[0].upper()  # Ensures only one key is read
    

ball_change_type = "S"
task_choice = expInfo["task"][0]

for trial_number, trial in enumerate(trials):
    print(f"Trial number: {trial_number + 1}")
    trial_clock = core.Clock()  # Create a clock for the trial
    
    
    start_positions, directions, fast_directions, slow_directions = get_pos_and_dirs(
        avg_ball_speed, square_size, ball_spawn_spread, config["ball_speed_change"]
    )
    
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    refreshInformation.setAutoDraw(True)
    fixation.draw()
    win.flip()
    core.wait(2 * timing_factor)  # Fixation display

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
    core.wait(2 * timing_factor)  # Fixation + diagonal line display
    
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    if trial == "45":
        line_45.draw()
    elif trial == "135":
        line_135.draw()
    occluder.draw()
    fixation.draw()
    win.flip()
    core.wait(1 * timing_factor)  # Occluder display

    # Ball movement setup
    edge = edges[trial_number] # Ball start position
    ball.pos = np.array(start_positions[edge])
    velocity = np.array(directions[edge])
    
    bounce = bounces[trial_number]  # 50% chance to bounce
    rand_bounce_direction = rand_bounce_directions[trial_number] # Random 90° phantom bounce direction
    rand_speed_change = rand_speed_changes[trial_number]  # 50% chance to slow down or speed up
    ball_change = ball_changes[trial_number]  # 20% probability of target ball change
    this_ball_speed = ball_speeds[trial_number]  # Random ball speed
    
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
    # trial_duration = win_dims[1] // (800 / 10) #  13 seconds now, scales with screensize, ideally (NO should be same, the rest should scale)
    trial_duration = square_size // (800 / 10)  * timing_factor
    print(f"Trial duration = {trial_duration}s") if verbose else None

##################### NEW CODE, integrate with stuff abocve, where I intiisalise the exp_data
    # Store trial characteristics
    exp_data["trial"].append(len(exp_data["trial"]) + 1)
    exp_data["interactor"].append(trial)
    exp_data["bounce"].append(bounce)  # Whether the ball will bounce
    exp_data["ball_speed"].append(this_ball_speed)

    # Append None placeholders
    placeholders = [
        "bounce_moment", "target_onset", "abs_congruent", "sim_congruent",
        "response", "accuracy", "rt", "end_pos", "abs_rfup", "abs_rfright",
        "abs_rfdown", "abs_rfleft", "sim_rfup", "sim_rfright", "sim_rfdown", "sim_rfleft"
    ]
    for key in placeholders:
        exp_data[key].append(None)

    # Conditional appends
    exp_data["random_bounce_direction"].append(rand_bounce_direction if bounce and trial == "none" else None)
    exp_data["speed_change"].append(rand_speed_change if ball_change and task_choice == "B" and ball_change_type == "S" else None)

    # Append remaining values
    exp_data["ball_change"].append(ball_change)
    exp_data["start_pos"].append(edge)
    
#####################################

    # **BALL MOVEMENT LOOP**
    while (
        trial_clock.getTime() < trial_duration
    ): 
        ball.pos += velocity  # Update ball position
        if trial_clock.getTime() % 0.5 < 0.02 and verbose:
            print(f"Screen refresh rate: {refreshRate}") # At 75 Hz in UB singel
            # print(f"Ball direction: {velocity_to_direction(velocity)}")
        # Check for bounce
        if bounce and check_collision(ball.pos, trial, ball):
            if trial == "45":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 45, this_ball_speed)  # Reflect off 45°
                bounce_moment = trial_clock.getTime()

            elif trial == "135":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 135, this_ball_speed)  # Reflect off 135°
                bounce_moment = trial_clock.getTime()

            bounce = False  # Prevent double bouncing
            crossed_fixation = True

        # Draw everything each frame
        ball.draw()
        left_border.draw()
        right_border.draw()
        top_border.draw()
        bottom_border.draw()
        if trial == "45":
            line_45.draw()
        elif trial == "135":
            line_135.draw()
        occluder.draw()
        fixation.draw()
        win.flip()
        core.wait(0.01)  # Smooth animation, frame time, presumably

        # Stop if the ball is near fixation and bounce is True
        if np.linalg.norm(ball.pos) <= (config["ball_radius"] // 2):
            if bounce and trial == "none":
                print("Phantom bounce") if verbose else None
                if rand_bounce_direction == "left":

                    (
                        print(f"BOUNCED LEFT at {trial_clock.getTime()}")
                        if verbose
                        else None
                    )
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "left"), this_ball_speed
                    )  # Reflect off 45°
                    # bounced_at = trial_clock.getTime()
                    # bounce_moment = trial_clock.getTime()

                elif rand_bounce_direction == "right":

                    (
                        print(f"BOUNCED RIGHT at {trial_clock.getTime()}")
                        if verbose
                        else None
                    )
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "right"), this_ball_speed
                    )  # Reflect off 135
                    # bounced_at = (
                    #     trial_clock.getTime()
                    # )  # Ugly that this is a double variable, fix at some point
                    # bounce_moment = trial_clock.getTime()
            
            bounce_moment = trial_clock.getTime() #if bounce_moment == None else bounce_moment # MAYBE WILL DO THE TRICK
            bounce = False
            crossed_fixation = True
            print(f"crossed fixation at {trial_clock.getTime()}") if verbose else None

        if (
            np.linalg.norm(ball.pos) > (occluder_radius - (ball_radius * 1.5))
            and crossed_fixation
            and not left_occluder
        ):  # Make sure to start counting after exiting the occluder
            print(f"occluder exit time: {trial_clock.getTime():.2f}")
            occluder_exit_moment = trial_clock.getTime()
            left_occluder = True

        elif (
            bounce == False
        ):  # If the ball has bounced, or won't bounce at all (for continuation)
            if (
                crossed_fixation and ball_change_moment == None and left_occluder
            ):  # If bounce not yet registered, and ball has crossed fixation
                print(
                    f"ball_change_MOMENT: {occluder_exit_moment + ball_change_delay}"
                ) if verbose else None
                ball_change_moment = occluder_exit_moment + ball_change_delay
                exp_data["target_onset"][-1] = (
                    ball_change_moment if ball_change else None
                )
            if bounce_moment != None and ball_change_moment != None:
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

                        print(f"Current speed: {compute_speed(velocity):.2f}")
                        ball_direction = velocity_to_direction(velocity)

                        if rand_speed_change == "slower":
                            # change_factor = 1 / config["ball_speed_change"]
                            # velocity = change_speed(
                            #     compute_speed(velocity), change_factor, ball_direction
                            # )
                            # velocity = directions_speedchanged[ball_direction]
                            velocity = np.array(slow_directions[_flip_dir(ball_direction)])
                            # print("SLOWWWWWWWWINGGGGG")
                        elif rand_speed_change == "faster":
                            # print("FASTERRRRRRRRRRRRRRRR")
                            # velocity = change_speed(
                            #     compute_speed(velocity), config["ball_speed_change"], ball_direction
                            # )
                            # velocity = directions_speedchanged[ball_direction]
                            velocity = np.array(fast_directions[_flip_dir(ball_direction)])
                        print(f"New speed: {compute_speed(velocity):.2f}")
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
                exp_data["response"][-1] = toetsen[0]  # Log the response
                correct_response = None # To prevent logging an accuracy value
                responded = True  # QUIT LOOP
            else:  # If on time
                toets_moment = trial_clock.getTime()  # Get the moment of response
                exp_data["response"][-1] = toetsen[0]  # Log the response
                exp_data["rt"][-1] = (
                    toets_moment - ball_change_moment
                )  # Log the reaction time

                if ball_change:  # If there was a target change
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
                            feedback_text = f"Responded too early" #if give_feedback else ""
                            print(f"Wrong, TOO EARLY")
                            correct_response = False
                        elif ball_direction == toetsen[0]:
                            feedback_text = f"Correct! detected {rand_speed_change} {toetsen[0]}ward ball in {round(toets_moment - ball_change_moment, 3)}s" if give_feedback else ""
                            print(
                                f"Correct! detected {rand_speed_change} {toetsen[0]}ward ball in {round(toets_moment - ball_change_moment, 3)}s"
                            )
                            correct_response = True
                        else:
                            feedback_text = f"Wrong direction, should be a {rand_speed_change} {ball_direction}ward ball" if give_feedback else ""
                            print(
                                f"Wrong direction, should be a {rand_speed_change} {ball_direction}ward ball"
                            )
                            correct_response = False
                else:  # If there was nothing to detect
                    print(f"Wrong, there was no change")
                    feedback_text = "Wrong, there was no change"
                    correct_response = False
                responded = True
        elif trial_clock.getTime() > trial_duration and not responded:
            # if not responded:
            if ball_change:
                # SOMETHING IS VERY WRONG HERRE WTF
                feedback_text = f"Undetected ball change, it was a {rand_speed_change} {ball_direction}ward ball" if give_feedback else ""
                correct_response = False
                print(feedback_text)
            else:
                feedback_text = ""
                correct_response = None
                print(feedback_text)
                # if not responded and ball_change:
                #     # SOMETHING IS VERY WRONG HERRE WTF
                #     feedback_text = f"Undetected ball change, it was a {rand_speed_change} {ball_direction} ward ball"
                #     correct_response = False

        exp_data["accuracy"][
            -1
        ] = correct_response  # Werkt (misschien nu niet meer, stond eerst hoger)
    
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

    if (trial_number + 1) % feedback_freq == 0 and trial_number > 10:
        intermit_data = pd.DataFrame(exp_data)
        this_precision = get_precision(intermit_data, hypothesis="both", include_dubtrials=False, return_df=False)
        this_sensitivity = get_sensitivity(intermit_data, hypothesis="both", include_dubtrials=False, return_df=False)
        this_f1 = get_f1_score(intermit_data, hypothesis="both", include_dubtrials=False, return_df=False)
        # feedback_text = f"Precision: {this_precision}\nSensitivity: {this_sensitivity}\nF1 Score: {this_f1}"
        feedback_text = f'Current accuracy: {np.mean((this_precision["simulation"], this_precision["abstraction"]))}% changes detected!'
        # feedback_text = "Theoretical feedback, implement still"
    else:
        feedback_text = ""

    feedback = visual.TextStim(
        win, text=feedback_text, color="white", pos=(0, 50), height=30
    )
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    feedback.draw()
    fixation.draw()
    win.flip()
    core.wait(2 * timing_factor)

    # Reset ball and fixation color to original after each trial
    ball.fillColor = "white"
    ball.lineColor = "white"
    fixation.color = "white"

    # Figure out how to fill in the RF specific values IS NIE TNODIOG DENK IK??
    # if trial == "none":
    #     for hypothesis in ["abs", "sim"]:
    #         exp_data[f"{hypothesis}_congruent"][-1] = 1 if exp_data["bounce"] != None else 0
        # exp_data["abs_congruent"][-1] = 1 if exp_data["bounce"] != None else 0
        # exp_data["sim_congruent"][-1] = 1 if exp_data["bounce"] != None else 0

    # # Get the predictions and sensory input for ball path per physical reasoning appraoch (hypothesis)
    # for hypothesis in ["abs", "sim"]:
    #     pred_to_input = predict_ball_path(
    #         hypothesis=hypothesis,
    #         interactor=trial,
    #         start_pos=edge,
    #         end_pos=exp_data["end_pos"][-1],
    #         plot=False,
    #     )
    #     exp_data[f"{hypothesis}_congruent"][-1] = False  # Initialize as False
    #     for location in pred_to_input.keys():
    #         exp_data[f"{hypothesis}_rf{location}"][-1] = pred_to_input[location]
    #         if sum(pred_to_input[location]) == 2:
    #             exp_data[f"{hypothesis}_congruent"][
    #                 -1
    #             ] = True  # Meaning that prediction and input agree (SEEMS TO WORK!!)

    
    
win.close()

df = pd.DataFrame(exp_data)

# Save the DataFrame to a CSV file
subject_id = expInfo["participant"]
task_name = expInfo["task"].lower().replace(" ", "_")
save_performance_data(expInfo["participant"], task_name, df)
