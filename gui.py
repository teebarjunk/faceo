import composite, faceget, filehelper
import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

class GUI_List:
    def __init__(self, parent, selectmode, path):
        self.image_paths = []
        self.path = path
        self.image = None
        
        self.scrollbar = Scrollbar(parent)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(parent, yscrollcommand=self.scrollbar.set, selectmode=selectmode)
        self.listbox.pack(side=LEFT, fill=BOTH)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.scrollbar.config(command=self.listbox.yview)
        
        self.update()

    def update(self):
        self.listbox.delete(0, END)
        self.image_paths = filehelper.get_path_list(self.path, filehelper.IMAGE_EXTENSIONS, True)
        
        for path in self.image_paths:
            self.listbox.insert(END, path[1])
    
    def on_select(self, event):
        print('')

class GUI_List_Photos(GUI_List):
    def __init__(self, parent, path):
        GUI_List.__init__(self, parent, SINGLE, path)

    def on_select(self, event):
        w = event.widget
        i = w.curselection()[0]
        self.image.set_path(self.image_paths[i])


'''
List of images that get blended together when selected.
'''
class GUI_List_Composite(GUI_List):
    def __init__(self, parent, path):
        GUI_List.__init__(self, parent, MULTIPLE, path)
        self.points = []
        self.selected = []
        self.selected_paths = []

    def average_points(self):
        '''
        self.points = []
        for i in range(0, 68):
            self.points.append([0,0])
        
        for path in self.selected:
            points, a, b = faceget.load_data('./photos/' + path[1]+'.jpg')
            for i in range(0, 68):
                self.points[i][0] += points[i][0]
                self.points[i][1] += points[i][1]
        
        for i in range(0, 68):
            self.points[i][0] = round(float(self.points[i][0]) / float(len(self.selected)))
            self.points[i][1] = round(float(self.points[i][1]) / float(len(self.selected)))

        faceget.get_aligned_face('', template_points = self.points)
        print(self.points)
        '''
    
    def on_select(self, event):
        w = event.widget
        
        if len(w.curselection()) > 0:
            self.selected = []
            self.selected_paths = []
            
            for i in w.curselection():
                self.selected.append(self.image_paths[i])
                self.selected_paths.append(self.image_paths[i][0])
            
            self.image.set_list(self.selected_paths)
        
        self.average_points()

'''
Base image class.
'''
class GUI_Image:
    def __init__(self, parent):
        self.image = None
        self.canvas = Canvas(parent, width=800, height=600)
        self.canvas.grid(row=1, columnspan=4)
        self.drawn = []
        self.scale = [1,1]
    
    def update_image(self, image):
        # Resize
        w, h = float(image.size[0]), float(image.size[1])
        image.thumbnail((800, 600), Image.ANTIALIAS)
        self.scale = (float(image.size[0]) / w, float(image.size[1]) / h)
        self.image = ImageTk.PhotoImage(image)
        
        # Add to canvas.
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)

        # Rerender debug data.
        self.draw_debug()
    
    # Render debug data. (Bounds, triangles, points...)
    def draw_debug(self):
        # Clear old overlay.
        while(len(self.drawn) > 0):
            self.canvas.delete(self.drawn.pop())

'''
Renders composite images.
'''
class GUI_Composite(GUI_Image):
    def __init__(self, parent):
        GUI_Image.__init__(self, parent)

        self.image_paths = []
    
    def set_list(self, image_paths):
        self.image_paths = image_paths
        image = Image.fromarray(composite.from_list(image_paths))
        self.update_image(image)
        
    def save(self, path):
        return True


'''
Renders unmodified images and their points/triangles.
'''
class GUI_Landmarks(GUI_Image):
    def __init__(self, parent):
        GUI_Image.__init__(self, parent)

        self.parent = parent
        self.path = ""
        self.points = []
        self.triangles = []
        self.bounds = [0, 0, 0, 0]

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
    def draw_debug(self):
        GUI_Image.draw_debug(self)
        
        # Draw triangles.
        if len(self.points) != 0:
            for triangle in self.triangles:
                t1, t2, t3 = self.points[triangle[0]], self.points[triangle[1]], self.points[triangle[2]]
                self.drawn.append(self.canvas.create_line([t1[0] * self.scale[0], t1[1] * self.scale[1], t2[0] * self.scale[0], t2[1] * self.scale[1]], fill='white'))
                self.drawn.append(self.canvas.create_line([t2[0] * self.scale[0], t2[1] * self.scale[1], t3[0] * self.scale[0], t3[1] * self.scale[1]], fill='white'))
                self.drawn.append(self.canvas.create_line([t3[0] * self.scale[0], t3[1] * self.scale[1], t1[0] * self.scale[0], t1[1] * self.scale[1]], fill='white'))
        
        # Draw points.
        for point in self.points:
            self.drawn.append(self.canvas.create_oval([point[0] * self.scale[0]-1, point[1] * self.scale[1]-1, point[0] * self.scale[0]+1, point[1] * self.scale[1]+1], outline='blue'))
        
        # Draw boundary.
        self.drawn.append(self.canvas.create_rectangle(self.bounds[0] * self.scale[0], self.bounds[1] * self.scale[1], self.bounds[2] * self.scale[0], self.bounds[3] * self.scale[1], outline='red'))
    
    # Gets image, looks for cached landmark data, generates if it doesn't exist.
    def update_data(self, new_bounds = None):
        self.bounds = new_bounds
        self.points, self.triangles, self.bounds = faceget.generate_data(self.path, new_bounds)
        self.draw_debug()
    
    def save(self):
        faceget.save_data(self.path, self.points, self.triangles, self.bounds)
    
    # Set path to image.
    def set_path(self, path = ''):
        if path == '':
            p, e = filehelper.ask_for_directory(self.parent)

            if p + e != '':
                path = p + e
        
        if path != '':
            print(path)
            self.path = path
            image, self.points, self.triangles, self.bounds = faceget.get_data(self.path)
            self.update_image(Image.open(self.path))
            self.draw_debug()
    
    # Mouse selection.
    def on_mouse_down(self, event):
        self.bounds[0], self.bounds[1] = int(event.x / self.scale[0]), int(event.y / self.scale[1])
    
    def on_mouse_move(self, event):
        self.bounds[2], self.bounds[3] = int(event.x / self.scale[0]), int(event.y / self.scale[1])
        self.draw_debug()
    
    def on_mouse_up(self, event):
        self.update_data(self.bounds)
        self.draw_debug()

