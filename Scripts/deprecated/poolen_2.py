import pygame
import math
import sys
import random
import time

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

ball_spawn_margin = 250 # used to be 75

# TODO: make sure it canno toverlap with the red ball through random spawnign
random_pos = random.randint(ball_spawn_margin, WIDTH-ball_spawn_margin), random.randint(ball_spawn_margin, HEIGHT-ball_spawn_margin) # not used anymore

# Ball properties
ball_radius = 30
red_ball_x, red_ball_y = WIDTH // 2, HEIGHT // 2
# white_ball_x, white_ball_y = WIDTH // random.randint(1,4), HEIGHT // random.randint(1,2)
white_ball_x, white_ball_y = random_pos

red_ball_velocity = [0, 0]  # [x_velocity, y_velocity]
white_ball_velocity = [0, 0]    # [x_velocity, y_velocity]
friction = 0.99  # Friction coefficient (was .98, which is probably more realistic)
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
def draw_table():
    screen.fill(DARKGREY)
    pygame.draw.rect(screen, BLACK, (25, 25, WIDTH - 50, HEIGHT - 50), 25)  # Table boundary

def draw_ball(x, y, color):
    pygame.draw.circle(screen, color, (int(x), int(y)), ball_radius)

# def draw_arrow(start_pos, end_pos):
#     pygame.draw.line(screen, red, start_pos, end_pos, 3)
#     pygame.draw.circle(screen, red, end_pos, 5)

# Adaptation for dotted aim arrow
def draw_arrow(start_pos, end_pos):
    # Draw the original continuous line and circle
    pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
    pygame.draw.circle(screen, WHITE, end_pos, 5)
    
    # Calculate the direction vector of the original line
    # dx = end_pos[0] - start_pos[0]
    # dy = end_pos[1] - start_pos[1]
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
    global red_ball_x, red_ball_y, white_ball_x, white_ball_y, red_ball_velocity, white_ball_velocity

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
        
        if natural_bounce:
            # Calculate angle of collision
            angle = math.atan2(dy, dx)
            sin_angle = math.sin(angle)
            cos_angle = math.cos(angle)
            distort_by = 0
            natural_angle = angle

        else:
            # Randomly generate an angle of collision to create unnatural bounce collision
            # angle = random.uniform(0, 2 * math.pi)
            # angle = math.atan2(dy + random.randint(100, 200), dx + random.randint(100, 200)) 
            natural_angle = math.atan2(dy, dx)
            
            # Attempt to prevent it from getting stuck in one another, but the problem is that
            # this overlap happens wshen they collide in their sideskirts (schampschoten), so 
            # I need to find a way to incorporate this in the dx dy. Basically, I can compute from the
            # derivative from the line fitted to each starting position compawhite to the natural angle
            # what the difference is between the angle and the natural angle, and then based on the difference
            # in derivative of those lines I can determine how much to distort the angle. If derivative delta is
            # positive the distortion should be positive and vice versa, or better yet determine a range of distortions
            # that ensure the balls will not get stuck in each other.
                
            if natural_angle + hit_angle < 0:
                distort_by = .75
            else:
                distort_by = -.75
                
            angle = natural_angle + distort_by # I need to find a more visually realistic way to do this
            sin_angle = math.sin(angle) #+ random.uniform(-0.5, 0.5)
            cos_angle = math.cos(angle) #+ random.uniform(-0.5, 0.5)


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

def reinit_game():
    global red_ball_x, red_ball_y, white_ball_x, white_ball_y, red_ball_velocity, white_ball_velocity    
    # Reinitialize the game state
    red_ball_x, red_ball_y = WIDTH // 2, HEIGHT // 2
    white_ball_x, white_ball_y = random.randint(ball_spawn_margin, WIDTH-ball_spawn_margin), random.randint(ball_spawn_margin, HEIGHT-ball_spawn_margin)
    # white_ball_x, white_ball_y = 100, 100
    red_ball_velocity = [0, 0]
    white_ball_velocity = [0, 0]

# Main loop
dragging = False
start_pos = (0, 0)
this_hit_angle = None
running = True

while running:
    screen.fill(GREEN)
    draw_table()
    
    draw_ball(red_ball_x, red_ball_y, RED)
    draw_ball(white_ball_x, white_ball_y, WHITE)

    pygame.draw.rect(screen, WHITE, reinit_button_rect)
    screen.blit(reinit_button_text, (reinit_button_rect.x + 10, reinit_button_rect.y + 5))
    
    
    pygame.draw.rect(screen, WHITE, switch_button_rect)
    screen.blit(switch_button_text, (switch_button_rect.x + 10, switch_button_rect.y + 5))
    physics_toggle_colour = GREEN if natural_physics else RED
    pygame.draw.circle(screen, physics_toggle_colour, (WIDTH - 180, HEIGHT - 37), 6)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse input to hit the ball
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Check if the reinit button is clicked
            if reinit_button_rect.collidepoint(mouse_x, mouse_y):
                reinit_game()        
                
            # Check if the switch button is clicked
            if switch_button_rect.collidepoint(mouse_x, mouse_y):
                natural_physics = not natural_physics
            
            # Check if the white ball is clicked
            elif math.sqrt((mouse_x - white_ball_x)**2 + (mouse_y - white_ball_y)**2) <= ball_radius:
                dragging = True
                start_pos = (mouse_x, mouse_y)

        if event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                end_pos = pygame.mouse.get_pos()
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                this_hit_angle = math.atan2(-dy, dx)  # Angle to hit
                power = min(math.sqrt(dx**2 + dy**2) / 10, 10)  # Power based on distance (clamped)
                hit_ball(this_hit_angle, power, stick_hit=True) # I CHANGED THIS BOOLEAN
                dragging = False
                
                print(f"{this_hit_angle} This is the angle variable in the loop, check if it is different from the previously printed one")

    if dragging:
        current_pos = pygame.mouse.get_pos()
        draw_arrow((white_ball_x, white_ball_y), current_pos)

    move_ball(natural_bounce=natural_physics, hit_angle=this_hit_angle)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
