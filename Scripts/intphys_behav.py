from psychopy import visual, core, event
import numpy as np
import random
import math
import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append("/Users/wiegerscheurer/repos/physicspred") # To enable importing from repository folders

from functions.utilities import setup_folders, save_performance_data
from functions.physics import check_collision, collide, velocity_to_direction, predict_ball_path

win_dims = [1000, 1000]
ball_speed = 5
verbose = False

exp_data = {
    "trial": [],
    "interactor": [],
    "bounce": [],
    "bounce_moment": [],
    "random_bounce_direction": [],
    "target_onset": [],
    "speed_change": [],
    "hue_change": [],
    "abs_congruent": [],
    "sim_congruent": [],
    "response": [],
    "accuracy": [],
    "rt": [],
    "start_pos": [],
    "end_pos": [],
    "abs_rftop": [],
    "abs_rfright": [],
    "abs_rfdown": [],
    "abs_rfleft": [],
    "sim_rftop": [],
    "sim_rfright": [],
    "sim_rfdown": [],
    "sim_rfleft": []
}

    
# Setup the window
win = visual.Window(win_dims, color='black', units='pix', fullscr=False)

# Define stimuli
fixation = visual.TextStim(win, text='+', color='white', pos=(0, 0), height=40)
line_45 = visual.Line(win, start=(-50, -50), end=(50, 50), lineWidth=5, lineColor='red')
line_135 = visual.Line(win, start=(-50, 50), end=(50, -50), lineWidth=5, lineColor='red')
occluder = visual.Circle(win, radius=100, fillColor='grey', lineColor='grey', pos=(0, 0))

# Define ball
ball = visual.Circle(win, radius=40, fillColor='white', lineColor='white')

# Define trial conditions
# trial_conditions = ["45", "135", "none"] * 10
# trial_conditions = ["45", "135", "none"] * 1
trial_conditions = ["45", "45", "45"] * 1
random.shuffle(trial_conditions)

