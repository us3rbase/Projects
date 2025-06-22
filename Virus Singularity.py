# ITMedia Project

import pygame
import sys
import os
import time
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info
from Dialog import dialog_create, tutorial_scene, fight_1, skip_current_dialog
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
        self.health = 50
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
        self.state = "tutorial"
        self.tutorial_complete = False
        self.combat_state = "idle"
        self.last_attack_time = 0
        self.attack_cooldown = 500  # 500ms cooldown between attacks
        self.last_dialog_time = 0
        self.dialog_active = False
        self.death_timer = 0
        self.score = 0
        self.enemy_manager = EnemyManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.enemy_event_manager = None  # Initialize enemy_event_manager as None
        self.player = Player()
        self.background = pygame.image.load('background.jpg')
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fight_background = pygame.image.load('fight.jpg')
        self.fight_background = pygame.transform.scale(self.fight_background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tutorial_start_time = pygame.time.get_ticks()
        self.tutorial_duration = 15000  # 15 seconds for tutorial
        self.last_attack_window_time = 0
        self.attack_window_duration = 1000  # 1 second attack window
        self.last_attack_window_end = 0
        self.attack_window_cooldown = 2000  # 2 seconds between attack windows
        self.last_dialog_skip_time = 0
        self.dialog_skip_cooldown = 200  # 200ms cooldown between dialog skips

    def reset(self):
        """Resets the game to the initial state."""
        self.state = "tutorial"
        self.tutorial_complete = False
        self.combat_state = "idle"
        self.last_attack_time = pygame.time.get_ticks()
        self.last_attack_window_time = pygame.time.get_ticks()
        self.last_attack_window_end = pygame.time.get_ticks()
        self.tutorial_start_time = pygame.time.get_ticks()
        self.tutorial_duration = 15000
        self.last_dialog_skip_time = pygame.time.get_ticks()
        self.dialog_skip_cooldown = 200
        self.last_dialog_time = pygame.time.get_ticks()
        self.dialog_active = False
        self.death_timer = 0
        self.score = 0
        self.enemy_manager = EnemyManager(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.player = Player()
        self.player.health = 50  # Ensure player starts with full health
        reset_game_loop_variables()  # Reset main game loop variables

    def start_death_sequence(self):
        """Initiates the death sequence."""
        self.state = "death"
        self.death_timer = pygame.time.get_ticks()

    def start_transition(self, new_state, duration):
        """Placeholder for state transitions."""
        print(f"Transitioning to {new_state} in {duration} frames (not implemented)")

    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Handle dialog skipping with Tab
        if keys[pygame.K_TAB] and pygame.time.get_ticks() - self.last_dialog_skip_time > self.dialog_skip_cooldown:
            if skip_current_dialog():
                self.last_dialog_skip_time = pygame.time.get_ticks()
                self.dialog_active = False
                return

        if self.state == "tutorial":
            if keys[pygame.K_SPACE] or mouse_buttons[0]:  # Space or left click
                self.tutorial_complete = True
                self.state = "combat"
                self.combat_state = "idle"
                self.last_attack_time = pygame.time.get_ticks()
                self.last_attack_window_time = pygame.time.get_ticks()
                self.last_attack_window_end = pygame.time.get_ticks()
                self.tutorial_start_time = pygame.time.get_ticks()
                self.tutorial_duration = 15000
                self.last_dialog_skip_time = pygame.time.get_ticks()
                self.dialog_skip_cooldown = 200
                self.last_dialog_time = pygame.time.get_ticks()
                self.dialog_active = False
                self.death_timer = 0
                self.score = 0
                self.enemy_manager = EnemyManager(WINDOW_WIDTH, WINDOW_HEIGHT)
                self.player = Player()
                return

        if self.state == "combat":
            # Handle player attack with Space or left click
            current_time = pygame.time.get_ticks()
            if (keys[pygame.K_SPACE] or mouse_buttons[0]) and current_time - self.last_attack_time > self.attack_cooldown:
                if self.combat_state == "attack_window":
                    self.player.attack()
                    self.last_attack_time = current_time
                    # Check for enemy hit
                    for enemy in self.enemy_manager.enemies:
                        if enemy.is_active and self.player.attack_rect.colliderect(enemy.rect):
                            enemy.take_damage(10)
                            if not enemy.is_active:  # If enemy is defeated
                                self.score += 100
                                self.enemy_manager.enemies.remove(enemy)
                                if not self.enemy_manager.enemies:  # If all enemies are defeated
                                    self.state = "boss_fight"
                                    self.combat_state = "idle"
                                    self.last_attack_time = current_time
                                    self.last_attack_window_time = current_time
                                    self.last_attack_window_end = current_time
                                    self.tutorial_start_time = current_time
                                    self.tutorial_duration = 15000
                                    self.last_dialog_skip_time = current_time
                                    self.dialog_skip_cooldown = 200
                                    self.last_dialog_time = current_time
                                    self.dialog_active = False
                                    self.death_timer = 0
                                    self.score = 0
                                    self.enemy_manager = EnemyManager(WINDOW_WIDTH, WINDOW_HEIGHT)
                                    self.player = Player()
                                    return

        elif self.state == "boss_fight":
            # Handle player attack with Space or left click
            current_time = pygame.time.get_ticks()
            if (keys[pygame.K_SPACE] or mouse_buttons[0]) and current_time - self.last_attack_time > self.attack_cooldown:
                if self.combat_state == "attack_window":
                    self.player.attack()
                    self.last_attack_time = current_time
                    # Check for boss hit
                    for enemy in self.enemy_manager.enemies:
                        if enemy.is_active and self.player.attack_rect.colliderect(enemy.rect):
                            enemy.take_damage(10)
                            if not enemy.is_active:  # If boss is defeated
                                self.score += 500
                                self.enemy_manager.enemies.remove(enemy)
                                self.state = "victory"
                                return

        elif self.state == "death":
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                self.reset()
                return

    def update(self):
        """Update game state logic each frame."""
        if self.state == "death" and self.death_timer > 0:
            if pygame.time.get_ticks() - self.death_timer > 5000:  # 5 seconds
                self.reset()
                return  # Avoid processing input during reset

        # You can add per-frame logic here if needed, or leave it as a placeholder for now.
        # For now, just call handle_input to process input each frame.
        self.handle_input()

def reset_game_loop_variables():
    """Reset the main game loop variables for a fresh start"""
    global fight_started, enemy_spawn_timer, boss_spawn_timer, start_fight_timer
    start_fight_timer = pygame.time.get_ticks() + 1000  # Start fight dialog 1 second after tutorial
    fight_started = False
    enemy_spawn_timer = None
    boss_spawn_timer = None
    tutorial_scene()  # Restart the tutorial dialog sequence

game_state = GameState()

clock = pygame.time.Clock()
running = True

current_background = load_fight_box()

game_state.player.x = 333
game_state.player.y = 302

pygame.time.delay(100)
window_x, window_y = get_window_position()
set_pygame_window_info(window_x, window_y, WINDOW_WIDTH, WINDOW_HEIGHT)

# Run the tutorial scene
tutorial_scene()

# Set up a timer to start the fight dialog after tutorial without freezing game
start_fight_timer = pygame.time.get_ticks() + 1000  # Start fight dialog 1 second after tutorial
fight_started = False
enemy_spawn_timer = None
boss_spawn_timer = None

while running:
    current_time = pygame.time.get_ticks()
    
    # Check if it's time to start the fight
    if not fight_started and current_time >= start_fight_timer:
        fight_1()  # This shows dialogs
        enemy_spawn_timer = current_time + 12000  # Spawn enemy 12 seconds after dialogs start
        game_state.state = "combat"
        fight_started = True
    
    # Check if it's time to spawn the enemy
    if enemy_spawn_timer and current_time >= enemy_spawn_timer:
        game_state.enemy_manager.spawn_enemy(count=1)
        game_state.enemy_manager.enemy_spawned = True
        enemy_spawn_timer = None  # Clear the timer
    
    # Check if it's time to spawn the boss
    if boss_spawn_timer and current_time >= boss_spawn_timer:
        game_state.enemy_manager.spawn_enemy(is_boss=True)
        boss_spawn_timer = None  # Clear the timer
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state.player.attack():
                    # Player attacks all enemies
                    if game_state.state == "combat":
                        defeated = game_state.enemy_manager.player_attack(25)  # Deal 25 damage
                        
                        if defeated > 0:
                            game_state.score += defeated * 100
                            print(f"Defeated {defeated} enemies! Score: {game_state.score}")
                            
                            if game_state.enemy_manager.count_active_enemies() == 0:
                                if not game_state.enemy_manager.is_boss_fight:
                                    # Start boss fight sequence
                                    boss_spawn_timer = game_state.enemy_manager.start_boss_fight()
                                else:
                                    # Boss defeated
                                    dialog_create("Tut", "Incredible! You've defeated the virus boss!", 3)
                                    game_state.start_transition("exploration", 180)
    
    keys = pygame.key.get_pressed()
    
    # Always allow player movement regardless of game state
    if keys[pygame.K_w]:
        game_state.player.move(0, -5)
    if keys[pygame.K_s]:
        game_state.player.move(0, 5)
    if keys[pygame.K_a]:
        game_state.player.move(-5, 0)
    if keys[pygame.K_d]:
        game_state.player.move(5, 0)
    
    if keys[pygame.K_ESCAPE]:
        running = False

    # Update game logic
    game_state.player.update()
    game_state.update()
    
    if game_state.state == "combat":
        # Update enemies and check for boss spawn
        game_state.enemy_manager.update_enemies()
        
        # Check for collisions with enemy attacks
        if game_state.enemy_manager.check_attack_collisions(game_state.player.x, game_state.player.y, game_state.player.width, game_state.player.height):
            if game_state.player.take_damage(10):  # Player takes 10 damage
                print(f"Player hit! Health: {game_state.player.health}")
                
                if game_state.player.health <= 0:
                    dialog_create("Tut", "Oh no! You've been defeated...", 3)
                    game_state.start_death_sequence()

    # Render everything
    if current_background:
        screen.blit(current_background, (0, 0))
    else:
        screen.fill(WHITE)
    
    # Always draw the player
    game_state.player.draw()
    
    # Draw enemies if in combat
    if game_state.state == "combat":
        game_state.enemy_manager.draw_enemies(screen)
        
    # Always draw player stats
    font = pygame.font.SysFont(None, 24)
    health_text = font.render(f"HP: {game_state.player.health}/50", True, (255, 255, 255))
    screen.blit(health_text, (10, 10))
    
    # Draw score
    score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 35))
    
    # Draw death screen
    if game_state.state == "death":
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw death message
        death_font = pygame.font.SysFont(None, 48)
        death_text = death_font.render("YOU DIED", True, (255, 0, 0))
        restart_text = font.render("Restarting in 5 seconds...", True, (255, 255, 255))
        
        screen.blit(death_text, (WINDOW_WIDTH//2 - death_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 10))
    
    pygame.display.flip()
    
    update_tkinter()
    
    clock.tick(60)

pygame.quit()
sys.exit()
