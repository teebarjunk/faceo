import sys, os, glob, cv2
from tkinter import *
from tkinter import ttk
#from PIL import Image, ImageTk, ImageDraw
from gui import GUI_Landmarks, GUI_Composite, GUI_List_Photos, GUI_List_Composite
import faceget, filehelper

template_path = "./photos/Putin.jpg"
photos_list = []

root = Tk()
image_scale = (800, 600)

def menu(option):
    print(option)

# Menu bar.
menubar = Menu(root)
root.config(menu=menubar)    
for key, value in [("File","New,Open,Save,Save as,Exit"),("Edit","Preferences"),("Help","Help,About")]:
    submenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label=key, menu=submenu)
    for option in value.split(','):
        submenu.add_command(label=option, command=lambda o=option:menu(o))

# Status bar.
status_bar = Label(root, text="", bd=1, relief=SUNKEN, anchor=W)
status_bar.pack(side=BOTTOM, fill=X)

def set_status(text, *args):
    status_bar.config(text=text % args)
    status_bar.update_idletasks()

# Progress bar.
progress_bar = ttk.Progressbar(status_bar, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(side=RIGHT)

def set_progress(value, max_value):
    progress_bar["maximum"] = max_value
    progress_bar["value"] = value

# Tabs.
nb = ttk.Notebook(root)
page_template = Frame(nb)
page_images = Frame(nb)
page_composite = Frame(nb)
nb.add(page_template, text='Template')
nb.add(page_images, text='Images')
nb.add(page_composite, text='Composite')
nb.pack(expand=1, fill=BOTH)

# Template Frame.
template = GUI_Landmarks(page_template)
template.set_path(template_path)

Button(page_template, text="...", command=template.set_path).grid(row=0, column=0, sticky=E+W)
Button(page_template, text="Save", command=template.save).grid(row=0, column=1, sticky=E+W)

def on_select_input(event):
    global image
    
    w = event.widget
    
    if len(w.curselection()) > 0:
        index = int(w.curselection()[0])
        value = "./photos/" + w.get(index)
        image.set_image(value)

# Images Frame.
m = PanedWindow(page_images, orient=HORIZONTAL)
m.pack(fill=BOTH, expand=1)
left = Frame(m)
right = Frame(m)
m.add(left)
m.add(right)

def process_image_list():
    faceget.get_aligned_face(template.path, 1, progress_bar, status_bar)

Button(left, text="Go", command=process_image_list).pack(fill=X)

image_listbox = GUI_List_Photos(left, './photos/')
image = GUI_Landmarks(right)
image_listbox.image = image
#image.set_path(template_path)

# Composite Frame.
m = PanedWindow(page_composite, orient=HORIZONTAL)
m.pack(fill=BOTH, expand=1)
left = Frame(m)
right = Frame(m)
m.add(left)
m.add(right)

v = IntVar()
v.set(1)
Radiobutton(left, text="Template", variable=v, value=1).pack(anchor=W)
Radiobutton(left, text="Average", variable=v, value=2).pack(anchor=W)

image_listbox = GUI_List_Composite(left, './output/Putin/')
composite = GUI_Composite(right)
image_listbox.image = composite
#composite.set_path()
