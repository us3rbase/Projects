import tkinter as tk
import time



def create_xp_notification(message="Input Message Here", duration = 10):
    start_time = time.time()
    root = tk.Tk()
    root.title("Computer")
    root.configure(bg="#ece9d8")  # Beige XP background
    root.resizable(False, False)
    root.overrideredirect(True)

    # === Title Bar ===
    title_colour = "#316AC5"  # Closer to real XP blue

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
        command=root.destroy  # <-- this closes the window
    )

    help_button.pack(side=tk.RIGHT, padx=5)

    # === Content Area ===
    content = tk.Frame(root, bg="#ece9d8", bd=1, relief="solid")
    content.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))

    message_label = tk.Label(content, text=message, bg="#ece9d8", font=("Tahoma", 9), justify="left", wraplength=280)
    message_label.pack(padx=15, pady=15)

    # Resize window based on text content
    def auto_resize():
        message_label.update_idletasks()
        width = message_label.winfo_reqwidth() + 40
        height = message_label.winfo_reqheight() + 60
        root.geometry(f"{width}x{height}+100+100")

    auto_resize()
    #root.after(duration * 1000, root.destroy)

    # === Allow dragging the window ===
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def do_move(event):
        x = event.x_root - root.x
        y = event.y_root - root.y
        root.geometry(f"+{x}+{y}")

    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)


    root.mainloop()


# Example usage:
create_xp_notification("hey gusy i got this working! it took me 2 hours 😭")
