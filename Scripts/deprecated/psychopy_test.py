from psychopy import visual, core, event
import numpy as np
import random
import math

win_dims = [1000, 1000]
ball_speed = 5
verbose = False

# Create objects to store performance in




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
trial_conditions = ["45", "135", "none"] * 10
random.shuffle(trial_conditions)

# Possible starting positions and movement directions
start_positions = {
    "top": (0, win_dims[0]//2), "bottom": (0, -win_dims[0]//2), "left": (-win_dims[1]//2, 0), "right": (win_dims[1]//2, 0)
}
directions = {
    "top": (0, -ball_speed), "bottom": (0, ball_speed), "left": (ball_speed, 0), "right": (-ball_speed, 0)
}

def check_collision(ball_pos, line_angle):
    """Returns True if the ball's edge intersects the diagonal line."""
    x, y = ball_pos
    if line_angle == "45":  
        return abs(y - x) <= ball.radius  # Ball touches y = x
    elif line_angle == "135":
        return abs(y + x) <= ball.radius  # Ball touches y = -x
    return False  # No line

def collide(start_direction: str, line_angle: int):
    """Returns the new direction vector of the ball after a collision."""
    direction_angles = {
        "top": 270,
        "bottom": 90,
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

    # **BALL MOVEMENT LOOP**
    while trial_clock.getTime() < trial_duration:  # Move until 6 seconds (scaled for window size)
        ball.pos += velocity  # Update ball position
        if trial_clock.getTime() % .5 < 0.02 and verbose:
            print(f"Ball direction: {velocity_to_direction(velocity)}")
        # Check for bounce
        if bounce and check_collision(ball.pos, trial):
            if trial == "45":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 45)  # Reflect off 45°
            elif trial == "135":
                print(f"BOUNCED at {trial_clock.getTime()}") if verbose else None
                velocity = collide(edge, 135)  # Reflect off 135°
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

        if bounce == False:
            if bounce_moment == None and crossed_fixation:
                # print(f"BOUNCE_MOMENT: {trial_clock.getTime()}")
                print(f"HUE_CHANGE_MOMENT: {trial_clock.getTime() + hue_change_delay}") if verbose else None
                bounce_moment = trial_clock.getTime()
                
                hue_change_moment = bounce_moment + hue_change_delay
                
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

win.close()



