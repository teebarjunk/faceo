import os, glob
from tkinter import filedialog

IMAGE_EXTENSIONS = ("*.jpg", "*.png")
IMAGE_FILETYPE = ('image files', ['.jpg', '.png'])

local_path = os.path.dirname(os.path.realpath(__file__))

'''
def set_images_directory(as_input):
    global listbox, btn_input, btn_output, progress_bar
    global input_path, output_path
    
    options = {}
    options['initialdir'] = local_path
    options['mustexist'] = True
    options['parent'] = root
    
    if as_input:
        input_path = filedialog.askdirectory(**options, title="Set input path")
    else:
        output_path = filedialog.askdirectory(**options, title="Set output path")
        # Ask to process all images.
        if messagebox.askyesno("Print", "Process {0} images from '{1}' to '{2}' using '{3}' template?".format(len(output_list), input_path.split('/')[-1], output_path.split('/')[-1], template.path.split('/')[-1])):
            images_list = facePose.get_aligned_face(template.path, input_path, output_path, 4, progress_bar, status_bar)
            set_status("Done processing.")
        else:
            print("OK :(")
    
    update_output_list(as_input)
'''

# request a directory from the user
def ask_for_directory(root, local_path = '.', file_type = IMAGE_FILETYPE):
    options = {}
    options['defaultextension'] = file_type[1][0]
    options['filetypes'] = [file_type]
    options['initialdir'] = local_path
    options['parent'] = root
    
    file_name, file_extension = os.path.splitext(filedialog.askopenfilename(**options))
    
    return file_name, file_extension

# returns: array of folder names, file name, extension
def get_path_parts(path):
    base_name = os.path.basename(path)
    
    if base_name != '':
        extension = os.path.splitext(base_name)[-1]
        file_name = base_name.split(extension)[0]
        folders = path.split(file_name)[0].split('/')
        return folders, file_name, extension
    else:
        return path.split('/'), '', ''

# checks if a local path exists and creates subfolders if they don't
def make_sure_path_exists(path):
    folders, file_name, extension = get_path_parts(path)
    path = './' + '/'.join(folders) + '/'
    
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# returns an array of file paths from the requested folder
def get_path_list(folder, extensions, short=False):
    path_list = []
    
    for extension in extensions:
        path_list.extend(glob.glob(os.path.join(folder, extension)))
    
    # a list that includes path AND name and extension seperatly
    if short:
        pl = []
        for path in path_list:
            folders, name, extension = get_path_parts(path)
            pl.append((path, name, extension))
        path_list = pl
            
    return path_list
