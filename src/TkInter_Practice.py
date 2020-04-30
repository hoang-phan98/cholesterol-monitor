import tkinter
from tkinter import *
from tkinter.ttk import *

window = tkinter.Tk()


def on_click():
    res = "You selected: " + combo.get()
    label.configure(text=res)
    return


# Set window title
window.title("GUI")

# Set window size
window.geometry('500x500')

# Create label
label = Label(window, text="Hello World!")
label.grid(column=0, row=0)

# Create button
bt = Button(window, text="Enter", command=on_click)
bt.grid(column=1, row=1)

# Create text box
txt = Entry(window, width=20)
txt.grid(column=0, row=1)

# Create combo box
combo = Combobox(window)
combo['values'] = ("A", "B", "C", "D")
combo.grid(column=0, row=2)

# Loop until window manually closed
window.mainloop()
