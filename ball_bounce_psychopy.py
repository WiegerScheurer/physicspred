from psychopy import visual, core, event
import random

# Create window
win = visual.Window([800, 800], monitor="testMonitor", units="deg")

# Create stimuli
fixation = visual.TextStim(win, text="+", height=0.5)
line45 = visual.Line(win, start=(-1, -1), end=(1, 1), lineWidth=5)
line135 = visual.Line(win, start=(-1, 1), end=(1, -1), lineWidth=5)
occluder = visual.Circle(win, radius=2, fillColor="grey")
ball = visual.Circle(win, radius=2.5, fillColor="white")

# Trial parameters
n_trials = 12
trial_duration = 2  # seconds
conditions = ['45', '135', 'none'] * 4  # 4 trials of each condition
random.shuffle(conditions)

for trial in range(n_trials):
    # Set up trial
    condition = conditions[trial]
    if condition == '45':
        line = line45
    elif condition == '135':
        line = line135
    else:
        line = None
    
    # Determine ball trajectory
    start_pos = random.choice([(-10, 0), (10, 0), (0, -7.5), (0, 7.5)])
    direction = [-1 if pos > 0 else 1 for pos in start_pos]
    ball.pos = start_pos
    
    # Determine if ball will continue or bounce
    will_bounce = random.choice([True, False])
    
    # Show fixation and line
    fixation.draw()
    if line:
        line.draw()
    win.flip()
    
    # Check for quit (escape key) during the trial
    for frame in range(int(trial_duration * 60)):  # Assuming 60 frames per second
        if 'escape' in event.getKeys():
            win.close()
            core.quit()
        core.wait(1/60.0)  # Wait for the next frame
    
    # Show occluder
    occluder.draw()
    fixation.draw()

# Close the window at the end of the experiment
win.close()
core.quit()