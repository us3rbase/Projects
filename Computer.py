import tkinter as tk

xp_notification_window = None

def create_xp_notification(message="Input Message Here", duration=10):
    global xp_notification_window

    # Check if a notification is already open.
    if xp_notification_window is not None and xp_notification_window.winfo_exists():
        return

    # If no main root exists, create one and hide it.
    if not tk._default_root:
        root_master = tk.Tk()
        root_master.withdraw()  # Hide the main window
    # Create a Toplevel window for the notification.
    root = tk.Toplevel()
    xp_notification_window = root

    root.title("Computer")
    root.configure(bg="#ece9d8")
    root.resizable(False, False)
    root.overrideredirect(True)

    title_colour = "#316AC5"

    title_bar = tk.Frame(root, bg=title_colour, height=24)
    title_bar.pack(fill=tk.X, side=tk.TOP)

    title_label = tk.Label(title_bar, text="Computer", bg=title_colour, fg="white", font=("Tahoma", 9, "bold"))
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

    def auto_resize():
        message_label.update_idletasks()
        width = message_label.winfo_reqwidth() + 40
        height = message_label.winfo_reqheight() + 60
        root.geometry(f"{width}x{height}+100+100")

    auto_resize()

    # Auto-close the window after `duration` seconds.
    root.after(duration * 1000, root.destroy)

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

