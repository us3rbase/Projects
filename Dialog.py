# ITMedia Project

import sys
import os
from Computer import initialize_tkinter, create_xp_notification, update_tkinter, set_pygame_window_info

def dialog_create(sender, message="", delay=1):
    create_xp_notification(sender, message, delay)

        
def tutorial_scene():
    dialog_create("????", "Hello! Welcome to the computer!", 3)
    dialog_create("????", "Are you the one they sent to save us?", 4)
    dialog_create("????", "The Anti-Virus has been non stop detecting viruses and nothing being done!", 4)
    dialog_create("????", "We need you to take them down!", 2)
    dialog_create("????", "Are you up to the task?", 2)
    dialog_create("Player", "I'll do what I can", 2)
    dialog_create("????", "Amazing, lets get to it then", 3)
    dialog_create("????", "My name is Tut by the way", 2)
    #Fade to Black

#def fight_1():
    #dialog_create("Tut", "Look theres one!", 2)
    #dialog_create("Tut", "Go get it", 1)
