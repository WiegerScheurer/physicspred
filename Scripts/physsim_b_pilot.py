# TODO: Make change more subtle, and verify based on nearby testing. Make sure pilots
# perform task when sitting closeby the screen, the distance is crucial. Ideally the 
# change is uniform in colour. But in that case you should only be able to detect it
# when you covertly attend to it (directed by intuitive physics). Hence, luminance
# cannot be too different because this will become more salient and attract your attention.


from psychopy import (
    visual,
    core,
    event,
    gui,
    data,
)  # Perhaps faster to import modules individually?

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
    get_pos_and_dirs,
    truncated_exponential_decay,
    two_sided_truncated_exponential,
    get_phantbounce_sequence,
    balance_over_bool,
    create_balanced_trial_design,
    check_balance,
    build_design_matrix,
    
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
    will_cross_fixation,
    calculate_decay_factor,
)
from functions.analysis import get_data, get_precision, get_sensitivity, get_f1_score, get_hit_rate

#############################
from psychopy import core, event, visual

def show_break(win, duration=10):
    clock = core.Clock()
    countdown_text = visual.TextStim(win, text='', pos=(0, 0), height=20)
    break_text = visual.TextStim(win, text='You deserve a break now. Press space if you disagree.', pos=(0, 50), height=30)
    
    while clock.getTime() < duration:
        remaining_time = duration - int(clock.getTime())
        countdown_text.text = f'Break ends in {remaining_time} seconds'
        countdown_text.draw()
        break_text.draw()
        win.flip()
        
        keys = event.getKeys(keyList=['space'])
        if 'space' in keys:
            break

    # Clear any remaining key presses
    event.clearEvents()
    
# def show_endscreen(win, duration=10):
#     clock = core.Clock()
#     while clock.getTime() < duration:
#         end_text = visual.TextStim(win, text='You have completed the task. Thank you for your participation.', pos=(0, 0), height=30)
#         end_text.draw()
#         win.flip()
#         core.wait(5)
        
#         keys = event.getKeys(keyList=['space'])
#         if 'space' in keys:
#             break


# Load configuration from YAML file (os.par)
config_path = os.path.join(os.path.dirname(__file__), os.pardir, "config.yaml")
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Access parameters from the config dictionary
win_dims = config['win_dims']
avg_ball_speed = config["avg_ball_speed"]
ball_radius = config["ball_radius"]
interactor_height = config["interactor_height"]
interactor_width = config["interactor_width"]
occluder_radius = config["occluder_radius"]
verbose = config["verbose"]
exp_parameters = config["exp_parameters"]
feedback_freq = config["feedback_freq"]

exp_data = {par: [] for par in exp_parameters}

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
psychopyVersion = config["psychopy_version"]
expName = (
    "IPE_SpatTemp_Pred_Behav"  # from the Builder filename that created this script
)
expInfo = {
    "participant": f"sub-{random.randint(0, 999999):06.0f}",
    "session": "001",
    # 'run': f"run-{random.randint(0, 10):02.0f}",
    "task": ["Ball Hue", "Ball Hiccup", "Ball Speed Change", "Fixation Hue Change"],
    "feedback": ["No", "Yes"],
}

give_feedback = True if expInfo["feedback"] == "Yes" else False
# --- Show participant info dialog --
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo["date"] = data.getDateStr()  # add a simple timestamp
expInfo["expName"] = expName
expInfo["psychopyVersion"] = psychopyVersion

from objects.task_components_mac import (
    win,
    ball,
    left_border,
    right_border,
    top_border,
    bottom_border,
    line_45_top,
    line_45_bottom,
    line_135_top,
    line_135_bottom,
    occluder,
    inner_outline,
    fixation,
    horizontal_lines,
    vertical_lines,    
    occluder_square,
)

line_map = {
    "45_top":       line_45_top,
    "45_bottom":    line_45_bottom,
    "135_top":      line_135_top,
    "135_bottom":   line_135_bottom,
}

# win_dims = win.size

print(f"Screen dimensions: {win_dims}")

win.mouseVisible = False
occluder_opaque = False
# store frame rate of monitor if we can measure it
expInfo["frameRate"] = win.getActualFrameRate()
if expInfo["frameRate"] != None:
    frameDur = 1.0 / round(expInfo["frameRate"])