# Possible starting positions and movement directions
start_positions = {
    "top": (0, win_dims[0]//2), "down": (0, -win_dims[0]//2), "left": (-win_dims[1]//2, 0), "right": (win_dims[1]//2, 0)
}
directions = {
    "top": (0, -ball_speed), "down": (0, ball_speed), "left": (ball_speed, 0), "right": (-ball_speed, 0)
}

# Define the start and end colors for the subtle change
start_color = np.array([1.0, 1.0, 1.0])  # White
# end_color = np.array([0.9, 0.9, 0.9])    # Light gray
end_color = np.array([0.75, 0.75, 0.75])    # Light gray

# Function to interpolate between two colors
def interpolate_color(start_color, end_color, factor):
    return start_color + (end_color - start_color) * factor

# **TASK SELECTION MENU**
task_choice = None
ball_change_type = None

while task_choice not in ['F', 'B']:
    instruction_text = visual.TextStim(win, text="Press 'F' for Fixation Hue Change Task\nPress 'B' for Ball Change Task", 
                                       color='white', pos=(0, 0), height=20)
    instruction_text.draw()
    win.flip()
    task_choice = event.waitKeys(keyList=['f', 'b'])[0].upper()  # Ensures only one key is read

if task_choice == 'B':
    while ball_change_type not in ['H', 'S']:
        instruction_text = visual.TextStim(win, text="Press 'H' for Ball Hue Change\nPress 'S' for Ball Speed Change", 
                                           color='white', pos=(0, 0), height=20)
        instruction_text.draw()
        win.flip()
        ball_change_type = event.waitKeys(keyList=['h', 's'])[0].upper()  # Ensures only one key is read

print(f"Selected task: {'Fixation Hue Change' if task_choice == 'F' else 'Ball Change'}")
if task_choice == 'B':
    print(f"Ball change type: {'Hue Change' if ball_change_type == 'H' else 'Speed Change'}")

for trial in trial_conditions:
    trial_clock = core.Clock()  # Create a clock for the trial
    
    if trial == "45":
        line_45.draw()
    elif trial == "135":
        line_135.draw()
    fixation.draw()

    win.flip()
    core.wait(2)  # Fixation + diagonal line display
    
    occluder.draw()
    fixation.draw()
    win.flip()
    core.wait(0.5)  # Occluder display
    
    # Ball movement setup
    edge = random.choice(list(start_positions.keys()))
    ball.pos = np.array(start_positions[edge])
    velocity = np.array(directions[edge])
    bounce = random.choice([True, False])  # 50% chance to bounce
    rand_bounce_direction = random.choice(["left", "right"])  # Random 90° bounce direction
    rand_speed_change = random.choice(["slower", "faster"])  # 50% chance to slow down or speed up
    hue_change_delay = random.uniform(0.2, .8)  # Random delay for hue change
    bounce_moment = None
    correct_response = None
    crossed_fixation = False
    trial_duration = (win_dims[0]//(800/6))
    print(f"Trial duration = {trial_duration}") if verbose else None
    # Apply hue change based on selected task
    hue_change = random.random() < .25 #0.2  # 20% probability
    feedback_text = ""

 
    # Store trial characteristics
    exp_data["trial"].append(len(exp_data["trial"]) + 1)
    exp_data["interactor"].append(trial)
    exp_data["bounce"].append(bounce) # Whether the ball will bounce (IMPORTANT TO HAVE IT HERE, as it will change after the bounce) it's like imperative
    exp_data["bounce_moment"].append(None)  # Placeholder for bounce moment
    exp_data["random_bounce_direction"].append(rand_bounce_direction)
    exp_data["target_onset"].append(None) # Cannot be done, until the moment of the change is known
    exp_data["speed_change"].append(rand_speed_change)
    exp_data["hue_change"].append(hue_change)
    exp_data["abs_congruent"].append(None)  # Placeholder for abstraction prediction congruency
    exp_data["sim_congruent"].append(None)  # Placeholder for simulated prediction congruency
    exp_data["response"].append(None)  # Placeholder for response
    exp_data["accuracy"].append(None)  # Placeholder for accuracy
    exp_data["rt"].append(None)  # Placeholder for reaction time
    exp_data["start_pos"].append(edge)
    exp_data["end_pos"].append(None)  # Placeholder for end position
    exp_data["abs_rftop"].append(None)  # Placeholder for absolute RF top
    exp_data["abs_rfright"].append(None)  # Placeholder for absolute RF right
    exp_data["abs_rfdown"].append(None)  # Placeholder for absolute RF down
    exp_data["abs_rfleft"].append(None)  # Placeholder for absolute RF left
    exp_data["sim_rftop"].append(None)  # Placeholder for simulated RF top
    exp_data["sim_rfright"].append(None)  # Placeholder for simulated RF right
    exp_data["sim_rfdown"].append(None)  # Placeholder for simulated RF down
    exp_data["sim_rfleft"].append(None)  # Placeholder for simulated RF left
    

    # **BALL MOVEMENT LOOP**
    while trial_clock.getTime() < trial_duration:  # Move until 6 seconds (scaled for window size)
        ball.pos += velocity  # Update ball position
        if trial_clock.getTime() % .5 < 0.02 and verbose:
            print(f"Ball direction: {velocity_to_direction(velocity)}")
        # Check for bounce
        if bounce and check_collision(ball.pos, trial, ball):
            if trial == "45":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 45, ball_speed)  # Reflect off 45°
            elif trial == "135":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 135, ball_speed)  # Reflect off 135°
            bounce = False  # Prevent double bouncing
            crossed_fixation = True
        
        # Draw everything each frame
        ball.draw()
        occluder.draw()
        fixation.draw()
        win.flip()
        core.wait(0.02)  # Smooth animation

        # Stop if the ball is near fixation and bounce is True
        if np.linalg.norm(ball.pos) <= 20:
            if bounce:
                if rand_bounce_direction == "left":
                    print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                    velocity = np.array([-velocity[1], -velocity[0]])  # Reflect off 45°
                elif rand_bounce_direction == "right":
                    print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                    velocity = np.array([velocity[1], velocity[0]])  # Reflect off 135°
            
            bounce = False
            crossed_fixation = True

        if bounce == False: # If the ball has bounced, or won't bounce at all (for continuation)
            if bounce_moment == None and crossed_fixation:
                # print(f"BOUNCE_MOMENT: {trial_clock.getTime()}")
                print(f"HUE_CHANGE_MOMENT: {trial_clock.getTime() + hue_change_delay}") if verbose else None
                bounce_moment = trial_clock.getTime()
                
                hue_change_moment = bounce_moment + hue_change_delay
                exp_data["bounce_moment"][-1] = bounce_moment
                exp_data["target_onset"][-1] = hue_change_moment
            if bounce_moment != None:
                if trial_clock.getTime() > hue_change_moment:
                    elapsed_time = trial_clock.getTime() - hue_change_moment
                    duration = 1.0  # Duration of the color change in seconds
                    factor = min(elapsed_time / duration, 1.0)  # Ensure factor is between 0 and 1
                    
                    if task_choice == 'F' and hue_change:
                        fixation.color = interpolate_color(start_color, end_color, factor)
                    elif task_choice == 'B' and hue_change:
                        if ball_change_type == 'H':
                            ball.fillColor = interpolate_color(start_color, end_color, factor)
                            ball.lineColor = interpolate_color(start_color, end_color, factor)
                        # Make ball velocity slowly decrease
                        elif ball_change_type == 'S':
                            if rand_speed_change == "slower" and sum(velocity) > 3:
                                velocity = tuple(v * (1 - factor / 15) for v in velocity)
                            elif rand_speed_change == "faster" and sum(velocity) < 8:
                                velocity = tuple(v * (1 + factor / 15) for v in velocity)
                        
        toetsen = event.getKeys(['space', 'left', 'right', 'up', 'down'])
        ball_direction = velocity_to_direction(velocity)
        
        exp_data["end_pos"][-1] = ball_direction # log end position
        
        if hue_change:
            if toetsen and bounce_moment != None and correct_response == None:
                toets_moment = trial_clock.getTime()
                if task_choice == 'F' and 'space' in toetsen:
                    if toets_moment < hue_change_moment:
                        feedback_text = f"Wrong, TOO EARLY"
                        print(f"Wrong, TOO EARLY")
                        correct_response = False
                    else:
                        feedback_text = f"Correct! detected hue change after {round(toets_moment - hue_change_moment, 3)}s"
                        print(f"Correct! detected hue change after {round(toets_moment - hue_change_moment, 3)}s")
                        correct_response = True
                if task_choice == 'B' and toetsen[0] in ['left', 'right', 'up', 'down']:
                    hue_or_speed = "hue" if ball_change_type == 'H' else "speed"
                    if toets_moment < hue_change_moment:
                        feedback_text = f"Wrong, TOO EARLY"
                        print(f"Wrong, TOO EARLY")
                        correct_response = False
                    elif ball_direction == toetsen[0]:
                        feedback_text = f"Correct! detected {hue_or_speed} change towards {toetsen[0]} after {round(toets_moment - hue_change_moment, 3)}s"
                        print(f"Correct! detected hue change towards {toetsen[0]} after {round(toets_moment - hue_change_moment, 3)}s")
                        correct_response = True
                    else:
                        feedback_text = f"Wrong, WRONG DIRECTION, should be a {hue_or_speed} change in {ball_direction} direction"
                        print(f"Wrong, WRONG DIRECTION, should be {ball_direction}")
                        correct_response = False
                        
            exp_data["accuracy"][-1] = correct_response
            exp_data["response"][-1] = toetsen[0] if toetsen else None
            exp_data["rt"][-1] = toets_moment - hue_change_moment if toetsen else None

        else:
            if toetsen != []:
                print(f"Wrong, there was no change")
                feedback_text = "Wrong, there was no change"

                correct_response = False

    feedback = visual.TextStim(win, text=feedback_text, 
                        color='white', pos=(0, 0), height=20)
    feedback.draw()
    win.flip()
    
    core.wait(2)
    
    # Reset ball and fixation color to original after each trial
    ball.fillColor = 'white'
    ball.lineColor = 'white'
    fixation.color = 'white'

    # **CHECK FOR 'R' TO SKIP TRIAL OR 'ESCAPE' TO QUIT**
    keys = event.getKeys()
    if 'escape' in keys:
        win.close()
        core.quit()
    elif 'r' in keys:
        continue  # Skip to the next trial        
    
    # Figure out how to fill in the RF specific values
    if trial == "none":
        exp_data["abs_congruent"][-1] = 1 if exp_data["bounce"] != None else 0
        exp_data["sim_congruent"][-1] = 1 if exp_data["bounce"] != None else 0

    # Get the predictions and sensory input for ball path per physical reasoning appraoch (hypothesis)
    for hypothesis in ["abs", "sim"]:
        pred_to_input = predict_ball_path(hypothesis=hypothesis, interactor=trial, start_pos=edge, end_pos=exp_data["end_pos"][-1], plot=False)
        for location in pred_to_input.keys():
            exp_data[f"{hypothesis}_rf{location}"] = pred_to_input[location]
            
    # TODO: ADD FUNCTION TO CHECK WHETHER THERE IS A TUPLE PAIR OF 2, IF SO, THERE IS NO VIOLATION, BECAUSE THIS MEANS PRED AND INPUT AGREE
    
    
    
win.close()

df = pd.DataFrame(exp_data)


# Save the DataFrame to a CSV file
subject_id = "subject_stront"
task_name = "task_01"
save_performance_data(subject_id, task_name, df)
