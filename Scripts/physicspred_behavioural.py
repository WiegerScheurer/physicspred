#!/usr/bin/env python3

# Import necessary libraries
from psychopy import visual, core, event, gui, data
import numpy as np
import random
import yaml
import pandas as pd
import os
import sys
import time

# Add repository to path
sys.path.append("/Users/wiegerscheurer/repos/physicspred")

# Import custom functions
from functions.utilities import (
    setup_folders,
    save_performance_data,
    interpolate_color,
    build_design_matrix,
    bellshape_sample,
    ordinal_sample,
    oklab_to_rgb,
    truncated_exponential_decay,
    get_pos_and_dirs,
    check_balance,
)
from functions.physics import (
    check_collision,
    collide,
    velocity_to_direction,
    predict_ball_path,
    _flip_dir,
    _rotate_90,
    _dir_to_velocity,
    will_cross_fixation,
    calculate_decay_factor
)
from functions.analysis import get_hit_rate

# Function for displaying breaks between trials
def show_break(win, duration=10, button_order={"lighter": "m", "darker": "x"}):
    longer_str = " longer" if duration > 10 else ""
    
    clock = core.Clock()
    countdown_text = visual.TextStim(win, text='', pos=(0, 0), height=20)
    break_text = visual.TextStim(
        win, 
        text=f'You deserve a{longer_str} break now.\n\nRemember: \n{button_order["lighter"]} for lighter\n{button_order["darker"]} for darker\n\nPress space to continue.', 
        pos=(0, 70), 
        height=30
    )
    
    while clock.getTime() < duration:
        remaining_time = duration - int(clock.getTime())
        countdown_text.text = f'\n\n\n\n\n\nBreak ends in {remaining_time} seconds'
        countdown_text.draw()
        break_text.draw()
        win.flip()
        
        keys = event.getKeys(keyList=['space'])
        if 'space' in keys:
            break

    # Clear any remaining key presses
    event.clearEvents()

# Load configuration file
config_path = os.path.join(os.path.dirname(__file__), os.pardir, "config_lumin.yaml")
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Extract configuration parameters
datadir = config["datadir"]
win_dims = config['win_dims']
avg_ball_speed = config["avg_ball_speed"]
ball_radius = config["ball_radius"]
interactor_height = config["interactor_height"]
interactor_width = config["interactor_width"]
occluder_radius = config["occluder_radius"]
verbose = config["verbose"]
exp_parameters = config["exp_parameters"]
feedback_freq = config["feedback_freq"]
n_trials = config["n_trials"]
square_size = config["square_size"]

# Set up button mappings
buttons = ["m", "x"]
random.shuffle(buttons)
button_order = {"lighter": buttons[0], "darker": buttons[1]}

# Initialize experiment data dictionary
exp_data = {par: [] for par in exp_parameters}

# Set up experiment directory
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Set up experiment info
expName = "IPE_SpatTemp_Pred_Behav"
expInfo = {
    "participant": f"sub-{random.randint(0, 999999):06.0f}",
    "session": "001",
    "task": ["Ball Hue", "Ball Hiccup", "Ball Speed Change", "Fixation Hue Change"],
    "feedback": ["No", "Yes"],
}

# Show participant dialog and get input
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if dlg.OK == False:
    core.quit()  # User pressed cancel

# Add timestamp and experiment info
expInfo["date"] = data.getDateStr()
expInfo["expName"] = expName
expInfo["psychopyVersion"] = config["psychopy_version"]
give_feedback = True if expInfo["feedback"] == "Yes" else False

# Import task components
from objects.task_components import (
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
    fixation,
    horizontal_lines,
    vertical_lines,    
    draw_screen_elements,
)

# Create a mapping for lines to simplify code later
line_map = {
    "45_top": line_45_top,
    "45_bottom": line_45_bottom,
    "135_top": line_135_top,
    "135_bottom": line_135_bottom,
}

# Hide mouse cursor and set up window
win.mouseVisible = False

# Get and store frame rate of monitor
expInfo["frameRate"] = win.getActualFrameRate()
frameDur = 1.0 / round(expInfo["frameRate"]) if expInfo["frameRate"] != None else 1.0 / 120.0
refreshRate = round(expInfo["frameRate"], 0) if expInfo["frameRate"] != None else None