else:
    frameDur = 1.0 / 120.0  # could not measure, so guess

# get screen Hz for adjusting animations later
# gets your refresh rate and stores it in the frame rate object
refreshRate = round(expInfo["frameRate"], 0) if expInfo["frameRate"] != None else None

# init text to display on refresh info screen
refreshText = str()
refreshInformation = visual.TextStim(
    win=win,
    name="refreshInformation",
    text="",
    font="Open Sans",
    pos=(0, 0),
    height=0.05,
    wrapWidth=None,
    ori=0.0,
    color="white",
    colorSpace="rgb",
    opacity=None,
    languageStyle="LTR",
    depth=-1.0,
)

square_size = config["square_size"]
# square_size = min(win.size)  # Get the smallest dimension of the window
skip_factor = 1
n_trials = config["n_trials"]  # Number of trials
print(f"Number of trials: {n_trials}")
                
#####################OLD CODE #############################                
# interactor_trial_options = ["45_top_r", "45_top_u",
#                             "45_bottom_l", "45_bottom_d",
#                             "135_top_l", "135_top_u",
#                             "135_bottom_r", "135_bottom_d"]
# empty_trial_options = ["none_l", "none_r", "none_u", "none_d"]  # For the none trials

# # 4 * ["none"] ### FIX THAT NONE TRIALS DON'T GET A EDGE NOW BEECAUSE NO ____
edge_options = ["up", "down", "left", "right"]
# bounce_options = [True, False]
# rand_bounce_direction_options = ["left", "right"] * 2
# random.shuffle(rand_bounce_direction_options)
# ball_change_options = [True] * 1 + [False] * int((1 / config["target_baserate"]) - 1)
# rand_speed_change_options = ["slower", "faster"]
# natural_speed_variance = config["natural_speed_variance"]


# ball_speed_options = list(
#     np.arange(
#         avg_ball_speed - natural_speed_variance,
#         avg_ball_speed + (2 * natural_speed_variance),
#         natural_speed_variance,
#     )
# )

# trial_types = determine_sequence(n_trials, [1, 0], randomised=True) # 1 is interactor, 0 is empty trial

# interactor_trials = balance_over_bool(trial_types, interactor_trial_options, randomised=True)

# # Create deterministically randomised; balanced parameter sequences
# trials = determine_sequence(n_trials, trial_options, randomised=True)

# bounces = determine_sequence(n_trials, bounce_options, randomised=True)

# rand_bounce_directions = get_phantbounce_sequence(trials, rand_bounce_direction_options, randomised=True) # Random phantom bounce direction

# ball_changes = determine_sequence(n_trials, ball_change_options, randomised=True)
# rand_speed_changes = determine_sequence(
#     n_trials, rand_speed_change_options, randomised=True
# )
# ball_speeds = determine_sequence(n_trials, ball_speed_options, randomised=True)
####################################################################################################################
# design_matrix = create_balanced_trial_design(trial_n=n_trials)
design_matrix = build_design_matrix(n_trials, verbose=True)

check_balance(design_matrix)
trial_types = list(design_matrix["trial_type"])
trials = list(design_matrix["trial_option"])
bounces = list(design_matrix["bounce"])
rand_bounce_directions = list(design_matrix["phant_bounce_direction"])
ball_changes = list(design_matrix["ball_change"])
ball_speeds = list(design_matrix["ball_speed"])

ball_spawn_spread = config[
    "ball_spawn_spread"
]  # Margin around fixation where the ball can spawn (smaller = )

# Get ITI distribution based on randomly sampled truncated exponential decay
decay_steepness = 1.0
itis = truncated_exponential_decay(config["min_iti"], config["truncation_cutoff"], n_trials) # CHANGED THIS NOW (maandag 10MAART)
# itis = two_sided_truncated_exponential(config["mean_iti"], config["min_iti"], config["max_iti"], scale=decay_steepness, size=n_trials)

# Generate a random ITI for each trial
# itis = np.random.uniform(config["min_iti"], config["max_iti"], n_trials)

