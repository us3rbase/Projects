# ITMedia Project

import pygame
import sys
import os
import time
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info
from Dialog import dialog_create, tutorial_scene
from Enemies import Enemy, EnemyManager, start_fight_scene

pygame.init()

initialize_tkinter()

WINDOW_WIDTH = 697
WINDOW_HEIGHT = 456
RED = (255, 0, 0)
CHAR_SIZE = 30
MOVEMENT_SPEED = 5
WHITE = (255, 255, 255)

os.environ['SDL_VIDEO_CENTERED'] = '1'

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Character Movement")

def get_window_position():
    import ctypes
    
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        return rect.left, rect.top
    except (ImportError, AttributeError, KeyError):
        screen_info = pygame.display.Info()
        
        screen_width = pygame.display.get_desktop_sizes()[0][0]
        screen_height = pygame.display.get_desktop_sizes()[0][1]
        
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        
        return x, y

def load_fight_box():
    try:
        background_image = pygame.image.load('fight.jpg')
        return pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error:
        print("Could not load background image. Using white background instead.")
        return None
        
def load_background():
    try:
        background_image = pygame.image.load('background.jpg')
        return pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error:
        print("Could not load background image. Using white background instead.")
        return None

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2 - CHAR_SIZE // 2
        self.y = WINDOW_HEIGHT // 2 - CHAR_SIZE // 2
        self.width = CHAR_SIZE
        self.height = CHAR_SIZE
        self.speed = MOVEMENT_SPEED
        self.health = 100
        self.player_hit_cooldown = 0  # Invincibility frames after being hit
        
        self.padding_left = 205
        self.padding_right = 201
        self.padding_top = 227
        self.padding_bottom = 63
        
        self.use_image = True
        try:
            self.image = pygame.image.load('char.jpg')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error:
            print("Could not load character image. Using red square instead.")
            self.use_image = False
            
        # Attack properties
        self.attack_cooldown = 0
        self.attack_max_cooldown = 180  # 3 seconds at 60 FPS
        self.can_attack = True
    
    def draw(self):
        # Flash if in invincibility frames
        if self.player_hit_cooldown > 0 and self.player_hit_cooldown % 10 > 5:
            return  # Skip drawing to create flashing effect
            
        if self.use_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        
        # Draw attack cooldown indicator
        cooldown_percentage = self.attack_cooldown / self.attack_max_cooldown
        cooldown_color = (0, 255, 0) if cooldown_percentage == 0 else (255, 255, 0)  # Green when ready, yellow when cooling down
        
        # Draw cooldown bar above player
        bar_width = self.width
        bar_height = 5
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y - 10, bar_width, bar_height))  # Background
        if cooldown_percentage < 1:  # Only draw if not fully on cooldown
            pygame.draw.rect(screen, cooldown_color, 
                         (self.x, self.y - 10, int(bar_width * (1 - cooldown_percentage)), bar_height))  # Foreground
    
    def move(self, dx=0, dy=0):
        new_x = self.x + dx
        new_y = self.y + dy
        
        if new_x < self.padding_left:
            self.x = self.padding_left
        elif new_x > WINDOW_WIDTH - self.width - self.padding_right:
            self.x = WINDOW_WIDTH - self.width - self.padding_right
        else:
            self.x = new_x
        
        if new_y < self.padding_top:
            self.y = self.padding_top
        elif new_y > WINDOW_HEIGHT - self.height - self.padding_bottom:
            self.y = WINDOW_HEIGHT - self.height - self.padding_bottom
        else:
            self.y = new_y
    
    def attack(self):
        """Perform an attack if not on cooldown"""
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_max_cooldown
            return True
        return False
    
    def take_damage(self, amount=10):
        """Player takes damage if not in invincibility frames"""
        if self.player_hit_cooldown <= 0:
            self.health -= amount
            self.player_hit_cooldown = 60  # 1 second of invincibility
            return True
        return False
    
    def update(self):
        """Update player state"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.player_hit_cooldown > 0:
            self.player_hit_cooldown -= 1

# Game state variables
class GameState:
    def __init__(self):
        self.state = "tutorial"  # States: "tutorial", "exploration", "combat", "transition"
        self.enemy_manager = None
        self.score = 0
        self.transition_timer = 0
        self.transition_target = None
        self.player_health = 100
        
    def start_transition(self, target_state, duration=60):
        """Start transition to a new state"""
        self.state = "transition"
        self.transition_target = target_state
        self.transition_timer = duration
        
    def update(self):
        """Update game state"""
        if self.state == "transition":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.state = self.transition_target
                self.transition_target = None
                
                # Initialize the target state
                if self.state == "combat":
                    self.enemy_manager = EnemyManager(WINDOW_WIDTH, WINDOW_HEIGHT)
                    self.enemy_manager.spawn_enemy(count=1)  # Just one enemy for Undertale style

player = Player()
game_state = GameState()

clock = pygame.time.Clock()
running = True

player_needed = True
previous_player_needed = player_needed
current_background = load_fight_box()

player.x = 333
player.y = 302

pygame.time.delay(100)
window_x, window_y = get_window_position()
set_pygame_window_info(window_x, window_y, WINDOW_WIDTH, WINDOW_HEIGHT)

# Run the tutorial scene
tutorial_scene()

# Set up a timer to start the fight dialog after tutorial without freezing game
start_fight_timer = pygame.time.get_ticks() + 1000  # Start fight dialog 1 second after tutorial
enemy_spawn_timer = None  # Will be set after dialog finishes

while running:
    current_time = pygame.time.get_ticks()
    
    # Check if it's time to start the fight dialog
    if game_state.state == "tutorial" and current_time >= start_fight_timer and enemy_spawn_timer is None:
        enemy_spawn_timer = start_fight_scene()  # This shows dialog and returns when to spawn enemy
    
    # Check if it's time to spawn the enemy
    if game_state.state == "tutorial" and enemy_spawn_timer is not None and current_time >= enemy_spawn_timer:
        game_state.start_transition("combat", 60)  # Transition to combat in 1 second
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state.state == "combat":
                if player.attack():
                    # Player attacks all enemies
                    if game_state.enemy_manager:
                        defeated = game_state.enemy_manager.player_attack(25)  # Deal 25 damage
                        
                        if defeated > 0:
                            game_state.score += defeated * 100
                            print(f"Defeated {defeated} enemies! Score: {game_state.score}")
                            
                            if game_state.enemy_manager.count_active_enemies() == 0:
                                dialog_create("Tut", "Great job! You defeated the virus!", 3)
                                # Transition to next state after victory
                                game_state.start_transition("exploration", 180)
    
    keys = pygame.key.get_pressed()
    
    if previous_player_needed != player_needed:
        if player_needed:
            current_background = load_fight_box()
        else:
            current_background = load_background()
        previous_player_needed = player_needed
    
    if player_needed and game_state.state == "combat":
        if keys[pygame.K_a]:
            player.move(dx=-player.speed)
        if keys[pygame.K_d]:
            player.move(dx=player.speed)
        if keys[pygame.K_w]:
            player.move(dy=-player.speed)
        if keys[pygame.K_s]:
            player.move(dy=player.speed)
    
    if keys[pygame.K_ESCAPE]:
        running = False

    # Update game logic
    player.update()
    game_state.update()
    
    if game_state.state == "combat" and game_state.enemy_manager:
        game_state.enemy_manager.update_enemies()
        
        # Check for collisions with enemy attacks
        if game_state.enemy_manager.check_attack_collisions(player.x, player.y, player.width, player.height):
            if player.take_damage(10):  # Player takes 10 damage
                print(f"Player hit! Health: {player.health}")
                
                if player.health <= 0:
                    dialog_create("Tut", "Oh no! You've been defeated...", 3)
                    # Could implement game over or restart here
                    player.health = 100  # Reset health for now

    # Render everything
    if current_background:
        screen.blit(current_background, (0, 0))
    else:
        screen.fill(WHITE)
    
    if player_needed:
        player.draw()
    
    # Draw enemies if in combat
    if game_state.state == "combat" and game_state.enemy_manager:
        game_state.enemy_manager.draw_enemies(screen)
        
        # Draw player health
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f"HP: {player.health}/100", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))
        
        # Draw score
        score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 35))
    
    pygame.display.flip()
    
    update_tkinter()
    
    clock.tick(60)

pygame.quit()
sys.exit()
