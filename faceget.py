import sys, os, dlib, cv2, glob, filehelper
from PIL import Image
import numpy as np
from math import trunc

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
triangles = []
for line in open("triangle_list.txt", "r"):
    x, y, z = line.split('  ')
    triangles.append([int(x), int(y), int(z)])

# Bounds of face.
def get_bounds(image):
    dets = detector(image, 0)
    if len(dets) == 0 or dets[0] is None:
        return [0, 0, 0, 0]
    else:
        return [dets[0].left(), dets[0].top(), dets[0].right(), dets[0].bottom()]

# Locations of facial landmarks.
# Pass in a custom bounding box to improve search.
def get_points(image, bounds = None):
    bounds = get_bounds(image) if bounds is None else bounds

    dif_x, dif_y = 0, 0
    scale = 10
    offsets = [[-scale, -scale], [-scale, scale], [scale, scale], [scale, -scale]]
    points = []
    for i in range(0, 68):
        points.append([0.0, 0.0])

    origin_rect = dlib.rectangle(bounds[0], bounds[1], bounds[2], bounds[3])
    origin_shape = predictor(image, origin_rect)
    
    for o in offsets:
        rect = dlib.rectangle(bounds[0] + o[0], bounds[1] + o[1], bounds[2] + o[0], bounds[3] + o[1])
        shape = predictor(image, rect)
        
        for i in range(0, shape.num_parts):
            p = shape.part(i)
            points[i][0] += float(p.x) / 4
            points[i][1] += float(p.y) / 4
    
    p2 = []
    for i in range(0, 68):
        p = points[i]
        dif_x += float(p[0] - origin_shape.part(i).x) / float(68)
        dif_y += float(p[1] - origin_shape.part(i).y) / float(68)
        p2.append((int(p[0]), int(p[1])))

    print(dif_x, dif_y)
    
    return p2, bounds

# Triangles MUST be the same as template. So only template has to generate these.
def get_triangles(image, points):
    size = image.shape
    rect = (0, 0, size[1], size[0])
    
    subdiv = cv2.Subdiv2D(rect);
    
    for point in points:
        subdiv.insert(point)
    
    triangles = []
    tris = subdiv.getTriangleList()
    for tri in tris:
        p = [(int(tri[0]), int(tri[1])),
             (int(tri[2]), int(tri[3])),
             (int(tri[4]), int(tri[5]))]
        
        inBounds = True
        for i in range(0, 3):
            if(p[i][0] >= rect[2] or p[i][1] >= rect[3] or p[i][0] <= 0 or p[i][1] <= 0):
                inBounds = False
        
        if inBounds is True:
            # Get indexes.
            p[0] = points.index(p[0])
            p[1] = points.index(p[1])
            p[2] = points.index(p[2])
            triangles.append(p)
    
    return triangles

# Faces will be saved to this location.
def get_output_path(image_path, template_image_path):
    base_name = os.path.basename(template_image_path)
    extension = os.path.splitext(base_name)[-1]
    template_folder_name = base_name.split(extension)[0]
    
    filehelper.make_sure_path_exists("./output/{0}".format(template_folder_name))
    
    return "./output/{0}/{1}".format(template_folder_name, get_safe_path_string(image_path))

def save_data(image_path, points, triangles, bounds):
    cached_path = get_cached_path(image_path)
    
    data = ''
    a = []
    for p in points:
        a.append(p[0])
        a.append(p[1])
    data += ','.join(map(str, a)) + '|'
    a = []
    for t in triangles:
        a.append(t[0])
        a.append(t[1])
        a.append(t[2])
    data += ','.join(map(str, a)) + '|'
    data += "{0},{1},{2},{3}".format(bounds[0], bounds[1], bounds[2], bounds[3])
    
    file = open(cached_path, "w")
    file.write(data)
    file.close()
    
def load_data(image_path):
    image = Image.open(image_path)
    
    cached_path = get_cached_path(image_path)
    points = []
    triangles = []
    bounds = []
    
    file = open(cached_path, "r")
    for line in file:
        pp, tt, bb = line.split('|')
        pp = pp.split(',')
        tt = tt.split(',')
        bb = bb.split(',')
        for p in list(zip(pp[::2],pp[1::2])): points.append([int(p[0]), int(p[1])])
        for t in list(zip(tt[::3],tt[1::3],tt[2::3])): triangles.append([int(t[0]), int(t[1]), int(t[2])])
        bounds = [int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3])]
        break
        '''parts = line.split('  ')
        if len(parts) == 2: points.append([int(parts[0]), int(parts[1])])
        elif len(parts) == 3: triangles.append([int(parts[0]), int(parts[1]), int(parts[2])])
        else: bounds = [int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])]
        '''
    file.close()
    
    return points, triangles, bounds

def generate_data(image_path, new_bounds = None):
    image_rgb = cv2.imread(image_path)
    points, bounds = get_points(image_rgb, new_bounds)
    triangles = get_triangles(image_rgb, points)
    return points, triangles, bounds
    
