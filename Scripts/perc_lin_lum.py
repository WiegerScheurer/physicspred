
# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# from psychopy import visual, core, event, monitors
# import numpy as np

# def lab_to_rgb(L, a, b):
#     """
#     Convert CIELAB color space to RGB
#     Simplified conversion assuming D65 white point
#     """
#     # Constants for D65 white point
#     Xn, Yn, Zn = 95.047, 100.000, 108.883
    
#     # Convert L*a*b* to XYZ
#     fy = (L + 16) / 116
#     fx = a / 500 + fy
#     fz = fy - b / 200
    
#     # Inverse of f function
#     def f_inv(t):
#         return t**3 if t > 0.206893 else (t - 16/116) / 7.787
    
#     X = Xn * f_inv(fx)
#     Y = Yn * f_inv(fy)
#     Z = Zn * f_inv(fz)
    
#     # XYZ to RGB (assuming sRGB)
#     R = 3.2406 * X/100 - 1.5372 * Y/100 - 0.4986 * Z/100
#     G = -0.9689 * X/100 + 1.8758 * Y/100 + 0.0415 * Z/100
#     B = 0.0557 * X/100 - 0.2040 * Y/100 + 1.0570 * Z/100
    
#     # Clip and scale to -1 to 1 range
#     # RGB = np.clip([R, G, B], -1, 1)
#     RGB = np.clip([R, G, B], 0, 255)
#     return RGB

# def create_perceptual_luminance_series(background_lab, n_steps):
#     """
#     Create perceptually linear luminance steps from middle to extremes
    
#     :param background_lab: Background color in L*a*b*
#     :param n_steps: Number of steps (should be odd)
#     :return: List of RGB colors
#     """
#     # Determine middle step
#     mid_step = n_steps // 2
    
#     # Create luminance steps
#     colors = []
#     for i in range(n_steps):
#         # Calculate relative position from middle
#         rel_pos = i - mid_step
        
#         # Interpolate luminance
#         if rel_pos == 0:
#             # Middle step is neutral grey
#             color_lab = [50, 0, 0]  # Neutral mid-grey in L*a*b*
#         elif rel_pos < 0:
#             # Steps towards black
#             color_lab = [50 * (1 + rel_pos / mid_step), 0, 0]
#         else:
#             # Steps towards white
#             color_lab = [50 + (100 - 50) * (rel_pos / mid_step), 0, 0]
        
#         # Convert to RGB
#         colors.append(lab_to_rgb(*color_lab))
    
#     return colors

# # Create a monitor and window
# mon = monitors.Monitor('testMonitor', width=53, distance=70)
# mon.setSizePix([1080, 1080])
# mon.save()

# # Create the window
# win = visual.Window(size=[1080, 1080], monitor=mon, color='gray', units='norm', fullscr=False, colorSpace='rgb255')

# # Parameters for the grid
# grid_rows = 9
# grid_cols = 9

# # Calculate positions and sizes
# ball_size = 0.15  # normalized size of each ball
# h_spacing = 2 / (grid_cols + 1)  # horizontal spacing
# v_spacing = 2 / (grid_rows + 1)  # vertical spacing

# # Create background colors for rows (in L*a*b*)
# # Varying backgrounds from dark to light
# background_colors_lab = [
#     [0, 0, 0],   # Very dark
#     [35, 0, 0],
#     [50, 0, 0],
#     [65, 0, 0],
#     [50, 0, 0],   # Middle row is neutral grey
#     [35, 0, 0],
#     [50, 0, 0],
#     [65, 0, 0],
#     [80, 0, 0]    # Very light
# ]


# # Create balls and backgrounds
# balls = []
# backgrounds = []
# labels = []

# for row in range(grid_rows):
#     row_balls = []
#     row_labels = []
    
#     # Background for this row
#     bg_color_lab = background_colors_lab[row]
#     bg_color_rgb = lab_to_rgb(*bg_color_lab)
#     bg_stim = visual.Rect(win, width=2, height=v_spacing, 
#                           pos=(0, 1 - (row + 1) * v_spacing), 
#                           fillColor=bg_color_rgb, 
#                           lineColor=bg_color_rgb)
#     backgrounds.append(bg_stim)
    
#     # Create perceptually linear luminance series for this row
#     luminance_colors = create_perceptual_luminance_series(bg_color_lab, grid_cols)
    
#     for col in range(grid_cols):
#         # Calculate ball position
#         x_pos = -1 + (col + 1) * h_spacing
#         y_pos = 1 - (row + 1) * v_spacing
        
#         # Create ball
#         ball_color = luminance_colors[col]
#         ball = visual.Circle(win, 
#                              radius=ball_size/2, 
#                              pos=(x_pos, y_pos), 
#                              fillColor=ball_color, 
#                              lineColor=ball_color)
        
