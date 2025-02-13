import pygame
import math
import sys
import random
import time
import matplotlib.pyplot as plt
import numpy as np

# Initialize pygame
pygame.init()

# Screen settings
screen_size = 1000  # 1200
screen = pygame.display.set_mode((screen_size, screen_size))

pygame.display.set_caption("Interactor Experiment")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 0)
GREY = (128, 128, 128)
GREEN = (34, 139, 34)

# Timing
CLOCK = pygame.time.Clock()
FPS = 60

# Fixation cross size
FIX_SIZE = 15
INTERACTOR_SIZE = 55
BALL_RADIUS = 20
BALL_SPEED = 15

# Global variables
interactor_type = None
interactor_angle = 0
interactor_loc = None
arc_angle = 0
ball_pos = None
ball_velocity = None
draw_simulation = False
occluder = False
occluder_excess = 45
ball_distance_from_screen = 350
add_interactor = True
stimloc = "center"
peri_factor = 6
locations_dict = {
    "center": (screen_size // 2, screen_size // 2),
    "top": (screen_size // 2, screen_size // 2 - screen_size // peri_factor),
    "bottom": (screen_size // 2, screen_size // 2 + screen_size // peri_factor),
    "left": (screen_size // 2 - screen_size // peri_factor, screen_size // 2),
    "right": (screen_size // 2 + screen_size // peri_factor, screen_size // 2),
}
loc_idx = 0
int_loc = locations_dict[list(locations_dict.keys())[loc_idx]]
trial_start = pygame.time.get_ticks()
ball_disappeared_time = None
surprisal_modes = [
    "pure_sim",
    "pure_abs",
    "random",
    "random: 1/3 realistic, 1/3 continuation, 1/3 stochastic violation",
    "60%\interactor: 1/3 realistic, 1/3 continuation, 1/3 stochastic violation; 40%\ no_interactor: 1/2 continuation, 1/2 stochastic violation",
    "left_only",
    # "80sim_20abs",
    # "20sim_80abs",
]
surprisal_idx = 0
surprise_dict = {
    "pure_sim": [1, 0, 0],
    "pure_abs": [0, 1, 0],
    "random": [1, 1, 1],
    "random: 1/3 realistic, 1/3 continuation, 1/3 stochastic violation": [1, 2, 0],
    "60%\interactor: 1/3 realistic, 1/3 continuation, 1/3 stochastic violation; 40%\ no_interactor: 1/2 continuation, 1/2 stochastic violation": [1, 2, 2],
    "left_only": [1, 1, 1],
    # "80sim_20abs": [4, 1],
    # "20sim_80abs": [1, 4],
}
phantom_bounce_angles = [ # Don't think i use this now
    270
]  # Think about better, because now it is doing weird stuff, and also
# causes the ball to become parallel, which is then another continuation, so that messes up the ratio.

unrealistic_types = [
    # "stochastic", # because not yet needed, only continuation as violation
    "continuation",
]  # Stochastic is a random omission, continuation is deterministic if you linearly extrapolate
# unrealistic_types = ["stochastic", "stochastic"]
stochastic_types = ["omission", "phantom_bounce"]
# stochastic_types = ["phantom_bounce", "phantom_bounce"]


def surprise_trial(verbose: bool = True):
    global surprisal_idx, this_mode
    this_mode = surprisal_modes[surprisal_idx]
    ratio = surprise_dict[this_mode]

    ball_behaviour = random.choice(
        ["realistic"] * ratio[0] + ["unrealistic"] * ratio[1] + ["no_interactor"] * ratio[2] # change these string names, now confusing
    )

    if verbose:
        print(
            f"Surprisal mode: {this_mode}, this trial: {ball_behaviour}"
        )
    return ball_behaviour


# Helper functions
def draw_fixation_cross():
    pygame.draw.line(
        screen,
        BLACK,
        (screen_size // 2 - FIX_SIZE, screen_size // 2),
        (screen_size // 2 + FIX_SIZE, screen_size // 2),
        3,
    )
    pygame.draw.line(
        screen,
        BLACK,
        (screen_size // 2, screen_size // 2 - FIX_SIZE),
        (screen_size // 2, screen_size // 2 + FIX_SIZE),
        3,
    )


def draw_interactor():
    global interactor_type, interactor_angle, interactor_loc, int_loc
    diag_line_length = INTERACTOR_SIZE + 25
    
    if interactor_type == "line":
        rad_angle = math.radians(interactor_angle)
        if interactor_angle in [0, 90, 180, 270]:
            if interactor_angle == 0:
                x1, y1 = (
                    int_loc[0] - INTERACTOR_SIZE,
                    int_loc[1] + INTERACTOR_SIZE,
                )
                x2, y2 = (
                    int_loc[0] + INTERACTOR_SIZE,
                    int_loc[1] + INTERACTOR_SIZE,
                )
            elif interactor_angle == 90:
                x1, y1 = (
                    int_loc[0] - INTERACTOR_SIZE,
                    int_loc[1] - INTERACTOR_SIZE,
                )
                x2, y2 = (
                    int_loc[0] - INTERACTOR_SIZE,
                    int_loc[1] + INTERACTOR_SIZE,
                )
            elif interactor_angle == 180:
                x1, y1 = (
                    int_loc[0] + INTERACTOR_SIZE,
                    int_loc[1] - INTERACTOR_SIZE,
                )
                x2, y2 = (
                    int_loc[0] - INTERACTOR_SIZE,
                    int_loc[1] - INTERACTOR_SIZE,
                )
            elif interactor_angle == 270:
                x1, y1 = (
                    int_loc[0] + INTERACTOR_SIZE,
                    int_loc[1] + INTERACTOR_SIZE,
                )
                x2, y2 = (
                    int_loc[0] + INTERACTOR_SIZE,
                    int_loc[1] - INTERACTOR_SIZE,
                )
        else:
            x1 = int_loc[0] - int(diag_line_length * math.cos(rad_angle))
            y1 = int_loc[1] - int(diag_line_length * math.sin(rad_angle))
            x2 = int_loc[0] + int(diag_line_length * math.cos(rad_angle))
            y2 = int_loc[1] + int(diag_line_length * math.sin(rad_angle))

        interactor_loc = (x1, x2, y1, y2)
        pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 20)
            
    elif interactor_type == "curve":
        curve_factor = 3
        arc_start = math.pi / 2 * arc_angle
        arc_end = arc_start + math.pi / 2

        x_shift = -curve_factor if arc_angle == 0 or arc_angle == 3 else 0
        y_shift = 0 if arc_angle == 0 or arc_angle == 1 else -curve_factor

        arc_dif = arc_end - arc_start
        # Draw the arc in a lot of steps so that it is smooth
        for i in range(1, 30, 1):
            pygame.draw.arc(
                screen,
                RED,
                (
                    int_loc[0] + INTERACTOR_SIZE * x_shift,
                    int_loc[1] + INTERACTOR_SIZE * y_shift,
                    curve_factor * INTERACTOR_SIZE,
                    curve_factor * INTERACTOR_SIZE,
                ),
                arc_start + (i - 1) / 30 * arc_dif,
                arc_end,
                12,
            )

    elif interactor_type == "hole":
        pygame.draw.circle(
            screen, RED, (screen_size // 2, screen_size // 2), INTERACTOR_SIZE * 0.5
        )


def draw_occluder():
    global int_loc
    pygame.draw.circle(
        screen,
        GREY,
        int_loc,
        INTERACTOR_SIZE + occluder_excess,
    )


def draw_ball(visibility: bool = True):
    pygame.draw.circle(
        screen,
        BLACK,
        (int(ball_pos[0]), int(ball_pos[1])),
        BALL_RADIUS if visibility else 0,
    )


# The original function in which the ball comes from one of the four middle points of the screen sides
# def reset_trial():
#     global interactor_type, interactor_angle, ball_pos, ball_velocity, occluder, trial_start, ball_disappeared_time, arc_angle, direction, ball_behaviour
#     ball_behaviour = surprise_trial()
#     option_list = ["hole"] * 1 + ["line"] * 24 + ["curve"] * 4
#     interactor_type = random.choice(option_list)
#     interactor_angle = random.choice(list(range(0, 360, 15)))
#     arc_angle = random.randint(0, 3)
#     direction = random.choice(["left", "right", "top", "bottom"])
#     ball_distance_from_screen = 30
#     if direction == "left":
#         ball_pos = [-ball_distance_from_screen, screen_size // 2]
#         ball_velocity = [BALL_SPEED, 0]
#     elif direction == "right":
#         ball_pos = [screen_size + ball_distance_from_screen, screen_size // 2]
#         ball_velocity = [-BALL_SPEED, 0]
#     elif direction == "top":
#         ball_pos = [screen_size // 2, -ball_distance_from_screen]
#         ball_velocity = [0, BALL_SPEED]
#     elif direction == "bottom":
#         ball_pos = [screen_size // 2, screen_size + ball_distance_from_screen]
#         ball_velocity = [0, -BALL_SPEED]
#     occluder = False
#     trial_start = pygame.time.get_ticks()
#     ball_disappeared_time = None
#     ball_visible = True
#     return ball_visible


# Make ball spawn from random polar direction, or rather a random point on a margin outline from the square screen area
def spawn_ball_around_square(
    screendim: int,
    screen_margin: int,
    spawn_margin,
    plot: bool = False,
    verbose: bool = False,
    avoid_angles: list = [45, 135],
    avoidance_margin: int = 35,
    bidirectional: bool = True, # Whether or not to avoid angles from both sides
):
    global int_loc
    plot_dim = screendim + 2 * screen_margin
    showcase = np.zeros((plot_dim, plot_dim))

    # center = ((plot_dim) / 2, (plot_dim) / 2)
    center = [int(int_loc[0] + screen_margin), int(int_loc[1] + screen_margin)]

    desirable_angle = False
    triangle_factor = 1.5
    while not desirable_angle:
        # Pythagoras theorie
        alpha = random.randint(0, 360)
        # s = screendim / 2 + spawn_margin
        s = int(np.max(center) * triangle_factor)

        o = int(center[0] - (np.sin(alpha) * s) // 1 * triangle_factor) # I switched the indices 0 and 1
        a = int(center[1] + (np.cos(alpha) * s) // 1 * triangle_factor)

        ball_angle = math.degrees(
            math.atan2(center[0] - o, center[1] - a)
        )  # Compute angle of incoming balleke
        ball_angle = ball_angle + 360 if ball_angle < 0 else ball_angle
        
        if bidirectional:
            bidirect_avoid_angles = avoid_angles + [angle + 180 for angle in avoid_angles]
        else:
            bidirect_avoid_angles = avoid_angles
            
        for angle in bidirect_avoid_angles:
            if ball_angle - avoidance_margin < angle < ball_angle + avoidance_margin:
                desirable_angle = False
                print(
                    f"Random ball angle {round(ball_angle, 2)} too parallel to interactor angle: {angle}, trying again"
                )
                break
            else:
                desirable_angle = True
                
    if verbose:
        print(f"schuine zijde: {s}, overstaande zijde: {o}, aanliggende zijde: {a}")
        print(f"Incoming ball angle: {round(ball_angle, 2)}")
        
    showcase[
        screen_margin : screendim + screen_margin,
        screen_margin : screendim + screen_margin,
    ] = 1

    showcase[o - 3 : o + 3, a // 1 - 3 : a // 1 + 3] = 10
    if plot:
        plt.imshow(showcase, cmap="RdGy")
    return o, a, alpha

def get_possible_angles(avoid_angles, avoidance_margins):
    """
    Returns a set of possible angles by removing the angles within the avoidance margin 
    of the given avoid angles.
    
    Parameters:
    avoid_angles (list): A list of angles to avoid.
    avoidance_margin (int): The margin within which angles should be avoided.
    
    Returns:
    set: A set of possible angles.
    """
    all_angles = set(range(0, 360))
    remove_angles = set()
    
    for margin_no, angle in enumerate(avoid_angles):
        angles_to_remove = range(int(angle) - avoidance_margins[margin_no], int(angle) + avoidance_margins[margin_no] + 1)
        # correct for angles that go over the 360 degrees
        remove_angles.update([angle % 360 for angle in angles_to_remove])
            
    return all_angles - remove_angles

def get_stim_loc(loc_idx:int):
    global int_loc, locations_dict
    # locs = ["center", "top", "bottom", "left", "right", "random"]
    locs = list(locations_dict.keys()) + ["random"]
    stimloc = locs[loc_idx]
    if stimloc == "random":
        current_loc_idx = random.randint(0, len(locations_dict) - 1)
    else:
        current_loc_idx = loc_idx
    int_loc = locations_dict[list(locations_dict.keys())[current_loc_idx]] # Check if this works 
    print(f"Stimulus location: {stimloc}")
    return int_loc

def phantom_bounce(screendim: int,
                   avoid_angles: list,
                   avoidance_margins: list,
                   BALL_SPEED:int,
                   verbose:bool=False):
    
    angle = random.choice(list(get_possible_angles(avoid_angles, avoidance_margins)))
    real_velocity = angle_to_velocity(angle, BALL_SPEED)        

    print(f"Phantom bounce velocity: {real_velocity}") if verbose else None
    return real_velocity
    
def reset_trial(verbose: bool = True):
    # global interactor_type, interactor_angle, ball_pos, ball_velocity, occluder, trial_start, ball_disappeared_time, arc_angle, direction, ball_behaviour, ball_distance_from_screen
    global  interactor_type, interactor_angle, ball_pos, ball_velocity
    global occluder, trial_start, ball_disappeared_time, arc_angle
    global ball_behaviour, ball_distance_from_screen, unrealistic_type
    global stochastic_type, violation_printed, phantom_bounce_angle, bounced_yet
    global ball_angle, draw_simulation, add_interactor, interactor_printed, this_mode, loc_idx, int_loc
    unrealistic_type = random.choice(unrealistic_types)
    stochastic_type = random.choice(stochastic_types)
    phantom_bounce_angle = random.choice(phantom_bounce_angles)
    violation_printed = False
    bounced_yet = False
    interactor_printed = False

    int_loc = get_stim_loc(loc_idx)
    ball_behaviour = surprise_trial()
    
    target_coords = int_loc
    # option_list = ["hole"] * 1 + ["line"] * 24 + ["curve"] * 4
    option_list = ["line"] * 24
    interactor_type = random.choice(option_list)
    # interactor_angle = random.choice(list(range(0, 360, 15)))
    interactor_angle = random.choice([45, 135])
    print(f"Interactor angle: {interactor_angle}")
    arc_angle = random.randint(0, 3)

    if this_mode == "left_only":
        ball_pos = [-ball_distance_from_screen, int_loc[1]]
    else:
        ball_y, ball_x, _ = spawn_ball_around_square(
            screendim=screen_size,
            screen_margin=0,
            spawn_margin=ball_distance_from_screen,
            plot=False,
            verbose=False,
            avoid_angles=[interactor_angle],
            avoidance_margin=35,
        )

        ball_pos = [ball_x, ball_y]
        
    dx_raw = target_coords[0] - ball_pos[0]
    dy_raw = target_coords[1] - ball_pos[1]

    ball_angle = math.degrees(math.atan2(dy_raw, dx_raw))  # Compute angle of incoming
    ball_angle = ball_angle + 360 if ball_angle < 0 else ball_angle

    dx = dx_raw / math.sqrt(dx_raw**2 + dy_raw**2) * BALL_SPEED
    dy = dy_raw / math.sqrt(dx_raw**2 + dy_raw**2) * BALL_SPEED

    ball_velocity = [dx, dy]

    occluder = False
    trial_start = pygame.time.get_ticks()
    ball_disappeared_time = None
    ball_visible = True
    return ball_visible


running = True
ball_visible = reset_trial()

def diag_bounce(
    angle,
    ball_pos,
    ball_velocity,
    screen_size,
    INTERACTOR_SIZE,
    line: bool,
    verbose: bool = False,
    int_loc: list = None,
):
    rad_angle = math.radians(angle)
    line_dx = INTERACTOR_SIZE * math.cos(rad_angle)
    line_dy = INTERACTOR_SIZE * math.sin(rad_angle)

    if line:
        x1, x2, y1, y2 = interactor_loc
    else:
        x1 = int_loc[0] - line_dx
        y1 = int_loc[1] - line_dy
        x2 = int_loc[0] + line_dx
        y2 = int_loc[1] + line_dy

    # Calculate the normal vector of the line
    normal_angle = rad_angle + math.pi / 2
    normal = [math.cos(normal_angle), math.sin(normal_angle)]

    # Define the boundaries correctly
    x_min, x_max = min(x1, x2) -1, max(x1, x2) +1
    y_min, y_max = min(y1, y2) -1, max(y1, y2) +1

    # Check if the ball overlaps with the region
    if (
        x_min <= ball_pos[0] - BALL_RADIUS <= x_max
        and x_min <= ball_pos[0] + BALL_RADIUS <= x_max
        and y_min <= ball_pos[1] - BALL_RADIUS <= y_max
        and y_min <= ball_pos[1] + BALL_RADIUS <= y_max
    ):
        # Calculate the dot product for reflection
        dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]

        # Reflect the velocity along the normal
        ball_velocity[0] -= 2 * dot_product * normal[0]
        ball_velocity[1] -= 2 * dot_product * normal[1]

    return ball_velocity


def bounce_back(
    angle, ball_velocity, ball_pos, screen_size, INTERACTOR_SIZE, line: bool
):
    rad_angle = math.radians(angle)
    line_dx = INTERACTOR_SIZE * math.cos(rad_angle)
    line_dy = INTERACTOR_SIZE * math.sin(rad_angle)

    if line:
        x1, x2, y1, y2 = interactor_loc
    else:
        x1 = screen_size // 2 - line_dx
        y1 = screen_size // 2 - line_dy
        x2 = screen_size // 2 + line_dx
        y2 = screen_size // 2 + line_dy

    # Calculate the line's direction vector
    line_direction = [line_dx, line_dy]

    # Normalize the line direction vector
    line_length = math.sqrt(line_dx**2 + line_dy**2)
    line_direction = [line_dx / line_length, line_dy / line_length]

    # Normalize the ball velocity vector
    velocity_length = math.sqrt(ball_velocity[0] ** 2 + ball_velocity[1] ** 2)
    normalized_velocity = [
        ball_velocity[0] / velocity_length,
        ball_velocity[1] / velocity_length,
    ]

    # Calculate the dot product
    dot_product = (
        normalized_velocity[0] * line_direction[0]
        + normalized_velocity[1] * line_direction[1]
    )

    # Check if the ball is moving parallel to the line
    if abs(dot_product) != 1:
        # print if it is parallel or not
        print("Not parallel")

        # Calculate the distance from the ball to the line segment
        px, py = ball_pos
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            # The line segment is a point
            dist = math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        else:
            t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
            if t < 0:
                nearest_x, nearest_y = x1, y1
            elif t > 1:
                nearest_x, nearest_y = x2, y2
            else:
                nearest_x = x1 + t * dx
                nearest_y = y1 + t * dy
            dist = math.sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)

        # Check if the ball is close enough to the line to bounce
        if dist <= INTERACTOR_SIZE:
            print("Bounce")
            ball_velocity = [-v for v in ball_velocity]

    return ball_velocity

def velocity_to_angle(velocity):
    angle = math.degrees(math.atan2(velocity[1], velocity[0]))
    return angle + 360 if angle < 0 else angle

def angle_to_velocity(angle, speed):
    rad_angle = math.radians(angle)
    dx = math.cos(rad_angle) * speed
    dy = math.sin(rad_angle) * speed
    return [dx, dy]

def get_hypothetical_velocity(ball_angle):
    global int_loc
    original_velocity = angle_to_velocity(ball_angle, BALL_SPEED)
    hypothetical_velocity = diag_bounce(
        interactor_angle,
        int_loc,
        original_velocity,
        screen_size,
        INTERACTOR_SIZE,
        True,
    )
    return hypothetical_velocity

def draw_sim_line(ball_angle, draw_simulation:bool):
    global int_loc
    if draw_simulation:
        hypothetical_velocity = get_hypothetical_velocity(ball_angle)
        pygame.draw.line(screen, GREEN, int_loc, (int_loc[0]+hypothetical_velocity[0]*200, int_loc[1]+hypothetical_velocity[1]*200), 10)
    else:
        pass
    
while running:
    screen.fill(WHITE)
    # draw_table()
    draw_fixation_cross()
    current_time = pygame.time.get_ticks()

    if current_time - trial_start < 2000:
        draw_interactor() if not ball_behaviour == "no_interactor" else None
        draw_fixation_cross()
    else:
        occluder = True
        draw_occluder()
        draw_interactor() if not ball_behaviour == "no_interactor" else None

        if (
            current_time - trial_start > 3000
        ):  # Add a delay of 2 seconds after the occluder appears
            ball_pos[0] += ball_velocity[0]
            ball_pos[1] += ball_velocity[1]
            
            draw_sim_line(ball_angle, draw_simulation)
            
        draw_ball(visibility=ball_visible)
        
        draw_occluder()
        draw_fixation_cross()
        

        if ball_behaviour == "realistic":

            # Hole interaction
            if (
                interactor_type == "hole"
                and math.dist(ball_pos, int_loc)
                < INTERACTOR_SIZE
            ):
                ball_visible = False

            # Line interaction
            if interactor_type == "line":
                if interactor_angle % 90 != 0:
                    ball_velocity = diag_bounce(
                        interactor_angle,
                        ball_pos,
                        ball_velocity,
                        screen_size,
                        INTERACTOR_SIZE,
                        True,
                        int_loc
                    )
                else:
                    ball_velocity = diag_bounce(
                        interactor_angle,
                        ball_pos,
                        ball_velocity,
                        screen_size,
                        INTERACTOR_SIZE,
                        True,
                        int_loc
                    )
                bounced_yet = True

            if not violation_printed:
                print("\n")
                violation_printed = True
                
        else:
            if ball_behaviour == "no_interactor":
                add_interactor = False
                if not interactor_printed:
                    print("* * * INTERACTOR ABSENT * * *\n")
                    interactor_printed = True
            else:
                if not interactor_printed:
                    print("* * * INTERACTOR PRESENT * * *\n")
                    interactor_printed = True
            if (
                unrealistic_type == "stochastic"
            ):  # To make 50% of the unrealistic trials an omission
                # Hole interaction
                if (
                    math.dist(ball_pos, [screen_size // 2, screen_size // 2])
                    < INTERACTOR_SIZE and bounced_yet == False
                ):
                
                    if stochastic_type == "omission":
                        if not violation_printed:
                            print("* * * OMSSION * * *\n")
                            violation_printed = True
                        ball_visible = False
                        bounced_yet = True
                    elif stochastic_type == "phantom_bounce":
                        bounce_factor = 1 if interactor_angle == 135 else -1
                        phantom_interactor_angle = (
                            interactor_angle + bounce_factor * phantom_bounce_angle
                        )
                        
                        if not violation_printed:
                            print("* * * PHANTOM BOUNCE * * *")
                            print(f"Phantom bounce angle: {phantom_interactor_angle}\n")
                            violation_printed = True
                        hypothetical_ball_velocity = diag_bounce(
                            interactor_angle,
                            ball_pos,
                            ball_velocity,
                            screen_size,
                            INTERACTOR_SIZE,
                            True,
                            int_loc
                        )
                        
                        ball_velocity = phantom_bounce(screendim=screen_size,
                                    avoid_angles=[velocity_to_angle(get_hypothetical_velocity(ball_angle)), velocity_to_angle(ball_velocity)],

                                    avoidance_margins=[100, 45],
                                    BALL_SPEED=BALL_SPEED,
                                    verbose=True)
                        bounced_yet = True
                        
            else:
                # ball_velocity = ball_velocity  # not necessary, but for clarity
                if not violation_printed:
                    print("* * * CONTINUATION * * *\n")
                    violation_printed = True

    if current_time - trial_start > 7000:
        ball_visible = reset_trial()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                ball_visible = reset_trial()
        if event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_v
            ):  # Set on violation of the simulation, a toggle basically
                ball_behaviour = (
                    "unrealistic" if ball_behaviour == "realistic" else "realistic"
                )
                print(f"Violate a different type of expectation, now: {ball_behaviour}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # surprise switch
                surprisal_idx += 1 if surprisal_idx < len(surprisal_modes) - 1 else -5
                print(f"Mode switched to: {surprisal_modes[surprisal_idx]}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:  # Make ball faster
                BALL_SPEED += 5 if BALL_SPEED < 100 else -90
                print(f"Changing speed to {BALL_SPEED}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:  # Make ball bigger
                BALL_RADIUS += 5 if BALL_RADIUS < 100 else -90
                print(f"Changing ball radius to {BALL_RADIUS}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:  # Make occluder bigger
                occluder_excess += 10 if occluder_excess < 100 else -90
                print(f"Changing occluder excess to {occluder_excess}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:  # Hide occluder 
                occluder_excess = -INTERACTOR_SIZE if occluder_excess > 0 else 30
                # occluder_excess += 10 if occluder_excess < 100 else -90
                print(f"Hiding/showing occluder")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                draw_simulation = not draw_simulation
                print(f"Draw simulation: {draw_simulation}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                locs = ["center", "top", "bottom", "left", "right", "random"]
                loc_idx += 1 if loc_idx < len(locs) - 1 else -6
                get_stim_loc(loc_idx)
    pygame.display.flip()
    CLOCK.tick(FPS)

pygame.quit()