# To save processing time, store face landmark data to a directory.
def get_cached_path(image_path):
    # Create directory if it doesn't already exist.
    filehelper.make_sure_path_exists("./cache/")
    # 
    safe_name = '___'.join(image_path.split('/'))
    safe_name = '___'.join(safe_name.split('//'))
    safe_name = '___'.join(safe_name.split('\\'))
    safe_name = '___'.join(safe_name.split('\\\\'))
    return "./cache/{0}.pts".format(safe_name)

def get_data(image_path):
    image = Image.open(image_path).convert("RGBA")
    
    # Try to load points and triangles.
    if os.path.isfile(get_cached_path(image_path)):
        points, triangles, bounds = load_data(image_path)
    else:
        points, triangles, bounds = generate_data(image_path)
        save_data(image_path, points, triangles, bounds)
    
    return image, points, triangles, bounds

def get_points_bounds(points):
    x_min, y_min, x_max, y_max = 999999, 999999, -999999, -999999
    for p in points:
        x, y = p
        if x < x_min: x_min = x
        if y < y_min: y_min = y
        if x > x_max: x_max = x
        if y > y_max: y_max = y
    w = x_max - x_min
    h = y_max - y_min
    return -x_min + 10, -y_min + 10, w + 20, h + 20

def get_aligned_face(template_path = '', scale = 1, progress_bar = None, status_bar = None, template_points = None):
    
    images_list = filehelper.get_path_list("./photos/", filehelper.IMAGE_EXTENSIONS)
    step = trunc(100/len(images_list))
    x, y = 0, 0
    
    if template_path != '':
        t_folders, t_name, t_extension = filehelper.get_path_parts(template_path)
        t_image, t_points, t_triangles, t_bounds = get_data(template_path)
        t_image = np.array(t_image)
        height, width, channels = t_image.shape
    
    if template_points is not None:
        t_points = template_points
        t_triangles = triangles
        t_name = 'Average'
        x, y, width, height = get_points_bounds(template_points)
        print("DIMENSIONS")
        print(x, y, width, height)
    
    # Scale target points.
    mp = []
    for i in range(0, len(t_points)):
        mp.append([(t_points[i][0] + x) * scale, (t_points[i][1] + y) * scale])
    t_points = mp
    
    # Final texture.
    img2 = np.zeros((height * scale, width * scale, 4), dtype = 'uint8')

    i = 0
    for image_path in images_list:
        folders, name, extension = filehelper.get_path_parts(image_path)
        
        # Tell gui which image is being processed.
        if status_bar != None:
            status_bar.config(text="processing {0} of {1} - {2}".format(i+1, len(images_list), name))
            status_bar.update_idletasks()
        
        # Load image and it's face points.
        i_image, i_points, NOT_USED, i_bounds = get_data(image_path)
        i_image = np.array(i_image)
        print(i_image.dtype)
        
        # Transfer face triangles.
        for tri in t_triangles:
            # Triangle from to triangle to.
            tri1 = np.float32([[i_points[tri[0]], i_points[tri[1]], i_points[tri[2]]]])
            tri2 = np.float32([[t_points[tri[0]], t_points[tri[1]], t_points[tri[2]]]])        
            
            # Find bounding box. 
            r1 = cv2.boundingRect(tri1)
            r2 = cv2.boundingRect(tri2)
            
            # Offset points by left top corner of the 
            # respective rectangles
            tri1Cropped = []
            tri2Cropped = []
            
            for j in range(0, 3):
              tri1Cropped.append(((tri1[0][j][0] - r1[0]),(tri1[0][j][1] - r1[1])))
              tri2Cropped.append(((tri2[0][j][0] - r2[0]),(tri2[0][j][1] - r2[1])))
            
            # Apply warpImage to small rectangular patches
            imgCropped = i_image[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
            
            # Given a pair of triangles, find the affine transform.
            warpMat = cv2.getAffineTransform(np.float32(tri1Cropped), np.float32(tri2Cropped))
            
            # Apply the Affine Transform just found to the src image
            img2Cropped = cv2.warpAffine(imgCropped, warpMat, (r2[2], r2[3]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            
            # Get mask by filling triangle
            mask = np.zeros((r2[3], r2[2], 4), dtype = np.float32)
            cv2.fillConvexPoly(mask, np.int32(tri2Cropped), (1.0, 1.0, 1.0, 1.0), 16, 0);
            
            # Apply mask to cropped region
            img2Cropped = img2Cropped * mask
            
            # Copy triangular region of the rectangular patch to the output image
            img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ((1.0, 1.0, 1.0, 1.0) - mask)
            img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Cropped
        
        # Save image to destination. (PNG to preserve transparency.)
        save_path = "./output/{0}/{1}{2}".format(t_name, name, ".png")
        filehelper.make_sure_path_exists(save_path)
        final_image = Image.fromarray(img2)
        final_image.save(save_path)
        print(save_path)
        
        # Update progress bar.
        if progress_bar != None:
            progress_bar.step(step)
            progress_bar.update()
        
        i += 1
    
    return images_list
