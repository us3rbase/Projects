# ITMedia Project

import sys
import os
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info, xp_notification_window, process_notification_queue
import pygame

def dialog_create(sender, message, duration):
    """Create a dialog message with the given sender, message, and duration"""
    create_xp_notification(sender, message, duration)
    return pygame.time.get_ticks() + (duration * 1000)  # Convert duration to milliseconds

def skip_current_dialog():
    """Skip the current dialog message"""
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        if xp_notification_window and xp_notification_window.winfo_exists():
            xp_notification_window.destroy()
            return True
    return False

def tutorial_scene():
    """Create the tutorial dialog sequence"""
    dialog_create("????", "Hello there!", 3)
    dialog_create("????", "I see you've found yourself in a computer", 3)
    dialog_create("????", "There are viruses here that need to be dealt with", 3)
    dialog_create("????", "Amazing, lets get to it then", 3)
    dialog_create("????", "My name is Tut by the way", 2)

def fight_1():
    dialog_create("Tut", "Look! There's a virus!", 3)
    dialog_create("Tut", "Move with WASD to dodge its attacks!", 3)
    dialog_create("Tut", "Press SPACE to attack when you see the red circle!", 3)
    dialog_create("Tut", "You can also use LEFT CLICK to attack!", 3)
    return pygame.time.get_ticks() + 3000  # 3 seconds after last message

def boss_fight_intro():
    dialog_create("Tut", "Great job! But...", 2)
    dialog_create("Tut", "The virus is mutating!", 2)
    dialog_create("Tut", "It's becoming something more dangerous...", 2)
    dialog_create("Tut", "Be careful! This one is different!", 2)
    return pygame.time.get_ticks() + 3000  # 3 seconds after last message
