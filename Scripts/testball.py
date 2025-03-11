class RealisticBall:
    def __init__(self, win, pos=(0, 0), radius=50, color=(1, 0, 0), shadow_opacity=0.3):
        # Store initial position as float array
        self._pos = np.array(pos, dtype=float)
        self.radius = radius
        self._color = color
        
        # Create all visual elements with explicit units
        # Main ball - setting vertices explicitly to avoid radius calculations
        n_vertices = 36  # enough for a smooth circle
        angles = np.linspace(0, 2*np.pi, n_vertices, endpoint=False)
        vertices = np.array([(np.cos(angle)*radius, np.sin(angle)*radius) for angle in angles])
        
        self.ball = visual.ShapeStim(
            win=win,
            vertices=vertices,
            pos=self._pos,
            fillColor=color,
            lineWidth=0
        )
        
        # Highlight
        highlight_radius = radius * 0.3
        highlight_vertices = np.array([(np.cos(angle)*highlight_radius, np.sin(angle)*highlight_radius) 
                                      for angle in angles])
        
        self.highlight = visual.ShapeStim(
            win=win,
            vertices=highlight_vertices,
            pos=(self._pos[0] - radius * 0.3, self._pos[1] + radius * 0.3),
            fillColor=(1, 1, 1),
            opacity=0.7,
            lineWidth=0
        )
        
        # Shadow (elliptical)
        shadow_width = radius * 2
        shadow_height = radius * 0.5
        shadow_vertices = np.array([(np.cos(angle)*shadow_width/2, np.sin(angle)*shadow_height/2) 
                                   for angle in angles])
        
        self.shadow = visual.ShapeStim(
            win=win,
            vertices=shadow_vertices,
            pos=(self._pos[0], self._pos[1] - radius * 1.2),
            fillColor=(-1, -1, -1),
            opacity=shadow_opacity,
            lineWidth=0
        )
        
        # Color reflection
        reflection_width = radius * 1.8
        reflection_height = radius * 0.4
        reflection_vertices = np.array([(np.cos(angle)*reflection_width/2, np.sin(angle)*reflection_height/2) 
                                       for angle in angles])
        
        self.reflection = visual.ShapeStim(
            win=win,
            vertices=reflection_vertices,
            pos=(self._pos[0], self._pos[1] - radius * 1.2),
            fillColor=color,
            opacity=0.2,
            lineWidth=0
        )
    
    def draw(self):
        # Draw elements in correct order (back to front)
        self.reflection.draw()
        self.shadow.draw()
        self.ball.draw()
        self.highlight.draw()
    
    # Property getters and setters for pos
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, new_pos):
        # Handle both direct assignment and in-place addition
        self._pos = np.array(new_pos, dtype=float)
        
        # Update component positions
        self.ball.pos = self._pos
        self.highlight.pos = (self._pos[0] - self.radius * 0.3, self._pos[1] + self.radius * 0.3)
        self.shadow.pos = (self._pos[0], self._pos[1] - self.radius * 1.2)
        self.reflection.pos = (self._pos[0], self._pos[1] - self.radius * 1.2)
    
    # Property getters and setters for color
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, new_color):
        self._color = new_color
        self.ball.fillColor = new_color
        self.reflection.fillColor = new_color
    
    # Additional methods to match PsychoPy's standard stim methods
    def setPos(self, pos):
        self.pos = pos
    
    def setColor(self, color):
        self.color = color
from psychopy import visual, core
import numpy as np

# Create window
win = visual.Window([800, 600], color=(-1, -1, -1), units='pix')

# Test with a simple Circle first
test_circle = visual.Circle(win, radius=50, pos=(0,0), fillColor='white')
test_circle.draw()
win.flip()
core.wait(1)

# Copy your RealisticBall class here...

# Test with the RealisticBall
ball = RealisticBall(win, pos=(0, 0), radius=50, color=(1, 0, 0))
ball.draw()
win.flip()
core.wait(2)

win.close()