# MRI RELATED::::: DO I NEED TO HAVE MY JITTER, OR ITI VARIABILITY IN ACCORDANCE WITH MY TR? OR WHAT DO WE DO? 
# IN NSD, FOR EXAMPLE, THEY JUST HAVE THESE BLANK TRIALS
# READ UP ON MUMFORD'S STUFF ON COLLINEARITY AND SUCH, AS SHE ARGUES THAT
# A LOT OF METHODS TO OVERCOME COLINEARITY BETWEEN YOUR REGRESSORS ACTUALLY
# INTRODUCE NOVEL PROBLEMS.

# Define the start and end colors for the subtle hue change
# start_color = np.array([1.0, 1.0, 1.0])  # White
start_color = config["ball_fillcolor"]
fixation_changecolor = np.array([0.75, 0.75, 0.75])  # Light gray (colour for fixation change)
# occluder_color = np.array([-0.25, -0.25, -0.25]) # np.array([0.1, 0.1, 0.1])
# occluder_color = np.array([-.5, -.55, -.5]) # np.array([0.1, 0.1, 0.1])
# occluder_color = np.array([-.75, -.75, -.75]) # np.array([0.1, 0.1, 0.1])
# occluder_color = np.array([-1, -1, -1]) # np.array([0.1, 0.1, 0.1])

# occluder_color = np.array([.4, .4, 0]) # np.array([0.1, 0.1, 0.1]) (colour for ball hue change)
# occluder_color = np.array([.2, .2, -.2])
# occluder_color = np.array([0, .3, 0])
occluder_color = np.array(config["ball_changecolor"], dtype=float)
ball_color_new = np.array([0, 0, 0])




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
    instruction_read = event.waitKeys(keyList=["space"])[
        0
    ].upper()  # Ensures only one key is read

explanation_text_speed = visual.TextStim(
    win,
    text=(
        "In this task, you will see a ball moving towards the\n"
        "center of the screen, where it passes behind a square.\n\n"
        "On top of this square you'll see a small white cross: +  \n"
        "Keep your eyes focused on this cross during the whole trial.\n\n"
        "In some trials, the ball changes colour behind the occluder \n\n"
        "but quickly turns white again after reappearing.\n\n"
        "You are challenged to detect these changes.\n\n"
        "When you see a change, press the arrow key to indicate on what\n"
        "side of the square you saw the brief change of colour.\n\n"
        "Be as fast and accurate as possible!\n\n\n"
        "We'll unveil your score every 10 trials.\n\n"
        "Press 'Space' to start."
    ),
    color="white",
    pos=(0, 0),
    height=30,  # Adjust the height to a more reasonable value
    wrapWidth=1000,  # Set wrap width to ensure text wraps within the window
)

# while ready_to_start not in ["space"]:
while ready_to_start != "SPACE":

    explanation_text_speed.draw()
    win.flip()
    ready_to_start = event.waitKeys(keyList=["space"])[
        0
    ].upper()  # Ensures only one key is read


ball_change_type = "S" if task_choice != "Fixation Hue Change" else "H"
# task_choice = expInfo["task"][0]
task_choice = expInfo["task"]

