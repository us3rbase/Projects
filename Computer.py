import tkinter as tk
import queue

notification_queue = queue.Queue()
xp_notification_window = None
pygame_window_info = {"x": 0, "y": 0, "width": 0, "height": 0}
pending_notifications = []

def set_pygame_window_info(x, y, width, height):
    global pygame_window_info
    pygame_window_info = {"x": x, "y": y, "width": width, "height": height}

def process_notification_queue():
    try:
        while not notification_queue.empty():
            sender, message, duration = notification_queue.get_nowait()
            pending_notifications.append((sender, message, duration))
    except Exception as e:
        print(f"Error processing notification: {e}")
    
    check_pending_notifications()
    
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        process_notification_queue.root.after(100, process_notification_queue)

def check_pending_notifications():
    global xp_notification_window
    if (xp_notification_window is None or not xp_notification_window.winfo_exists()) and pending_notifications:
        next_sender, next_message, next_duration = pending_notifications.pop(0)
        _create_xp_notification_internal(next_sender, next_message, next_duration)

def initialize_tkinter():
    if not hasattr(process_notification_queue, "root"):
        root = tk.Tk()
        root.withdraw()
        process_notification_queue.root = root
        root.after(100, process_notification_queue)

def update_tkinter():
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        process_notification_queue.root.update()

def create_xp_notification(sender, message="Input Message Here", duration=10):
    notification_queue.put((sender, message, duration))

def _create_xp_notification_internal(sender="Test", message="Input Message Here", duration=10):
    global xp_notification_window

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
        command=root.destroy
    )
    help_button.pack(side=tk.RIGHT, padx=5)

    content = tk.Frame(root, bg="#ece9d8", bd=1, relief="solid")
    content.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))

    message_label = tk.Label(content, text=message, bg="#ece9d8", font=("Tahoma", 9), justify="left", wraplength=280)
    message_label.pack(padx=15, pady=15)

    root.update_idletasks()
    
    def position_notification():
        width = root.winfo_width()
        height = root.winfo_height()
        
        if width < 100:
            width = message_label.winfo_reqwidth() + 40
            height = message_label.winfo_reqheight() + 60
        
        x = pygame_window_info["x"] + (pygame_window_info["width"] - width) // 2
        y = pygame_window_info["y"] + pygame_window_info["height"] + 5
        
        x = max(0, x)
        y = max(0, y)
        
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        root.deiconify()
        
        print(f"Notification position: {x}, {y}, size: {width}x{height}")
        print(f"Pygame window: {pygame_window_info}")

    message_label.update_idletasks()
    width = message_label.winfo_reqwidth() + 40
    height = message_label.winfo_reqheight() + 60
    root.geometry(f"{width}x{height}")
    
    root.after(50, position_notification)

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
    if hasattr(process_notification_queue, "root") and process_notification_queue.root.winfo_exists():
        process_notification_queue.root.after(200, check_pending_notifications)
