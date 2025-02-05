# import pygame
# import sys
# import math
# from pygame.locals import *

# # Initialize Pygame
# pygame.init()

# # Screen dimensions
# SCREEN_WIDTH, SCREEN_HEIGHT = 1500, 1000
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Bouncing Ball Simulation with Sliders")

# # Colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# GRAY = (200, 200, 200)
# BLUE = (0, 0, 255)
# GREEN = (0, 255, 0)
# RED = (255, 0, 0)

# # Ball properties
# ball_radius = 50

# # Physical parameters (default values)
# gravity = 0.5
# gravity_direction = 1  # 1 for normal, -1 for inverted
# ball_weight = 1
# ball_hardness = 0.8
# wind_horizontal = 0
# wind_vertical = 0
# floor_materials = {"sand": 0.5, "water": 0.3, "stone": 1.0}
# current_floor = "stone"

# # Floor properties
# floor_y = SCREEN_HEIGHT - 50
# floor_color = GRAY

# # Slider properties
# slider_positions = {
#     "Gravity": 0.5,
#     "Weight": 0.5,
#     "Hardness": 0.8,
#     "Wind Horizontal": 0.5,
#     "Wind Vertical": 0.5,
# }
# slider_ranges = {
#     "Gravity": (0.1, 2.0),
#     "Weight": (0.1, 2.0),
#     "Hardness": (0.1, 1.0),
#     "Wind Horizontal": (-1.0, 1.0),
#     "Wind Vertical": (-1.0, 1.0),
# }
# slider_rects = {
#     "Gravity": (50, 500, 200, 10),
#     "Weight": (50, 520, 200, 10),
#     "Hardness": (50, 540, 200, 10),
#     "Wind Horizontal": (300, 500, 200, 10),
#     "Wind Vertical": (300, 520, 200, 10),
# }
# selected_slider = None

# # Gravity inversion button
# gravity_inversion_button = pygame.Rect(600, 500, 150, 40)

# def initialize_game():
#     """Reset ball position to start state."""
#     global ball_pos, ball_velocity
#     ball_pos = [50, 50]  # Start slightly below the top-left
#     ball_velocity = [2, 0]  # Initial rightward movement

# initialize_game()

# def draw_sliders():
#     """Draw sliders for adjustable parameters."""
#     for name, rect in slider_rects.items():
#         x, y, w, h = rect
#         pygame.draw.rect(screen, GRAY, rect)  # Slider background
#         slider_pos = slider_positions[name]
#         slider_x = int(x + slider_pos * w)  # Map value to slider width
#         pygame.draw.circle(screen, BLUE, (slider_x, y + h // 2), 8)
#         text_surface = pygame.font.SysFont(None, 20).render(name, True, BLACK)
#         screen.blit(text_surface, (x, y - 20))

# def update_slider(mouse_pos):
#     """Update slider value based on mouse position."""
#     global selected_slider
#     if selected_slider:
#         x, y, w, h = slider_rects[selected_slider]
#         relative_x = max(0, min(w, mouse_pos[0] - x))
#         slider_positions[selected_slider] = relative_x / w

# def map_slider_values():
#     """Map slider positions to actual parameter values."""
#     global gravity, ball_weight, ball_hardness, wind_horizontal, wind_vertical
#     gravity = gravity_direction * slider_positions["Gravity"] * (slider_ranges["Gravity"][1] - slider_ranges["Gravity"][0]) + slider_ranges["Gravity"][0]
#     ball_weight = slider_positions["Weight"] * (slider_ranges["Weight"][1] - slider_ranges["Weight"][0]) + slider_ranges["Weight"][0]
#     ball_hardness = slider_positions["Hardness"] * (slider_ranges["Hardness"][1] - slider_ranges["Hardness"][0]) + slider_ranges["Hardness"][0]
#     wind_horizontal = slider_positions["Wind Horizontal"] * (slider_ranges["Wind Horizontal"][1] - slider_ranges["Wind Horizontal"][0]) + slider_ranges["Wind Horizontal"][0]
#     wind_vertical = slider_positions["Wind Vertical"] * (slider_ranges["Wind Vertical"][1] - slider_ranges["Wind Vertical"][0]) + slider_ranges["Wind Vertical"][0]

# def draw_wind_arrow():
#     """Draw an arrow representing wind direction and strength."""
#     arrow_x = SCREEN_WIDTH // 2
#     arrow_y = SCREEN_HEIGHT - 25
#     arrow_length = 50
#     end_x = int(arrow_x + wind_horizontal * arrow_length)
#     end_y = int(arrow_y - wind_vertical * arrow_length)
#     pygame.draw.line(screen, RED, (arrow_x, arrow_y), (end_x, end_y), 3)
#     pygame.draw.circle(screen, RED, (end_x, end_y), 5)

# # Main game loop
# clock = pygame.time.Clock()
# running = True

# while running:
#     screen.fill(WHITE)
    
#     # Draw floor
#     pygame.draw.rect(screen, floor_color, (0, floor_y, SCREEN_WIDTH, 50))
    
#     # Draw ball
#     pygame.draw.circle(screen, BLUE, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    
#     # Draw sliders
#     draw_sliders()
    
#     # Draw wind arrow
#     draw_wind_arrow()
    
#     # Draw gravity inversion button
#     pygame.draw.rect(screen, GRAY, gravity_inversion_button)
#     text_surface = pygame.font.SysFont(None, 20).render("Invert Gravity", True, BLACK)
#     screen.blit(text_surface, (gravity_inversion_button.x + 20, gravity_inversion_button.y + 10))
    