#         # Create text label with scaled RGB values
#         scaled_rgb = [round((c + 1) * 127.5) for c in ball_color]
#         rgb_label = f'{scaled_rgb}'
#         label = visual.TextStim(win, 
#                                 text=rgb_label, 
#                                 pos=(x_pos, y_pos - ball_size/2 - 0.05), 
#                                 height=0.025, 
#                                 color='white')
        
#         row_balls.append(ball)
#         row_labels.append(label)
    
#     balls.append(row_balls)
#     labels.append(row_labels)

# # Draw everything
# for bg in backgrounds:
#     bg.draw()

# for row in balls:
#     for ball in row:
#         ball.draw()

# for row in labels:
#     for label in row:
#         label.draw()

# # Flip the window to show the stimuli
# win.flip()

# # Wait for key press
# event.waitKeys()

# # Close the window
# win.close()
# core.quit()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy import visual, core, event, monitors
import numpy as np
# import scikit-image as skimage
import skimage
from skimage import color




# def lab_to_rgb(L, a, b):
#     """
#     Convert CIELAB color space to RGB
#     Simplified conversion assuming D65 white point
#     """
#     # Constants for D65 white point
#     Xn, Yn, Zn = 95.047, 100.000, 108.883
    
#     # Convert L*a*b* to XYZ
#     fy = (L + 16) / 116
#     fx = a / 500 + fy
#     fz = fy - b / 200
    
#     # Inverse of f function
#     def f_inv(t):
#         return t**3 if t > 0.206893 else (t - 16/116) / 7.787
    
#     X = Xn * f_inv(fx)
#     Y = Yn * f_inv(fy)
#     Z = Zn * f_inv(fz)
    
#     # XYZ to RGB (assuming sRGB)
#     R = 3.2406 * X/100 - 1.5372 * Y/100 - 0.4986 * Z/100
#     G = -0.9689 * X/100 + 1.8758 * Y/100 + 0.0415 * Z/100
#     B = 0.0557 * X/100 - 0.2040 * Y/100 + 1.0570 * Z/100
    
#     # Clip and scale to 0-255 range
#     RGB = np.clip([R, G, B], 0, 1) * 255
#     return RGB

# def lab_to_rgb(L, a, b):
#     lab = np.array([[[L, a, b]]], dtype=np.float32)
#     rgb = color.lab2rgb(lab)
#     return rgb[0][0]

def lab_to_rgb(L, a, b):
    lab = np.array([[[L, a, b]]], dtype=np.float32)
    rgb = color.lab2rgb(lab)
    # Scale to 0-255 range and return as integer values
    rgb_255 = np.clip(rgb[0][0] * 255, 0, 255).astype(int)
    return rgb_255

# def create_perceptual_luminance_series(background_lab, n_steps):
#     """
#     Create perceptually linear luminance steps from middle to extremes
    
#     :param background_lab: Background color in L*a*b*
#     :param n_steps: Number of steps (should be odd)
#     :return: List of RGB colors
#     """
#     # Determine middle step
#     mid_step = n_steps // 2
    
#     # Create luminance steps
#     colors = []
#     for i in range(n_steps):
#         # Calculate relative position from middle
#         rel_pos = i - mid_step
        
#         # Interpolate luminance
#         if rel_pos == 0:
#             # Middle step is neutral grey
#             color_lab = [50, 0, 0]  # Neutral mid-grey in L*a*b*
#         elif rel_pos < 0:
#             # Steps towards black
#             color_lab = [50 * (1 + rel_pos / mid_step), 0, 0]
#         else:
#             # Steps towards white
#             color_lab = [50 + (100 - 50) * (rel_pos / mid_step), 0, 0]
        
#         # Convert to RGB
#         colors.append(lab_to_rgb(*color_lab))
    
#     return colors

def create_perceptual_luminance_series(background_lab, n_steps):
    """
    Create perceptually linear luminance steps from middle to extremes, considering Weber contrast
    
    :param background_lab: Background color in L*a*b*
    :param n_steps: Number of steps (should be odd)
    :return: List of RGB colors
    """
    # Determine middle step
    mid_step = n_steps // 2
    
    # Background luminance
    L_b = background_lab[0]
    
    # Create luminance steps
    colors = []
    for i in range(n_steps):
        # Calculate relative position from middle
        rel_pos = i - mid_step
        
        # Interpolate luminance with Weber contrast
        if rel_pos == 0:
            # Middle step is the background color
            color_lab = background_lab
        elif rel_pos < 0:
            # Steps towards black
            L = L_b * (1 + rel_pos / mid_step)
            color_lab = [L, 0, 0]
        else:
            # Steps towards white
            L = L_b + (100 - L_b) * (rel_pos / mid_step)
            color_lab = [L, 0, 0]
        
        # Convert to RGB
        colors.append(lab_to_rgb(*color_lab))
    
    return colors

