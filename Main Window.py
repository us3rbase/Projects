# ITMedia Project

import pygame
import sys
import os
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info

# Initialize pygame
pygame.init()

# Initialize tkinter in the main thread
initialize_tkinter()

# Constants - Updated to match your window
WINDOW_WIDTH = 697
WINDOW_HEIGHT = 456
RED = (255, 0, 0)  # Backup color in case image loading fails
SQUARE_SIZE = 30   # Size of the character
MOVEMENT_SPEED = 5
WHITE = (255, 255, 255)  # White background to match your image

# Position the pygame window (this helps with notification placement)
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the window on the screen

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Character Movement")

def get_window_position():
    """Get the pygame window position"""
    import ctypes
    
    # This is a Windows-specific approach to get the window handle and position
    try:
        # Get window handle
        hwnd = pygame.display.get_wm_info()["window"]
        
        # Get window rect
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        return rect.left, rect.top
    except (ImportError, AttributeError, KeyError):
        # Fallback for non-Windows or if the approach fails
        # Since pygame.NOFRAME is used, we can use the display's offset
        screen_info = pygame.display.Info()
        
        # Default to centered on the screen
        screen_width = pygame.display.get_desktop_sizes()[0][0]
        screen_height = pygame.display.get_desktop_sizes()[0][1]
        
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        
        return x, y

def load_fight_box():
    try:
        # Try to load the background image
        background_image = pygame.image.load('fight.jpg')
        # Scale it to fit the window size
        return pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error:
        print("Could not load background image. Using white background instead.")
        return None
        
def load_background():
    try:
        # Try to load the background image
        background_image = pygame.image.load('background.jpg')
        # Scale it to fit the window size
        return pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error:
        print("Could not load background image. Using white background instead.")
        return None

# Create the player character
class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2 - SQUARE_SIZE // 2
        self.y = WINDOW_HEIGHT // 2 - SQUARE_SIZE // 2
        self.width = SQUARE_SIZE
        self.height = SQUARE_SIZE
        self.speed = MOVEMENT_SPEED
        
        # Define different padding for each side
        self.padding_left = 205    # Left padding
        self.padding_right = 201   # Right padding (same as left)
        self.padding_top = 257     # Top padding
        self.padding_bottom = 53  # Bottom padding
        
        # Try to load the character image
        self.use_image = True
        try:
            # Load the character sprite - replace 'character.png' with your image
            self.image = pygame.image.load('char.jpg')
            # Scale the image to match the desired size
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error:
            print("Could not load character image. Using red square instead.")
            self.use_image = False
    
    def draw(self):
        if self.use_image:
            # Draw the character sprite
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback to red square if image loading failed
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def move(self, dx=0, dy=0):
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check x boundaries with custom padding
        if new_x < self.padding_left:
            self.x = self.padding_left
        elif new_x > WINDOW_WIDTH - self.width - self.padding_right:
            self.x = WINDOW_WIDTH - self.width - self.padding_right
        else:
            self.x = new_x
        
        # Check y boundaries with custom padding
        if new_y < self.padding_top:
            self.y = self.padding_top
        elif new_y > WINDOW_HEIGHT - self.height - self.padding_bottom:
            self.y = WINDOW_HEIGHT - self.height - self.padding_bottom
        else:
            self.y = new_y

# Create the player
player = Player()

# Game loop
clock = pygame.time.Clock()
running = True

player_needed = True
previous_player_needed = player_needed  # Track previous state to detect changes
current_background = load_fight_box()  # Initialize with the default background

# Set initial position
player.x = 333
player.y = 302

# Flag to track if notification has been shown
notification_shown = False

# Get and set window position for notifications
# Allow a short delay for the window to fully initialize before getting its position
pygame.time.delay(100)
window_x, window_y = get_window_position()
set_pygame_window_info(window_x, window_y, WINDOW_WIDTH, WINDOW_HEIGHT)

# Define a key cooldown to prevent multiple notifications
key_cooldown = 1
cooldown_time = 30  # frames

def dialog_create(message="", delay=1):
    create_xp_notification(message, delay)
    cooldown_time = delay * 60
    key_cooldown = cooldown_time
        
dialog_create("Test Dialog", 10)
dialog_create("test dialog 2", 10)

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle continuous key presses using WASD
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_q]:
        player_needed = not player_needed  # Toggle player_needed state with Q key
        
    # Check if player_needed state has changed
    if previous_player_needed != player_needed:
        if player_needed:
            current_background = load_fight_box()
        else:
            current_background = load_background()
        previous_player_needed = player_needed
    
    # Movement controls only when player is needed
    if player_needed:
        if keys[pygame.K_a]:  # A key for left
            player.move(dx=-player.speed)
        if keys[pygame.K_d]:  # D key for right
            player.move(dx=player.speed)
        if keys[pygame.K_w]:  # W key for up
            player.move(dy=-player.speed)
        if keys[pygame.K_s]:  # S key for down
            player.move(dy=player.speed)
    
    if keys[pygame.K_ESCAPE]:
        running = False

    # Show notification with N key (with cooldown)

    # Reduce cooldown timer
    if key_cooldown > 0:
        key_cooldown -= 1

    # Draw the background
    if current_background:
        screen.blit(current_background, (0, 0))
    else:
        screen.fill(WHITE)  # White background as fallback
    
    # Draw the player only if needed
    if player_needed:
        player.draw()
    
    # Update the display
    pygame.display.flip()
    
    
    # Update tkinter (handle notification windows)
    update_tkinter()
    
    # Cap the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
sys.exit()