# Create text stimuli for refresh information
refreshText = str()
refreshInformation = visual.TextStim(
    win=win,
    name="refreshInformation",
    text="",
    font="Arial",#"Open Sans",
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

# Define edge options
edge_options = ["up", "down", "left", "right"]

# Create experiment design matrix
design_matrix = build_design_matrix(
    n_trials=n_trials,
    change_ratio=[True],
    ball_color_change_mean=config["ball_color_change_mean"],
    ball_color_change_sd=config["ball_color_change_sd"],
    verbose=verbose,
    neg_bias_factor=config["neg_bias_factor"]
)

if verbose:
    check_balance(design_matrix)
    print(f'Ball changes: {list(ordinal_sample(config["ball_color_change_mean"], config["ball_color_change_sd"], n_elements=5, round_decimals=3))}')

# Extract trial parameters from design matrix
trial_types = list(design_matrix["trial_type"])
trials = list(design_matrix["trial_option"])
bounces = list(design_matrix["bounce"])
rand_bounce_directions = list(design_matrix["phant_bounce_direction"])
ball_changes = list(design_matrix["ball_change"])
ball_color_changes = list(design_matrix["ball_luminance"])

# Generate ball speeds and starting colors
ball_speeds = bellshape_sample(float(avg_ball_speed), float(config["natural_speed_variance"]), n_trials)
ball_start_colors = bellshape_sample(float(config["ball_start_color_mean"]), float(config["ball_start_color_sd"]), n_trials)
ball_spawn_spread = config["ball_spawn_spread"]

# Generate inter-trial intervals
itis = truncated_exponential_decay(config["min_iti"], config["max_iti"], n_trials)

# Define fixation change color
fixation_changecolor = np.array([0.75, 0.75, 0.75])  # Light gray

# Display welcome screen
welcome_text = visual.TextStim(
    win,
    text=f"Welcome! Today you will perform the {expInfo['task']} task.\n\nPress 'Space' to continue.",
    color="white",
    pos=(0, 0),
    height=30,
)

instruction_read = ""
while instruction_read != "SPACE":
    welcome_text.draw()
    win.flip()
    instruction_read = event.waitKeys(keyList=["space"])[0].upper()

# Display task instructions
explanation_text_speed = visual.TextStim(
    win,
    text=(
        "In this task, you will see a ball moving towards the\n"
        "center of the screen, where it passes behind a square.\n\n"
        "On top of this square you'll see a small red cross: +  \n"
        "Keep your eyes focused on this cross during the whole trial.\n\n"
        "The ball changes colour when behind the occluder \n\n"
        "You are challenged to detect these changes.\n\n"
        f"If the ball becomes lighter, press {button_order['lighter']}\n"
        f"If the ball becomes darker, press {button_order['darker']}\n"
        "Be as fast and accurate as possible!\n\n\n"
        f"We'll unveil your score every {config['feedback_freq']} trials.\n\n"
        "Press 'Space' to start."
    ),
    color="white",
    pos=(0, 0),
    height=30,
    wrapWidth=1000,
)

ready_to_start = ""
while ready_to_start != "SPACE":
    explanation_text_speed.draw()
    win.flip()
    ready_to_start = event.waitKeys(keyList=["space"])[0].upper()

# Set task type
task_choice = expInfo["task"]
ball_change_type = "S" if task_choice != "Fixation Hue Change" else "H"

# Start time tracking
start_time = time.time()

# MAIN EXPERIMENTAL LOOP
for trial_number, trial in enumerate(trials):
    if verbose:
        print(f"Trial number: {trial_number + 1}")
    
    trial_clock = core.Clock()
    
    # Get positions and directions for ball movement
    start_positions, directions, fast_directions, slow_directions, skip_directions, wait_directions = get_pos_and_dirs(
        avg_ball_speed, square_size, ball_spawn_spread, config["ball_speed_change"], ball_radius
    )
    
    # Set up ball color
    ball_start_color = ball_start_colors[trial_number]
    ball_color_change = ball_color_changes[trial_number]
    changed_ball_color = oklab_to_rgb([(ball_start_color + ball_color_change), 0, 0], psychopy_rgb=True)
    start_color = np.clip(ball_start_color, -1, 1)
    ball.color = np.clip(oklab_to_rgb([ball_start_color, 0, 0], psychopy_rgb=True), -1, 1)
    
    # FIXATION CROSS DISPLAY
    draw_screen_elements(None)
    refreshInformation.setAutoDraw(True)
    win.flip()
    
    if verbose:
        print(f"Exact Fixation time: {trial_clock.getTime()}s")
    core.wait(config["fixation_time"])
    
    # INTERACTOR LINE DISPLAY
    draw_screen_elements(trial, draw_grid=True)
    win.flip()
    
    if verbose:
        print(f"Exact interactor time: {trial_clock.getTime()}s")
    core.wait(config["interactor_time"])
    
    # OCCLUDER DISPLAY
    draw_screen_elements(trial, draw_occluder=True, draw_grid=True)
    win.flip()
    
    if verbose:
        print(f"Exact occluder time: {trial_clock.getTime()}s")
    core.wait(config["occluder_time"])
    
    # Extract start position letter from trial name
    if trial[:4] == "none":
        edge_letter = trial[-1]
    else:
        edge_letter = trial.split("_")[2]
        
    # Find the full edge option string
    edge = _flip_dir(next(option for option in edge_options if option.startswith(edge_letter)))
    
    if verbose:
        print(f"Trial: {trial}")
        print(f"Edge letter: {edge_letter}")
        print(f"Actual edge: {edge}")
        print(f"Ball will bounce: {bounces[trial_number]}")
    
    # Set ball position and velocity
    ball.pos = np.array(start_positions[edge])
    velocity = np.array(directions[edge])
    
    # Get trial parameters
    bounce = bounces[trial_number]
    rand_bounce_direction = rand_bounce_directions[trial_number]
    ball_change = ball_changes[trial_number]
    this_ball_speed = ball_speeds[trial_number]
    this_iti = itis[trial_number]
    
    if verbose:
        print(f"Target trial: {ball_change}")
    
    # Initialize trial variables
    ball_change_delay = 0
    bounce_moment = None
    correct_response = None
    crossed_fixation = False
    responded = False
    left_occluder = False
    ball_change_moment = None
    occluder_exit_moment = None
    hue_changed = False
    hue_changed_back = False
    pre_bounce_velocity = None
    bounced_phantomly = False
    
    # Calculate trial duration
    trial_duration = (
        config["fixation_time"] + 
        config["interactor_time"] + 
        config["occluder_time"] + 
        config["ballmov_time"]
    )
    
    if verbose:
        print(f"Trial duration = {trial_duration}s")
    
    # Store trial characteristics
    trial_no = len(exp_data["trial"]) + 1
    exp_data["trial"].append(trial_no)
    exp_data["trial_type"].append(trial_types[trial_no - 1])
    exp_data["interactor"].append(trial)
    exp_data["bounce"].append(bounce)
    exp_data["ball_speed"].append(this_ball_speed)
    exp_data["ball_start_color"].append(ball_start_color)
    exp_data["ball_color_change"].append(ball_color_change)
    exp_data["target_color"].append(changed_ball_color if ball_change else None)
    
    # Initialize placeholders for data that will be filled during trial
    placeholders = [
        "bounce_moment", "target_onset", "abs_congruent", "sim_congruent",
        "response", "accuracy", "rt", "end_pos", "abs_rfup", "abs_rfright",
        "abs_rfdown", "abs_rfleft", "sim_rfup", "sim_rfright", 
        "sim_rfdown", "sim_rfleft"
    ]
    for key in placeholders:
        exp_data[key].append(None)
    
    # Add bounce direction data
    exp_data["random_bounce_direction"].append(
        rand_bounce_direction if bounce and trial[:4] == "none" else None
    )
    
    # Add remaining trial data
    exp_data["ball_change"].append(ball_change)
    exp_data["start_pos"].append(edge)
    
    # Initialize ball movement variables
    ballmov_time = 0
    enter_screen_time = None
    left_screen_time = None
    entered_screen = None
    
    if verbose:
        print(f"Exact ballmovstart time: {trial_clock.getTime()}s")
    
    # BALL MOVEMENT LOOP
    while trial_clock.getTime() < trial_duration:
        # Apply ball speed decay
        decay_factor = calculate_decay_factor(
            this_ball_speed, ballmov_time, trial_duration, constant=config["decay_constant"]
        )
        velocity = [velocity[0] * decay_factor, velocity[1] * decay_factor]
        ball.pos += tuple([velocity[0] * 1, velocity[1] * 1])  # Using skip_factor=1
        
        # Update elapsed time
        ballmov_time += config["frame_rate"]
        
        # Track when ball enters and leaves screen
        if (np.linalg.norm(ball.pos) > square_size / 2) and trial_clock.getTime() < (trial_duration // 2):
            enter_screen_time = trial_clock.getTime()
            entered_screen = True
        
        if (entered_screen and 
            enter_screen_time is not None and 
            left_screen_time is None and
            trial_clock.getTime() > (trial_duration // 2) and
            (np.linalg.norm(ball.pos) > square_size // 2)):
            left_screen_time = trial_clock.getTime()
            if verbose:
                screen_time = left_screen_time - enter_screen_time
                print(f"LEFT SCREEN AT {left_screen_time:.3f}")
                print(f"SCREEN TIME: {screen_time:.3f}")
        
        # Handle normal bounce
        if will_cross_fixation(ball.pos, velocity, 1) and bounce and trial[:4] != "none":
            pre_bounce_velocity = np.max(np.abs(velocity)) if pre_bounce_velocity is None else pre_bounce_velocity
            if trial[:2] == "45":
                if verbose:
                    print(f"BOUNCED on 45 at {trial_clock.getTime()}")
                velocity = collide(_flip_dir(edge), 45, pre_bounce_velocity)
                bounce_moment = trial_clock.getTime()
            elif trial[:3] == "135":
                if verbose:
                    print(f"BOUNCED on 135 at {trial_clock.getTime()}")
                velocity = collide(_flip_dir(edge), 135, pre_bounce_velocity)
                bounce_moment = trial_clock.getTime()
            
            bounce = False
            crossed_fixation = True
        
        # Draw the current frame
        ball.draw()
        draw_screen_elements(trial, draw_occluder=True, draw_grid=config["draw_grid"])
        win.flip()
        core.wait(config["frame_rate"])
        
        # Handle phantom bounce or fixation crossing
        if will_cross_fixation(ball.pos, velocity, 1):
            if bounce and trial[:4] == "none":
                pre_bounce_velocity = np.max(np.abs(velocity)) if pre_bounce_velocity is None else pre_bounce_velocity
                
                if verbose:
                    print("Phantom bounce")
                
                if rand_bounce_direction == "left":
                    if verbose:
                        print(f"BOUNCED LEFT at {trial_clock.getTime()}")
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "left"), pre_bounce_velocity
                    )
                elif rand_bounce_direction == "right":
                    if verbose:
                        print(f"BOUNCED RIGHT at {trial_clock.getTime()}")
                    velocity = _dir_to_velocity(
                        _rotate_90(_flip_dir(edge), "right"), pre_bounce_velocity
                    )
                
                bounced_phantomly = True
                bounce_moment = trial_clock.getTime()
            
            elif not bounce and not bounced_phantomly:
                bounce_moment = trial_clock.getTime()
            
            bounce = False
            crossed_fixation = True
            
            if verbose:
                print(f"crossed fixation at {trial_clock.getTime()}")
        
        # Check if ball is leaving occluder. This is not Exact, but the moment the ball is in the middle.
        # if (np.linalg.norm(ball.pos) > (occluder_radius / 2) - (ball_radius * 2.0)
        if (np.linalg.norm(ball.pos) > (occluder_radius / 2) - (ball_radius * 2)
            and crossed_fixation
            and not left_occluder):
            
            if verbose:
                print(f"occluder exit time: {trial_clock.getTime():.2f}")
            print(f"LEAVING OCCLUDER NOW!! exit time: {trial_clock.getTime():.2f}")
            

            occluder_exit_moment = trial_clock.getTime()
            left_occluder = True
        
        # Handle ball changes after occluder exit
        if bounce == False:
            if crossed_fixation and ball_change_moment is None and left_occluder:
                
                if verbose:
                    print(f"ball_change_moment: {occluder_exit_moment + ball_change_delay}")
                
                ball_change_moment = occluder_exit_moment + ball_change_delay
                exp_data["target_onset"][-1] = ball_change_moment if ball_change else None
            
            if task_choice == "Ball Hue" and crossed_fixation and ball_change_moment is None:
                ball.color = changed_ball_color

        
        # Record ball direction and bounce moment
        ball_direction = velocity_to_direction(velocity)
        # bounce_moment = bounce_moment
        exp_data["bounce_moment"][-1] = bounce_moment if _flip_dir(ball_direction) != edge else None
        exp_data["end_pos"][-1] = ball_direction
        
        # Check for key presses
        keys = event.getKeys(["space", "x", "m", "escape"])
        
        if "escape" in keys:
            print("ESCAPE PRESSED")
            win.close()
            core.quit()
        
        if keys and not responded:
            if verbose:
                print(f"Response: {keys[0]}")
            
            # if not crossed_fixation:
            if not left_occluder:
                print(f"Wrong, too early")
                feedback_text = "Wrong, too early"
                exp_data["response"][-1] = keys[0]
                correct_response = None
                responded = True
            else:
                toets_moment = trial_clock.getTime()
                exp_data["response"][-1] = keys[0]
                exp_data["rt"][-1] = toets_moment - ball_change_moment
                
                if ball_change and task_choice[0] == "B" and keys[0] in ["x", "m"]:
                    hue_or_speed = "hue" if ball_change_type == "H" else "speed"
                    
                    if keys[0] == button_order["lighter"]:
                        this_response = "lighter"
                    elif keys[0] == button_order["darker"]:
                        this_response = "darker"
                    
                    if (this_response == "lighter" and ball_color_change > 0) or (this_response == "darker" and ball_color_change < 0):
                        print(f"Correct! detected a {this_response} ball in {round(toets_moment - ball_change_moment, 3)}s")
                        correct_response = True
                    elif ball_color_change == 0:
                        correct_response = None
                    elif (this_response == "lighter" and ball_color_change < 0) or (this_response == "darker" and ball_color_change > 0):
                        print(f"Wrong answer, the ball didn't become {this_response}")
                        correct_response = False
                    
                    exp_data["response"][-1] = this_response
                    exp_data["rt"][-1] = toets_moment - ball_change_moment
                    
                    if toets_moment < ball_change_moment:
                        feedback_text = "Responded too early"
                        print(f"Wrong, TOO EARLY")
                        correct_response = False
                else:
                    if ball_change:
                        print(f"Wrong, there was no change")
                        feedback_text = "Wrong, there was no change"
                        correct_response = False
                
                responded = True
        elif trial_clock.getTime() > trial_duration and not responded:
            if ball_change:
                feedback_text = f"Undetected ball change, there was a hue change of the {ball_direction}ward ball" if give_feedback else ""
                correct_response = False
                if verbose:
                    print(feedback_text)
            else:
                feedback_text = ""
                correct_response = None
                if verbose:
                    print(feedback_text)
        
        exp_data["accuracy"][-1] = correct_response
    
    # Calculate predictions for ball path
    for hypothesis in ["abs", "sim"]:
        pred_to_input = predict_ball_path(
            hypothesis=hypothesis,
            interactor=trial,
            start_pos=edge,
            end_pos=exp_data["end_pos"][-1],
            plot=False,
        )
        exp_data[f"{hypothesis}_congruent"][-1] = False
        for location in pred_to_input.keys():
            exp_data[f"{hypothesis}_rf{location}"][-1] = pred_to_input[location]
            if sum(pred_to_input[location]) == 2:
                exp_data[f"{hypothesis}_congruent"][-1] = True
    
    # Show feedback at specified intervals
    if (trial_number + 1) % feedback_freq == 0:
        intermit_data = pd.DataFrame(exp_data)
        intermit_rt = np.mean(intermit_data["rt"].dropna())
        feedback_text = (
            f'Progress: {trial_number + 1}/{n_trials}\n'
            f'Detected changes: {(get_hit_rate(intermit_data, sim_con=None, expol_con=None)*100):.2f}%\n'
            f'Average speed: {intermit_rt:.2f}s\n\n'
            f'Remember: \n{button_order["lighter"]} for lighter\n{button_order["darker"]} for darker'
        )
        
        subject = expInfo["participant"]
        os.makedirs(f"{datadir}/{subject}", exist_ok=True)
        intermit_data.to_csv(f"{datadir}/{subject}/intermit_data.csv")
        
        if (trial_number + 1) % (n_trials // 2) == 0 and (trial_number + 1 != n_trials):
            # Halfway break
            show_break(win, duration=30, button_order=button_order)
            
            feedback = visual.TextStim(
                win, text=feedback_text, color="white", pos=(0, 150), height=30
            )
            draw_screen_elements(None)
            feedback.draw()
            win.flip()
            core.wait(config["feedback_time"])
        else:
            # Regular break
            show_break(win, duration=10, button_order=button_order)
            
            feedback = visual.TextStim(
                win, text=feedback_text, color="white", pos=(0, 150), height=30
            )
            draw_screen_elements(None)
            feedback.draw()
            win.flip()
            core.wait(config["feedback_time"])
    else:
        feedback_text = ""

# Close the window and save all data
win.close()

# Create final dataframe and save results
df = pd.DataFrame(exp_data)
subject_id = expInfo["participant"]
task_name = expInfo["task"].lower().replace(" ", "_")
save_performance_data(expInfo["participant"], task_name, df, base_dir=datadir)
save_performance_data(expInfo["participant"], task_name, design_matrix, design_matrix=True, base_dir=datadir)

# Record timing information
end_time = time.time()
elapsed_time = end_time - start_time
timing_df = pd.DataFrame({"n_trials": [n_trials], "time_elapsed": [elapsed_time]})
timing_df.to_csv(f"{datadir}/{subject}/timing.csv")