# Create a monitor and window
mon = monitors.Monitor('testMonitor', width=53, distance=70)
mon.setSizePix([1080, 1080])
mon.save()

# Create the window with RGB255 color space
win = visual.Window(size=[1080, 1080], monitor=mon, color=[127, 127, 127], units='norm', 
                    fullscr=False, colorSpace='rgb255')

# Parameters for the grid
grid_rows = 9
grid_cols = 9

# Calculate positions and sizes
ball_size = 0.15  # normalized size of each ball
h_spacing = 2 / (grid_cols + 1)  # horizontal spacing
v_spacing = 2 / (grid_rows + 1)  # vertical spacing

# # Create background colors with smooth gradient from white to black
# background_colors_lab = [
#     [100, 0, 0],  # Pure white
#     [90, 0, 0],
#     [80, 0, 0],
#     [70, 0, 0],
#     [50, 0, 0],   # Middle row is neutral grey
#     [40, 0, 0],
#     [30, 0, 0],
#     [20, 0, 0],
#     [0, 0, 0]     # Pure black
# ]

# # Create background colors with smooth gradient from white to black in 'rgb255' colorspace
# background_colors_lab = [
#     [255, 255, 255],  # Pure white
#     [204, 204, 204],  # Light grey
#     [153, 153, 153],  # Medium light grey
#     [102, 102, 102],  # Medium grey
#     [51, 51, 51],     # Medium dark grey
#     [40, 40, 40],     # Dark grey
#     [30, 30, 30],     # Darker grey
#     [20, 20, 20],     # Very dark grey
#     [0, 0, 0]         # Pure black
# ]



# def lab_to_rgb(L, a, b):
#     lab = np.array([[[L, a, b]]], dtype=np.float32)
#     rgb = color.lab2rgb(lab)
#     return rgb[0][0]

# Create background colors with smooth gradient from white to black in CIELAB color space
# background_colors_lab = [
#     [100, 0, 0],  # Pure white
#     [90, 0, 0],
#     [80, 0, 0],
#     [70, 0, 0],
#     [50, 0, 0],   # Middle row is neutral grey
#     [40, 0, 0],
#     [30, 0, 0],
#     [20, 0, 0],
#     [0, 0, 0]     # Pure black
# ]

# vals = np.round(np.linspace(0, 100, 9), 2)

# background_colors_lab = [([val, 0, 0]) for val in vals]


# Generate 9 evenly spaced L* values from 0 (black) to 100 (white)
vals = np.linspace(0, 100, 9)

# Create background colors in CIELAB color space
background_colors_lab = [[val, 0, 0] for val in vals]

# Convert the CIELAB colors to RGB
background_colors_rgb = [lab_to_rgb(*color) for color in background_colors_lab]

# Print the RGB values to verify
for i, rgb in enumerate(background_colors_rgb):
    print(f"Step {i}: RGB = {rgb}")
    
    
    

# Create balls and backgrounds
balls = []
backgrounds = []
labels = []

for row in range(grid_rows):
    row_balls = []
    row_labels = []
    
    # Background for this row
    bg_color_lab = background_colors_lab[row]
    bg_color_rgb = lab_to_rgb(*bg_color_lab)
    bg_stim = visual.Rect(win, width=2, height=v_spacing, 
                          pos=(0, 1 - (row + 1) * v_spacing), 
                          fillColor=bg_color_rgb, 
                          lineColor=bg_color_rgb,
                          colorSpace='rgb255')
    backgrounds.append(bg_stim)
    
    # Create perceptually linear luminance series for this row
    luminance_colors = create_perceptual_luminance_series(bg_color_lab, grid_cols)
    
    for col in range(grid_cols):
        # Calculate ball position
        x_pos = -1 + (col + 1) * h_spacing
        y_pos = 1 - (row + 1) * v_spacing
        
        # Create ball
        ball_color = luminance_colors[col]
        ball = visual.Circle(win, 
                             radius=ball_size/2, 
                             pos=(x_pos, y_pos), 
                             fillColor=ball_color, 
                             lineColor=ball_color,
                             colorSpace='rgb255')
        
        # Create text label with RGB values
        rgb_label = f'{[round(c) for c in ball_color]}'
        label = visual.TextStim(win, 
                                text=rgb_label, 
                                pos=(x_pos, y_pos - ball_size/2 - 0.015), 
                                height=0.025, 
                                color='white')
        
        row_balls.append(ball)
        row_labels.append(label)
    
    balls.append(row_balls)
    labels.append(row_labels)

# Draw everything
for bg in backgrounds:
    bg.draw()

for row in balls:
    for ball in row:
        ball.draw()

for row in labels:
    for label in row:
        label.draw()

# Flip the window to show the stimuli
win.flip()

# Wait for key press
event.waitKeys()

# Close the window
win.close()
core.quit()