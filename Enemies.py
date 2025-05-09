import pygame
import sys
import os
import random
import math
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info
from Dialog import dialog_create

class Attack:
    def __init__(self, x, y, speed=3, pattern="linear"):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 15
        self.speed = speed
        self.pattern = pattern
        self.is_active = True
        self.start_x = x
        self.start_time = pygame.time.get_ticks()
        self.color = (255, 0, 0)  # White attack projectile
        
    def update(self):
        """Update attack position based on pattern"""
        if self.pattern == "linear":
            self.y += self.speed
        elif self.pattern == "sine":
            time_elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
            self.x = self.start_x + math.sin(time_elapsed * 5) * 50
            self.y += self.speed
        elif self.pattern == "zigzag":
            time_elapsed = (pygame.time.get_ticks() - self.start_time) / 200.0
            offset = 30 if int(time_elapsed) % 2 == 0 else -30
            self.x += offset * 0.1
            self.y += self.speed
            
        # Check if attack is off screen
        if self.y > 500:  # Just beyond screen height
            self.is_active = False
            
    def draw(self, screen):
        """Draw the attack"""
        if not self.is_active:
            return
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, width=60, height=60):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = 100
        self.is_active = True
        self.attack_timer = 0
        self.attack_cooldown = 90  # Frames between attacks (1.5 seconds at 60fps)
        self.attacks = []
        self.attack_patterns = ["linear", "sine", "zigzag"]
        
        # Try to load the enemy image, fallback to a colored rectangle
        self.use_image = True
        try:
            self.image = pygame.image.load('virus.jpg')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except pygame.error:
            print("Could not load virus image. Using colored square instead.")
            self.use_image = False
            self.color = (255, 0, 255)  # Purple color for viruses
    
    def draw(self, screen):
        if not self.is_active:
            return
            
        if self.use_image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
        # Draw health bar
        health_bar_width = self.width
        health_bar_height = 5
        health_percentage = max(0, self.health / 100.0)
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.x, self.y - 10, health_bar_width, health_bar_height))
        # Foreground (green)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x, self.y - 10, int(health_bar_width * health_percentage), health_bar_height))
    
    def update(self):
        """Update enemy state and create attacks"""
        if not self.is_active:
            return
            
        # Update attack timer
        self.attack_timer += 1
        if self.attack_timer >= self.attack_cooldown:
            self.attack_timer = 0
            self.create_attack()
            
        # Update existing attacks
        for attack in self.attacks[:]:
            attack.update()
            if not attack.is_active:
                self.attacks.remove(attack)
    
    def create_attack(self):
        """Create a new attack"""
        # Create 1-3 attacks in a pattern
        attack_count = random.randint(1, 3)
        pattern = random.choice(self.attack_patterns)
        
        for i in range(attack_count):
            # Spawn attack from enemy position
            offset_x = random.randint(-20, 20)
            attack_x = self.x + self.width/2 - 7 + offset_x  # Center of enemy + small random offset
            attack_y = self.y + self.height
            
            # Create attack with random pattern
            self.attacks.append(Attack(attack_x, attack_y, pattern=pattern))
    
    def draw_attacks(self, screen):
        """Draw all active attacks"""
        for attack in self.attacks:
            attack.draw(screen)
    
    def take_damage(self, amount):
        """Reduce enemy health by the given amount"""
        self.health -= amount
        if self.health <= 0:
            self.is_active = False
            return True  # Enemy is defeated
        return False  # Enemy is still active

class EnemyManager:
    def __init__(self, screen_width, screen_height):
        self.enemies = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fight_box_top = 227     # Top of the fight box area
        self.fight_box_bottom = 393  # Bottom of the fight box area (456 - 63)
        self.fight_box_left = 205    # Left of the fight box area
        self.fight_box_right = 496   # Right of the fight box area (697 - 201)
        self.enemy_spawn_y = 120     # Y position for enemies (above the fight box)
    
    def spawn_enemy(self, count=1):
        """Spawn a specified number of enemies positioned above the fight box"""
        
        # Calculate the center of the screen
        center_x = self.screen_width / 2
        
        if count == 1:
            # For a single enemy, center it
            x = center_x - 30  # Half of enemy width (60)
            y = self.enemy_spawn_y
            self.enemies.append(Enemy(x, y))
        else:
            # For multiple enemies, space them evenly
            total_width = count * 60 + (count - 1) * 20  # enemies * width + spaces between
            start_x = center_x - total_width / 2
            
            for i in range(count):
                x = start_x + i * (60 + 20)
                y = self.enemy_spawn_y
                self.enemies.append(Enemy(x, y))
    
    def draw_enemies(self, screen):
        """Draw all active enemies and their attacks"""
        for enemy in self.enemies:
            enemy.draw(screen)
            enemy.draw_attacks(screen)
    
    def update_enemies(self):
        """Update all enemies"""
        for enemy in self.enemies:
            if enemy.is_active:
                enemy.update()
    
    def check_attack_collisions(self, player_x, player_y, player_width, player_height):
        """Check if any enemy attack collides with the player"""
        for enemy in self.enemies:
            for attack in enemy.attacks:
                if not attack.is_active:
                    continue
                    
                # Simple rectangle collision detection
                if (player_x < attack.x + attack.width and
                    player_x + player_width > attack.x and
                    player_y < attack.y + attack.height and
                    player_y + player_height > attack.y):
                    attack.is_active = False  # Remove the attack
                    return True  # Collision detected
        return False  # No collision
    
    def player_attack(self, damage=10):
        """Player attacks and damages all active enemies"""
        defeated_count = 0
        for enemy in self.enemies:
            if enemy.is_active:
                if enemy.take_damage(damage):
                    defeated_count += 1
        
        return defeated_count
    
    def count_active_enemies(self):
        """Count how many active enemies are remaining"""
        return sum(1 for enemy in self.enemies if enemy.is_active)
    
    def clear_enemies(self):
        """Remove all enemies"""
        self.enemies.clear()

def start_fight_scene():
    """Start a fight scene with enemies"""
    dialog_create("Tut", "Look! There's a virus!", 3)
    dialog_create("Tut", "Move with WASD to dodge its attacks!", 3)
    dialog_create("Tut", "Press SPACE to attack it when your attack is ready!", 2)
    
    # Return a timestamp that marks when the enemy should actually spawn
    # This timestamp will be approximately when the first dialog appears
    return pygame.time.get_ticks() + 100  # Spawn almost immediately after dialog starts
