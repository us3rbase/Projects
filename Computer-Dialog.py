from tkinter import *

running = True

root = Tk()
root.geometry('302x125+800+800')
root.overrideredirect(True) 

#Define Image
bg = PhotoImage(file="computer-dialog.jpg")

#Create Label
label = Label(root, image=bg)
label.place(x=0, y=0, relwidth=1, relheight=1)

dialog = Label(root, text="This is a Test Dialog Box!", font=("Tahoma", 13), bg="#ece8d8")
dialog.pack(pady=50, padx=30)

while running:
    root.mainloop()