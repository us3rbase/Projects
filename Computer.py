import tkinter as tk
import queue

# Queue for communication between threads
notification_queue = queue.Queue()
xp_notification_window = None
pygame_window_info = {"x": 0, "y": 0, "width": 0, "height": 0}
pending_notifications = []  # Queue to store pending notifications

def set_pygame_window_info(x, y, width, height):
    """Set the pygame window position and size to position notifications"""
    global pygame_window_info
    pygame_window_info = {"x": x, "y": y, "width": width, "height": height}

def process_notification_queue():
    """Process notifications from the queue on the main tkinter thread"""
    try:
        while not notification_queue.empty():
            sender, message, duration = notification_queue.get_nowait()
            # Add to pending notifications instead of displaying immediately
            pending_notifications.append((sender, message, duration))
    except Exception as e:
        print(f"Error processing notification: {e}")
    
    # Check if we need to display a notification
    check_pending_notifications()
    
    # Schedule the next queue check
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        process_notification_queue.root.after(100, process_notification_queue)

def check_pending_notifications():
    """Check if there are pending notifications to display"""
    global xp_notification_window
    
    # If there's no active notification and we have pending ones, show the next one
    if (xp_notification_window is None or not xp_notification_window.winfo_exists()) and pending_notifications:
        next_sender, next_message, next_duration = pending_notifications.pop(0)
        _create_xp_notification_internal(next_sender, next_message, next_duration)

def initialize_tkinter():
    """Initialize tkinter in the main thread"""
    if not hasattr(process_notification_queue, "root"):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        process_notification_queue.root = root
        
        # Start the queue processing
        root.after(100, process_notification_queue)

def update_tkinter():
    """Update the tkinter event loop - call this from pygame main loop"""
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        process_notification_queue.root.update()

def create_xp_notification(sender, message="Input Message Here", duration=10):
    """Queue a notification to be displayed by the tkinter thread"""
    notification_queue.put((sender, message, duration))

def _create_xp_notification_internal(sender="Test", message="Input Message Here", duration=10):
    """Internal function to create the notification window"""
    global xp_notification_window

    # Create a Toplevel window for the notification
    root = tk.Toplevel(process_notification_queue.root)
    xp_notification_window = root

    root.withdraw()    

    root.title("Dialog")
    root.configure(bg="#ece9d8")
    root.resizable(False, False)
    root.overrideredirect(True)

    title_colour = "#000084"

    title_bar = tk.Frame(root, bg=title_colour, height=24)
    title_bar.pack(fill=tk.X, side=tk.TOP)

    title_label = tk.Label(title_bar, text=sender, bg=title_colour, fg="white", font=("Tahoma", 9, "bold"))
    title_label.pack(side=tk.LEFT, padx=5)

    help_button = tk.Button(
        title_bar,
        text="?",
        bg=title_colour,
        fg="white",
        font=("Tahoma", 9, "bold"),
        bd=0,
        activebackground=title_colour,
        activeforeground="white",
        command=root.destroy  # Closes the window when clicked
    )
    help_button.pack(side=tk.RIGHT, padx=5)

    content = tk.Frame(root, bg="#ece9d8", bd=1, relief="solid")
    content.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))

    message_label = tk.Label(content, text=message, bg="#ece9d8", font=("Tahoma", 9), justify="left", wraplength=280)
    message_label.pack(padx=15, pady=15)

    # First update to get correct size
    root.update_idletasks()
    
    def position_notification():
        # Get the notification window size
        width = root.winfo_width()
        height = root.winfo_height()
        
        if width < 100:  # If width is too small, it hasn't been properly measured yet
            width = message_label.winfo_reqwidth() + 40
            height = message_label.winfo_reqheight() + 60
        
        # Calculate position to center directly under the pygame window
        x = pygame_window_info["x"] + (pygame_window_info["width"] - width) // 2
        y = pygame_window_info["y"] + pygame_window_info["height"] + 5  # 5px padding below pygame window
        
        # Ensure positive coordinates
        x = max(0, x)
        y = max(0, y)
        
        # Set the window geometry with explicit size and position
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make the window visible only after positioning
        root.deiconify()
        
        # Print debug info
        print(f"Notification position: {x}, {y}, size: {width}x{height}")
        print(f"Pygame window: {pygame_window_info}")

    # Set a default size first
    message_label.update_idletasks()
    width = message_label.winfo_reqwidth() + 40
    height = message_label.winfo_reqheight() + 60
    root.geometry(f"{width}x{height}")
    
    # Then position it correctly after a short delay to ensure size calculations are complete
    root.after(50, position_notification)

    # Auto-close the window after `duration` seconds
    root.after(duration * 1000, lambda: on_notification_closed(root))

    def start_move(event):
        root.x = event.x
        root.y = event.y

    def do_move(event):
        x = event.x_root - root.x
        y = event.y_root - root.y
        root.geometry(f"+{x}+{y}")

    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)

    def on_destroy(event):
        global xp_notification_window
        xp_notification_window = None

    root.bind("<Destroy>", on_destroy)

def on_notification_closed(window):
    """Handle notification closure and display next notification if available"""
    window.destroy()
    # Check for pending notifications after a short delay
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        process_notification_queue.root.after(200, check_pending_notifications)
