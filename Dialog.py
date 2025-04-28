# ITMedia Project

import sys
import os
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info

def dialog_create(sender, message="", delay=1):
    create_xp_notification(sender, message, delay)

        
def tutorial_scene():
    dialog_create("????", "Hello! Welcome to the computer!", 3)
    dialog_create("????", "Are you the one they sent to save us?", 4)
    dialog_create("????", "The Anti-Virus has been non stop detecting viruses and nothing being done!", 4.5)