for trial_number, trial in enumerate(trials):
    print(f"Trial number: {trial_number + 1}")
    trial_clock = core.Clock()  # Create a clock for the trial

    # start_positions, directions, fast_directions, slow_directions, skip_directions, wait_directions = (
    #     get_pos_and_dirs(
    #         avg_ball_speed, square_size, ball_spawn_spread, config["ball_speed_change"], ball_radius
    #     )
    # )
    
    start_positions, directions, fast_directions, slow_directions, skip_directions, wait_directions = (
        get_pos_and_dirs(
            avg_ball_speed, square_size, ball_spawn_spread, config["ball_speed_change"], ball_radius
        )
    )
    
    this_occluder_color = occluder_color
    np.random.shuffle(this_occluder_color)
    
    ########### DRAW FIXATION CROSS ###########
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    refreshInformation.setAutoDraw(True)
    fixation.draw()
    
    win.flip()
    print(f"EXACT Fixation time: {trial_clock.getTime()}s") if verbose else None
    core.wait(config["fixation_time"])

    ########### DRAW INTERACTOR LINE ###########
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    if trial[:-2] == "45_top":
        line_135_top.draw()
    elif trial[:-2] == "45_bottom":
        line_135_bottom.draw()
    elif trial[:-2] == "135_top":
        line_45_top.draw()
    elif trial[:-2] == "135_bottom":
        line_45_bottom.draw()
    if config["draw_grid"]:
        for line in horizontal_lines + vertical_lines:
            line.draw()
    fixation.draw()
    
    win.flip()
    print(f"EXACT interactor time: {trial_clock.getTime()}s") if verbose else None
    core.wait(config["interactor_time"])

    ########### DRAW OCCLUDER ###########
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()    
    if trial[:-2] == "45_top":
        line_135_top.draw()
    elif trial[:-2] == "45_bottom":
        line_135_bottom.draw()
    elif trial[:-2] == "135_top":
        line_45_top.draw()
    elif trial[:-2] == "135_bottom":
        line_45_bottom.draw()
    # inner_outline.draw()
    occluder.draw()
    occluder_square.draw()
    
    
    if config["draw_grid"]:
        for line in horizontal_lines + vertical_lines:
            line.draw()
    fixation.draw()
    
    win.flip()
    print(f"EXACT occluder time: {trial_clock.getTime()}s") if verbose else None
    core.wait(config["occluder_time"])

    # Extract start position letter from trial name
    if trial[:4] == "none":
        edge_letter = trial[-1]
    else:
        edge_letter = trial.split("_")[2]
        
    # Find the full edge option string
    edge = _flip_dir(next(option for option in edge_options if option.startswith(edge_letter)))

    print(f"Trial: {trial}")
    print(f"Edge letter: {edge_letter}")
    print(f"Actual edge: {edge}")
    print(f"Ball will bounce: {bounces[trial_number]}")

    ball.pos = np.array(start_positions[edge])
    # gaussian.pos = ball.pos
    velocity = np.array(directions[edge])

    bounce = bounces[trial_number]  # 50% chance to bounce
    rand_bounce_direction = rand_bounce_directions[trial_number]  # Random 90° phantom bounce direction
    # rand_speed_change = rand_speed_changes[trial_number]  # 50% chance to slow down or speed up
    ball_change = ball_changes[trial_number]  # 20% probability of target ball change
    this_ball_speed = ball_speeds[trial_number]  # Random ball speed
    this_iti = itis[trial_number]  # Random ITI

    print(f"Target trial: {ball_change}")


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
    hue_changed = False
    hue_changed_back = False
    pre_bounce_velocity = None
    bounced_phantomly = False
    
    trial_duration = (config["fixation_time"] + 
                      config["interactor_time"] + 
                      config["occluder_time"] + 
                      config["ballmov_time"]) # +
                    #   config["feedback_time"] + 
                    #   this_iti)
    
    
    print(f"Trial duration = {trial_duration}s") # if verbose else None

    ##################### NEW CODE, integrate with stuff abocve, where I intiisalise the exp_data
    # Store trial characteristics
    trial_no = len(exp_data["trial"]) + 1
    exp_data["trial"].append(trial_no)
    exp_data["trial_type"].append(trial_types[trial_no - 1])
    exp_data["interactor"].append(trial)
    exp_data["bounce"].append(bounce)  # Whether the ball will bounce
    exp_data["ball_speed"].append(this_ball_speed)
    exp_data["target_color"].append(this_occluder_color) if ball_change else exp_data["target_color"].append(None)
    
    # Append None placeholders
    placeholders = [
        "bounce_moment",
        "target_onset",
        "abs_congruent",
        "sim_congruent",
        "response",
        "accuracy",
        "rt",
        "end_pos",
        "abs_rfup",
        "abs_rfright",
        "abs_rfdown",
        "abs_rfleft",
        "sim_rfup",
        "sim_rfright",
        "sim_rfdown",
        "sim_rfleft",
    ]
    for key in placeholders:
        exp_data[key].append(None)

    # Conditional appends
    exp_data["random_bounce_direction"].append(
        rand_bounce_direction if bounce and trial[:4] == "none" else None # CHANGED HERE
    )

    # Append remaining values
    exp_data["ball_change"].append(ball_change)
    exp_data["start_pos"].append(edge)
    
    ballmov_time = 0 # MOVE TO BETTER PLACE
    enter_screen_time = None
    left_screen_time = None
    entered_screen = None
    #####################################
    print(f"EXACT ballmovstart time: {trial_clock.getTime()}s") 

    # **BALL MOVEMENT LOOP**
    while trial_clock.getTime() < trial_duration:
        # Realistic ball speed decay, helps a lot
        decay_factor = calculate_decay_factor(this_ball_speed, ballmov_time, trial_duration, constant=config["decay_constant"])
        velocity = [velocity[0] * decay_factor, velocity[1] * decay_factor] 
        ball.pos += tuple([velocity[0] * skip_factor, velocity[1] * skip_factor])
                
        # Update elapsed time (assuming you have a way to measure time, e.g., using a clock)
        ballmov_time += config["frame_rate"]  # time_step should be the time increment per loop iteration

        if (np.linalg.norm(ball.pos) > square_size / 2) and trial_clock.getTime() < (trial_duration // 2):
            enter_screen_time = trial_clock.getTime()
            # print(f"OUT OF BOUNDS at {trial_clock.getTime():.3f}") 
            entered_screen = True
        
        if (entered_screen and 
            enter_screen_time != None and 
            left_screen_time == None and
            trial_clock.getTime() > (trial_duration // 2) and
            (np.linalg.norm(ball.pos) > square_size // 2)):
            left_screen_time = trial_clock.getTime()
            screen_time = left_screen_time - enter_screen_time
            print(f"LEFT SCREEN AT {left_screen_time:.3f}")
            print(f"SCREEN TIME: {screen_time:.3f}")
                    
        if trial_clock.getTime() % 0.5 < 0.02 and verbose:
            print(f"Screen refresh rate: {refreshRate}")  # At 75 Hz in UB singel
            
        #################### NORMAL BOUNZZZZZ ####################
        if will_cross_fixation(ball.pos, velocity, skip_factor) and bounce and trial[:4] != "none":
            pre_bounce_velocity = np.max(np.abs(velocity)) if pre_bounce_velocity == None else pre_bounce_velocity
            if trial[:2] == "45":
                print(f"BOUNCED on 45 at {trial_clock.getTime()}") #if verbose else None
                velocity = collide(_flip_dir(edge), 45, pre_bounce_velocity)  # Reflect off 45°
                bounce_moment = trial_clock.getTime()

            elif trial[:3] == "135":
                print(f"BOUNCED on 135 at {trial_clock.getTime()}") #if verbose else None
                velocity = collide(_flip_dir(edge), 135, pre_bounce_velocity)  # Reflect off 135°
                bounce_moment = trial_clock.getTime()

            bounce = False  # Prevent double bouncing
            crossed_fixation = True

        # Draw on each frame
        ball.draw()
        left_border.draw()
        right_border.draw()
        top_border.draw()
        bottom_border.draw()
        
        if trial[:-2] == "45_top":
            line_135_top.draw()
        elif trial[:-2] == "45_bottom":
            line_135_bottom.draw()
        elif trial[:-2] == "135_top":
            line_45_top.draw()
        elif trial[:-2] == "135_bottom":
            line_45_bottom.draw()
            
        if config["draw_grid"]:
            for line in horizontal_lines + vertical_lines:
                line.draw()

        occluder.draw() # if occluder_opaque else occluder_glass.draw()
        occluder_square.draw()
        fixation.draw()
        
        win.flip()
        core.wait(config["frame_rate"])  # Smooth animation, for 60 Hz do (1/60) which is 0.0166667

        skip_factor = 1 # leftover from old ball hiccup implementation, but move upwads later on
            

        if will_cross_fixation(ball.pos, velocity, skip_factor):

            if bounce and trial[:4] == "none":
                pre_bounce_velocity = np.max(np.abs(velocity)) if pre_bounce_velocity == None else pre_bounce_velocity

                print("FENTOM BAUNZZZZZ")
                print("Phantom bounce") if verbose else None
                if rand_bounce_direction == "left":

                    (
                        print(f"BOUNCED LEFT at {trial_clock.getTime()}")
                        if verbose
                        else None
                    )
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "left"), pre_bounce_velocity 
                    )  # Reflect off 45°

                elif rand_bounce_direction == "right":

                    (
                        print(f"BOUNCED RIGHT at {trial_clock.getTime()}")
                        if verbose
                        else None
                    )
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "right"), pre_bounce_velocity 
                    )  # Reflect off 135
                
                bounced_phantomly = True
                bounce_moment = (trial_clock.getTime()) 
                
            elif not bounce and not bounced_phantomly:
                bounce_moment = (
                    trial_clock.getTime()
                )  # if bounce_moment == None else bounce_moment # MAYBE WILL DO THE TRICK
            
            bounce = False                
            crossed_fixation = True
            print(f"crossed fixation at {trial_clock.getTime()}") if verbose else None


        # USED TO BE ELIF, BUT SHOULDN'T MAKE SENSE
        # Check if ball is about to leave occluder
        if (
            np.linalg.norm(ball.pos) > occluder_radius - (ball_radius * 2.0) # WAS 1.5!!!
            and crossed_fixation
            and not left_occluder
        ):  # Make sure to start counting after exiting the occluder
            print(f"occluder exit time: {trial_clock.getTime():.2f}")
            occluder_exit_moment = trial_clock.getTime()
            left_occluder = True

        # elif (
        if (
            bounce == False
        ):  # If the ball has bounced, or won't bounce at all (for continuation)
            if (
                crossed_fixation and ball_change_moment == None and left_occluder
            ):  # If bounce not yet registered, and ball has crossed fixation
                (
                    print(
                        f"ball_change_MOMENT: {occluder_exit_moment + ball_change_delay}"
                    )
                    if verbose
                    else None
                )
                ball_change_moment = occluder_exit_moment + ball_change_delay
                exp_data["target_onset"][-1] = (
                    ball_change_moment if ball_change else None
                )
            if bounce_moment != None and ball_change_moment != None:
                elapsed_time = trial_clock.getTime() - ball_change_moment

                duration = config["hue_change_duration"]  # Duration of the color change in seconds
                ball_duration = config["ball_change_duration"]  # Duration of the color change in seconds
                factor = min(elapsed_time / duration, 1.0)  # Ensure factor is between 0 and 1
                ball_factor = min(elapsed_time / ball_duration, 1.0)  # Ensure factor is between 0 and 1

                if task_choice == "Fixation Hue Change" and ball_change and not hue_changed_back:
                    if not hue_changed:
                        fixation.color = interpolate_color(start_color, fixation_changecolor, factor)
                        if np.all(fixation.color == fixation_changecolor):  # Check if the color has fully changed
                            hue_changed = True  # Hue change confirmation toggle
                            ball_change_moment = trial_clock.getTime()  # Reset the change moment
                            print(f"KLEUR changed to fixation_changecolor at {trial_clock.getTime()}") if verbose else None
                    else:
                        elapsed_time_inv = trial_clock.getTime() - ball_change_moment
                        factor_inv = min(elapsed_time_inv / duration, 1.0)
                        fixation.color = interpolate_color(fixation_changecolor, start_color, factor_inv)
                        if np.all(fixation.color == start_color):  # Check if the color has fully changed back
                            hue_changed_back = True  # Reset the hue change confirmation toggle
                            print(f"KLEUR changed back to start_color at {trial_clock.getTime()}") if verbose else None
                            print("Hue change") # if verbose else None

                
                if task_choice == "Ball Hue" and ball_change and not hue_changed_back:
                
                    if not hue_changed:
                        ball.color = this_occluder_color  

                        hue_changed = True  # Hue change confirmation toggle
                        print(f"KLEUR changed to fixation_changecolor at {trial_clock.getTime()}") if verbose else None
                    else:                        
                        ball.color = interpolate_color(this_occluder_color, start_color, ball_factor)

                        if np.all(ball.color == this_occluder_color):  # Check if the color has fully changed back # CHECK IF THIS SHIT IS CORRECT
                            hue_changed_back = True  # Reset the hue change confirmation toggle 
                            print(f"KLEUR changed back to start_color at {trial_clock.getTime()}") if verbose else None
                            print("Hue change") # if verbose else None


        ball_direction = velocity_to_direction(velocity)
        bounce_moment = bounced_at if bounce_moment == None else bounce_moment
        exp_data["bounce_moment"][-1] = (
            bounce_moment if _flip_dir(ball_direction) != edge else None
        )  # Check whether the ball hasn't just continued
        exp_data["end_pos"][-1] = ball_direction  # log end position

        toetsen = event.getKeys(
            ["space", "left", "right", "up", "down", "escape", "r", "o"]
        )  # Construction set

        # **CHECK FOR 'R' TO SKIP TRIAL OR 'ESCAPE' TO QUIT**
        if "escape" in toetsen:
            print("ESCAPE PRESSED")
            win.close()
            core.quit()

        if toetsen != [] and not responded:  # If toets pressed and not done so before
            print(f"Response: {toetsen[0]}")
            
            if not crossed_fixation:  # If too early
                print(f"Wrong, too early")
                feedback_text = "Wrong, too early"
                exp_data["response"][-1] = toetsen[0]  # Log the response
                correct_response = None  # To prevent logging an accuracy value
                responded = True  # QUIT LOOP??
            else:  # If on time
                toets_moment = trial_clock.getTime()  # Get the moment of response
                exp_data["response"][-1] = toetsen[0]  # Log the response
                exp_data["rt"][-1] = (
                    toets_moment - ball_change_moment
                )  # Log the reaction time

                if ball_change:  # If there was a target change
                    if task_choice[0] == "B" and toetsen[0] in [
                        "left",
                        "right",
                        "up",
                        "down",
                    ]:
                        hue_or_speed = "hue" if ball_change_type == "H" else "speed"
                        exp_data["response"][-1] = toetsen[0]
                        exp_data["rt"][-1] = toets_moment - ball_change_moment
                        if toets_moment < ball_change_moment:
                            feedback_text = (
                                f"Responded too early"  # if give_feedback else ""
                            )
                            print(f"Wrong, TOO EARLY")
                            correct_response = False
                        elif ball_direction == toetsen[0]:
                            feedback_text = (
                                f"Correct! detected hue change of {toetsen[0]}ward ball in {round(toets_moment - ball_change_moment, 3)}s"
                                if give_feedback
                                else ""
                            )
                            print(
                                f"Correct! detected hue change of {toetsen[0]}ward ball in {round(toets_moment - ball_change_moment, 3)}s"
                            )
                            correct_response = True
                        else:
                            feedback_text = (
                                f"Wrong direction, should be a hue change of {ball_direction}ward ball"
                                if give_feedback
                                else ""
                            )
                            print(
                                f"Wrong direction, should be a hue change of {ball_direction}ward ball"
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
                feedback_text = (
                    f"Undetected ball change, there was a hue change of the {ball_direction}ward ball"
                    if give_feedback
                    else ""
                )
                correct_response = False
                print(feedback_text)
            else:
                feedback_text = ""
                correct_response = None
                print(feedback_text)

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
        
    if (trial_number + 1) % feedback_freq == 0: # and trial_number > 10:
        intermit_data = pd.DataFrame(exp_data)
        intermit_rt = np.mean(intermit_data["rt"].dropna())
        feedback_text = f'Detected changes: {(get_hit_rate(intermit_data, sim_con=None, expol_con=None)*100):.2f}%\nAverage speed: {intermit_rt:.2f}s'
        
        
        # Show the break with countdown
        show_break(win, duration=10)
    else:
        feedback_text = ""

    feedback = visual.TextStim(
        win, text=feedback_text, color="white", pos=(0, 100), height=30
    )
    left_border.draw()
    right_border.draw()
    top_border.draw()
    bottom_border.draw()
    feedback.draw()
    fixation.draw()
    
    win.flip()
    core.wait(config["feedback_time"])

    # Reset ball and fixation color to original after each trial
    ball.fillColor = config["ball_fillcolor"]
    ball.lineColor = config["ball_linecolor"]
    fixation.color = config["fixation_color"]
    
    
    df = pd.DataFrame(exp_data)


    if trial_no // 10 == 0:
        # Save the DataFrame to a CSV file
        subject_id = expInfo["participant"]
        task_name = expInfo["task"].lower().replace(" ", "_")
        save_performance_data(expInfo["participant"], task_name, df, intermediate=True)
        save_performance_data(expInfo["participant"], task_name, design_matrix, design_matrix=True, intermediate=True)

win.close()

df = pd.DataFrame(exp_data)

# Save the DataFrame to a CSV file
subject_id = expInfo["participant"]
task_name = expInfo["task"].lower().replace(" ", "_")
save_performance_data(expInfo["participant"], task_name, df)
save_performance_data(expInfo["participant"], task_name, design_matrix, design_matrix=True)