#     # Update ball position
#     map_slider_values()
#     ball_velocity[1] += gravity * ball_weight + wind_vertical  # Apply gravity and wind
#     ball_velocity[0] += wind_horizontal  # Apply horizontal wind
#     ball_pos[0] += ball_velocity[0]
#     ball_pos[1] += ball_velocity[1]
    
#     # Handle collisions with floor
#     if ball_pos[1] + ball_radius > floor_y:
#         ball_pos[1] = floor_y - ball_radius
#         ball_velocity[1] = -ball_velocity[1] * ball_hardness * floor_materials[current_floor]
    
#     # Handle collisions with walls
#     if ball_pos[0] - ball_radius < 0 or ball_pos[0] + ball_radius > SCREEN_WIDTH:
#         ball_velocity[0] = -ball_velocity[0]
    
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             running = False
#         elif event.type == MOUSEBUTTONDOWN:
#             for name, rect in slider_rects.items():
#                 if rect[0] <= event.pos[0] <= rect[0] + rect[2] and rect[1] <= event.pos[1] <= rect[1] + rect[3]:
#                     selected_slider = name
#             if gravity_inversion_button.collidepoint(event.pos):
#                 gravity_direction *= -1
#         elif event.type == MOUSEBUTTONUP:
#             selected_slider = None
#         elif event.type == MOUSEMOTION and selected_slider:
#             update_slider(event.pos)
#         elif event.type == KEYDOWN:
#             if event.key == K_r:
#                 initialize_game()
    
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
# sys.exit()

import pygame
import sys
import math
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bouncing Ball Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Ball properties
ball_radius = 20

# Initial physical parameters
gravity = 0.5
ball_weight = 1
ball_hardness = 0.8  # Coefficient of restitution
wind_resistance = 0
floor_materials = {"sand": 0.5, "water": 0.3, "stone": 1.0}
current_floor = "stone"

# Floor properties
floor_y = SCREEN_HEIGHT - 50
floor_color = GRAY

# Button positions and sizes
buttons = {
    "Gravity Up": (50, 500, 100, 40),
    "Gravity Down": (160, 500, 100, 40),
    "Increase Weight": (50, 550, 120, 40),
    "Decrease Weight": (180, 550, 120, 40),
    "Increase Hardness": (310, 500, 150, 40),
    "Decrease Hardness": (470, 500, 150, 40),
    "Toggle Floor": (640, 500, 120, 40),
}

def initialize_game():
    """Reset ball and parameters to initial state."""
    global ball_pos, ball_velocity, gravity, ball_weight, ball_hardness, wind_resistance, current_floor, floor_color
    ball_pos = [50, 50]  # Start slightly below the top-left
    ball_velocity = [2, 0]  # Initial rightward movement
    gravity = 0.5
    ball_weight = 1
    ball_hardness = 0.8
    wind_resistance = 0
    current_floor = "stone"
    floor_color = GRAY

initialize_game()

def draw_buttons():
    """Draw the control buttons."""
    for name, (x, y, w, h) in buttons.items():
        pygame.draw.rect(screen, GRAY, (x, y, w, h))
        text_surface = pygame.font.SysFont(None, 20).render(name, True, BLACK)
        screen.blit(text_surface, (x + 10, y + 10))

def check_button_click(mouse_pos):
    """Check if a button was clicked."""
    for name, (x, y, w, h) in buttons.items():
        if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
            return name
    return None

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    
    # Draw floor
    pygame.draw.rect(screen, floor_color, (0, floor_y, SCREEN_WIDTH, 50))
    
    # Draw ball
    pygame.draw.circle(screen, BLUE, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
    
    # Draw buttons
    draw_buttons()
    
    # Update ball position
    ball_velocity[1] += gravity * ball_weight  # Apply gravity
    ball_velocity[0] -= wind_resistance  # Apply wind resistance
    ball_pos[0] += ball_velocity[0]
    ball_pos[1] += ball_velocity[1]
    
    # Handle collisions with floor
    if ball_pos[1] + ball_radius > floor_y:
        ball_pos[1] = floor_y - ball_radius
        ball_velocity[1] = -ball_velocity[1] * ball_hardness * floor_materials[current_floor]
    
    # Handle collisions with walls
    if ball_pos[0] - ball_radius < 0 or ball_pos[0] + ball_radius > SCREEN_WIDTH:
        ball_velocity[0] = -ball_velocity[0]
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            clicked_button = check_button_click(event.pos)
            if clicked_button == "Gravity Up":
                gravity += 0.1
            elif clicked_button == "Gravity Down":
                gravity = max(0.1, gravity - 0.1)
            elif clicked_button == "Increase Weight":
                ball_weight += 0.1
            elif clicked_button == "Decrease Weight":
                ball_weight = max(0.1, ball_weight - 0.1)
            elif clicked_button == "Increase Hardness":
                ball_hardness = min(1.0, ball_hardness + 0.1)
            elif clicked_button == "Decrease Hardness":
                ball_hardness = max(0.1, ball_hardness - 0.1)
            elif clicked_button == "Toggle Floor":
                floor_cycle = list(floor_materials.keys())
                current_index = floor_cycle.index(current_floor)
                current_floor = floor_cycle[(current_index + 1) % len(floor_cycle)]
                floor_color = {"sand": (194, 178, 128), "water": BLUE, "stone": GRAY}[current_floor]
        elif event.type == KEYDOWN:
            if event.key == K_r:
                initialize_game()  # Reinitialize the game
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
