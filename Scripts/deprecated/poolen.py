import pygame
import math
import sys
import random
import time
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pool Table Simulation")

# Colors
GREEN = (34, 139, 34)
DARKGREY = (50, 50, 50) # Dark grey
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)

# Here I create an array to determine which locations are allowed for the ball to spawn in
bound_margin = 150 # used to be 75
central_margin = 150
allowed_region = np.zeros((HEIGHT, WIDTH))
allowed_region[bound_margin:HEIGHT-bound_margin, bound_margin:WIDTH-bound_margin] = 1
allowed_region[(HEIGHT//2-central_margin):(HEIGHT//2+ central_margin), (WIDTH//2 - central_margin):(WIDTH//2 + central_margin)] = 0
random_x, random_y = WIDTH // 2, HEIGHT//1.5 # initial location of the white ball

def wball_coords(random_y=0, random_x=0, verbose:bool=True):
    
    while allowed_region[random_y, random_x] == 0:
        random_x = random.randint(bound_margin, WIDTH - bound_margin)
        random_y = random.randint(bound_margin, HEIGHT - bound_margin)
        
    if verbose:
        print(f"Wball coords: {random_x, random_y}")
    return (random_x, random_y)

def get_aim(fluct_fact:int=10, rand_seed=0):
    random.seed(rand_seed)
    flucts = [-3, -2.5, -2, 2, 2.5, 3]
    x_fluct = random.choice(flucts)
    y_fluct = random.choice(flucts)
    middle_pos = (white_ball_x - (red_ball_x - white_ball_x), white_ball_y - (red_ball_y - white_ball_y)) # if stick_hit is true
    
    return (middle_pos[0] + (fluct_fact * x_fluct), middle_pos[1] + (fluct_fact * y_fluct))

# Ball properties
ball_radius = 35
red_ball_x, red_ball_y = WIDTH // 2, HEIGHT // 2
# white_ball_x, white_ball_y = WIDTH // random.randint(1,4), HEIGHT // random.randint(1,2)
white_ball_x, white_ball_y = wball_coords()

red_ball_velocity = [0, 0]  # [x_velocity, y_velocity]
white_ball_velocity = [0, 0]    # [x_velocity, y_velocity]
friction = 0.985  # Friction coefficient (was .98, which is probably more realistic)
natural_physics = True

# Restart button params
reinit_button_font = pygame.font.SysFont(None, 25)
reinit_button_text = reinit_button_font.render('Restart', True, BLACK)
reinit_button_rect = pygame.Rect(WIDTH - 150, HEIGHT - 50, 80, 25)

switch_button_font = pygame.font.SysFont(None, 25)
switch_button_text = switch_button_font.render('Natural physics:', True, BLACK)
switch_button_rect = pygame.Rect(WIDTH - 350, HEIGHT - 50, 155, 25)

# Game clock
clock = pygame.time.Clock()

# Functions
# def draw_table(show_aim:bool=False, fluct_fact:int=10):
#     screen.fill(DARKGREY)
#     pygame.draw.rect(screen, BLACK, (25, 25, WIDTH - 50, HEIGHT - 50), 25)  # Table boundary
    
#     if show_aim:
#         # end_pos = (white_ball_x - (red_ball_x - white_ball_x), white_ball_y - (red_ball_y - white_ball_y)) # if stick_hit is true
        
        
#         draw_arrow((white_ball_x, white_ball_y), get_aim(fluct_fact=fluct_fact))
        
# Set the random seed
random.seed()

sides = ['top', 'bottom', 'left', 'right']
# Determine which boundary side will turn green
green_side = random.choice(sides)

def draw_table(show_aim: bool = False, fluct_fact: int = 10):
    screen.fill(DARKGREY)
    
    # Draw the table boundary
    pygame.draw.rect(screen, BLACK, (25, 25, WIDTH - 50, HEIGHT - 50), 25)
    
    # Draw the green boundary side with smaller width
    boundary_thickness = 5  # Adjust this value to make the sides smaller

    if green_side == 'top':
        pygame.draw.rect(screen, GREEN, (25, 45, WIDTH - 50, boundary_thickness))
    elif green_side == 'bottom':
        pygame.draw.rect(screen, GREEN, (25, HEIGHT - 55, WIDTH - 50, boundary_thickness))
    elif green_side == 'left':
        pygame.draw.rect(screen, GREEN, (45, 25, boundary_thickness, HEIGHT - 50))
    elif green_side == 'right':
        pygame.draw.rect(screen, GREEN, (WIDTH - 55, 25, boundary_thickness, HEIGHT - 50))
    if show_aim:
        # Calculate the aim position
        aim_pos = get_aim(fluct_fact=fluct_fact)
        draw_arrow((white_ball_x, white_ball_y), aim_pos)        
        
def draw_ball(x, y, color):
    pygame.draw.circle(screen, color, (int(x), int(y)), ball_radius)

def draw_fixation_cross(screen, color, center, size):
    x, y = center
    half_size = size // 2
    pygame.draw.line(screen, color, (x - half_size, y), (x + half_size, y), 2)
    pygame.draw.line(screen, color, (x, y - half_size), (x, y + half_size), 2)

# Adaptation for dotted aim arrow
def draw_arrow(start_pos, end_pos, aim_line:bool=True, shot:bool=False):
    if shot:
        start_pos = (white_ball_x, white_ball_y)
        end_pos = (red_ball_x, red_ball_y)
    else:
        # Draw the original continuous line and circle
        pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
        pygame.draw.circle(screen, WHITE, end_pos, 5)
        
        if aim_line:
            # Calculate the direction vector of the original line, and reverse it
            dx = -(end_pos[0] - start_pos[0])
            dy = -(end_pos[1] - start_pos[1])
            
            # Normalize the direction vector
            length = math.sqrt(dx**2 + dy**2)
            dx /= length
            dy /= length
            
            # Draw the dotted line
            dot_length = 10
            gap_length = 5
            current_pos = start_pos
            
            while 0 <= current_pos[0] <= WIDTH and 0 <= current_pos[1] <= HEIGHT:
                start_dot = current_pos
                end_dot = (start_dot[0] + dot_length * dx, start_dot[1] + dot_length * dy)
                pygame.draw.line(screen, WHITE, start_dot, end_dot, 3)
                current_pos = (end_dot[0] + gap_length * dx, end_dot[1] + gap_length * dy)

def move_ball(natural_bounce:bool=True, hit_angle:float=0):
    global red_ball_x, red_ball_y, white_ball_x, white_ball_y, red_ball_velocity, white_ball_velocity, dragging, counter, shot_yet
    # Update ball positions
    red_ball_x += red_ball_velocity[0]
    red_ball_y += red_ball_velocity[1]
    white_ball_x += white_ball_velocity[0]
    white_ball_y += white_ball_velocity[1]
    
    # Apply friction
    red_ball_velocity[0] *= friction
    red_ball_velocity[1] *= friction
    white_ball_velocity[0] *= friction
    white_ball_velocity[1] *= friction

    # Stop the ball if it moves too slowly
    if abs(red_ball_velocity[0]) < 0.1:
        red_ball_velocity[0] = 0
    if abs(red_ball_velocity[1]) < 0.1:
        red_ball_velocity[1] = 0
    if abs(white_ball_velocity[0]) < 0.1:
        white_ball_velocity[0] = 0
    if abs(white_ball_velocity[1]) < 0.1:
        white_ball_velocity[1] = 0

    # Collision with walls
    if red_ball_x - ball_radius <= 50 or red_ball_x + ball_radius >= WIDTH - 50:
        red_ball_velocity[0] = -red_ball_velocity[0]
    if red_ball_y - ball_radius <= 50 or red_ball_y + ball_radius >= HEIGHT - 50:
        red_ball_velocity[1] = -red_ball_velocity[1]
    if white_ball_x - ball_radius <= 50 or white_ball_x + ball_radius >= WIDTH - 50:
        white_ball_velocity[0] = -white_ball_velocity[0]
    if white_ball_y - ball_radius <= 50 or white_ball_y + ball_radius >= HEIGHT - 50:
        white_ball_velocity[1] = -white_ball_velocity[1]

    # Collision between balls
    dx = white_ball_x - red_ball_x
    dy = white_ball_y - red_ball_y
    distance = math.sqrt(dx**2 + dy**2)
        
    if distance < 2 * ball_radius:
        print("BOUNCE")
        # dragging = False

        if natural_bounce:
            # Calculate angle of collision
            angle = math.atan2(dy, dx)
            sin_angle = math.sin(angle)
            cos_angle = math.cos(angle)
            distort_by = 0
            natural_angle = angle
            # dragging = False

        else:
            # Randomly generate an angle of collision to create unnatural bounce collision
            natural_angle = math.atan2(dy, dx)
                
            if natural_angle + hit_angle < 0:
                distort_by = .8 #.75
            else:
                distort_by = -.8 #-.75
                
            angle = natural_angle + distort_by # I need to find a more visually realistic way to do this
            sin_angle = math.sin(angle) #+ random.uniform(-0.5, 0.5)
            cos_angle = math.cos(angle) #+ random.uniform(-0.5, 0.5)

        dragging = False    
        
        print(f"Natural angle: {natural_angle}, angle distortion: {distort_by}, sin: {sin_angle}, cos: {cos_angle}")
            
        # Rotate velocities to align with collision angle
        red_ball_velocity_rot = [red_ball_velocity[0] * cos_angle + red_ball_velocity[1] * sin_angle,
                                -red_ball_velocity[0] * sin_angle + red_ball_velocity[1] * cos_angle]
        
        white_ball_velocity_rot = [white_ball_velocity[0] * cos_angle + white_ball_velocity[1] * sin_angle,
                                -white_ball_velocity[0] * sin_angle + white_ball_velocity[1] * cos_angle]    
        
        # Swap the x velocities (since they are now aligned with the collision angle)
        red_ball_velocity_rot[0], white_ball_velocity_rot[0] = white_ball_velocity_rot[0], red_ball_velocity_rot[0]

        # Rotate velocities back to original coordinate system
        red_ball_velocity = [red_ball_velocity_rot[0] * cos_angle - red_ball_velocity_rot[1] * sin_angle,
                               red_ball_velocity_rot[0] * sin_angle + red_ball_velocity_rot[1] * cos_angle]
        
        white_ball_velocity = [white_ball_velocity_rot[0] * cos_angle - white_ball_velocity_rot[1] * sin_angle,
                             white_ball_velocity_rot[0] * sin_angle + white_ball_velocity_rot[1] * cos_angle]

        # Separate the balls to prevent overlap
        overlap = 2 * ball_radius - distance
        red_ball_x -= overlap * cos_angle / 2
        red_ball_y -= overlap * sin_angle / 2
        white_ball_x += overlap * cos_angle / 2
        white_ball_y += overlap * sin_angle / 2
        
def hit_ball(angle, power, stick_hit:bool=True):
    global white_ball_velocity
    if stick_hit:
        white_ball_velocity[0] = -power * math.cos(angle)
        white_ball_velocity[1] = power * math.sin(angle)
    else:
        white_ball_velocity[0] = power * math.cos(angle)
        white_ball_velocity[1] = -power * math.sin(angle)

def reinit_game(show_aim:bool=False):
    global red_ball_x, red_ball_y, white_ball_x, white_ball_y, red_ball_velocity, white_ball_velocity, auto_toggle, green_side
    
    green_side = random.choice(sides)
    
    auto_toggle = False    
    # Reinitialize the game state
    red_ball_x, red_ball_y = WIDTH // 2, HEIGHT // 2
    white_ball_x, white_ball_y = wball_coords()
    red_ball_velocity = [0, 0]
    white_ball_velocity = [0, 0]
    
    draw_table(show_aim=show_aim)



# Main loop
dragging = False
start_pos = (0, 0)
this_hit_angle = None
running = True
auto_toggle = False
auto_draw_delay = 0
clock = pygame.time.Clock()
counter = 0
toggle_a = False
this_show_aim = False
show_aim = False
fluct_fact = 10
rand_seed = random.randint(0,1000)
print(f"Random seed: {rand_seed}")

while running:
    
    if toggle_a:
        draw_table(show_aim=True)
        
    else:
        draw_table()
    if dragging:
        current_pos = pygame.mouse.get_pos() if not auto_toggle else end_pos
        if toggle_a:
            draw_arrow((white_ball_x, white_ball_y), get_aim(fluct_fact=fluct_fact, rand_seed=10), shot=True)
        else:
            draw_arrow((white_ball_x, white_ball_y), end_pos=pygame.mouse.get_pos())

    draw_ball(red_ball_x, red_ball_y, RED)
    draw_ball(white_ball_x, white_ball_y, WHITE)

    pygame.draw.rect(screen, WHITE, reinit_button_rect)
    screen.blit(reinit_button_text, (reinit_button_rect.x + 10, reinit_button_rect.y + 5))
    
    pygame.draw.rect(screen, WHITE, switch_button_rect)
    screen.blit(switch_button_text, (switch_button_rect.x + 10, switch_button_rect.y + 5))
    physics_toggle_colour = GREEN if natural_physics else RED # Toggle colour "light"
    pygame.draw.circle(screen, physics_toggle_colour, (WIDTH - 180, HEIGHT - 37), 6)
    
    draw_fixation_cross(screen, WHITE, (WIDTH // 2, HEIGHT // 2), 20)

    for event in pygame.event.get():
        counter = 0
        random.seed()
        # dragging = True
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reinit_game(show_aim=False)
                
        # Detect key press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                toggle_a = not toggle_a
                random.seed(random.seed(0,1000))

        # Mouse input to hit the ball
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check if the reinit button is clicked
            if reinit_button_rect.collidepoint(mouse_x, mouse_y):
                reinit_game(show_aim=False)        
                
            # Check if the switch button is clicked
            if switch_button_rect.collidepoint(mouse_x, mouse_y):
                natural_physics = not natural_physics
            
            # Check if the white ball is clicked
            elif math.sqrt((mouse_x - white_ball_x)**2 + (mouse_y - white_ball_y)**2) <= ball_radius:
                dragging = True
                start_pos = (mouse_x, mouse_y)
                
        back_to_normal = True
        if event.type == pygame.MOUSEBUTTONUP and auto_toggle == False and back_to_normal == True:
            if dragging:
                end_pos = pygame.mouse.get_pos()
                print(f"Start pos: {start_pos}, End pos: {end_pos}")
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                this_hit_angle = math.atan2(-dy, dx)  # Angle to hit
                power = min(math.sqrt(dx**2 + dy**2) / 5, 15)  # Power based on distance (clamped)
                hit_ball(this_hit_angle, power, stick_hit=True) # I CHANGED THIS BOOLEAN
                dragging = False
                print(f"Hit ball with power: {power}")
                
        # Detect key press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                
                auto_toggle = not auto_toggle
                print(f"Automatic shooting mode: {auto_toggle}")
                
                if auto_toggle:
                    start_pos = (white_ball_x, white_ball_y)
                    print(start_pos)

                    # Compute the perfect center-center hit given the ball positions
                    # end_pos = (white_ball_x - (red_ball_x - white_ball_x), white_ball_y - (red_ball_y - white_ball_y)) # if stick_hit is true
                    # end_pos = (white_ball_x + (red_ball_x - white_ball_x), white_ball_y + (red_ball_y - white_ball_y)) # if stick_hit is false, fix thiss later
                    end_pos = get_aim(fluct_fact=10, rand_seed=rand_seed)
                    print(f"This is the aimed location: {end_pos}")
                    dragging = True
                    
                    
                    # draw_arrow((white_ball_x, white_ball_y), end_pos, aim_line=False)
   
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    
                    this_hit_angle = math.atan2(-dy, dx)  # Angle to hit
                    power = min(math.sqrt(dx**2 + dy**2) / 5, 10)  # Power based on distance (clamped)
                    hit_ball(this_hit_angle, power, stick_hit=True) # I CHANGED THIS BOOLEAN
                    
    counter += clock.get_time()
    if counter >= 3000 and auto_toggle == True:
        auto_toggle = False
        print("Ready to shoot again, press s")
            # dragging = False
    
        

    move_ball(natural_bounce=natural_physics, hit_angle=this_hit_angle)
    pygame.display.flip()
    clock.tick(60)
    
    # if auto_toggle:
    #     time.sleep(1)
    #     reinit_game()

pygame.quit()
sys.exit()
