import sys, os, dlib, cv2, glob
import numpy as np

input_folder = "./pho/" # where face will be retrieved from.
output_folder = "./pho2/" # where to save images.
input_image = "current_merged.isomap.png" # image to use as template.
scale = 4 # Try to get as much detail from image as possible. Downsizing final results is better than upsizing.

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def get_image(image_name):
    return cv2.imread(image_name)

def get_triangles(image, points):
    size = image.shape
    rect = (0, 0, size[1], size[0])
    
    subdiv = cv2.Subdiv2D(rect);

    for point in points:
        subdiv.insert(point)
    
    triangles = []
    tris = subdiv.getTriangleList()
    for tri in tris:
        p = [
            (int(tri[0]), int(tri[1])),
            (int(tri[2]), int(tri[3])),
            (int(tri[4]), int(tri[5]))
        ]
        
        inBounds = True
        for i in range(0, 3):
            if(p[i][0] >= rect[2] or p[i][1] >= rect[3] or p[i][0] <= 0 or p[i][1] <= 0):
                inBounds = False
        
        if inBounds == True:
            # Get indexes.
            p[0] = points.index(p[0])
            p[1] = points.index(p[1])
            p[2] = points.index(p[2])
            triangles.append(p)
    
    return triangles

def get_points(image):
    dets = detector(image, 1)
    shape = predictor(image, dets[0])
    
    points = []
    for i in range(0, shape.num_parts):
        points.append((shape.part(i).x, shape.part(i).y))
    
    return points

mi = get_image(input_image)
height, width, channels = mi.shape
mp = get_points(mi)
triangles = get_triangles(mi, mp)

# Output
for i in range(0, len(mp)):
    mp[i] = [mp[i][0] * scale, mp[i][1] * scale]

files = glob.glob(os.path.join(input_folder, "*.jpg"))
for i in range(0, len(files)):
    img = get_image(files[i])
    ip = get_points(img)

    img2 = 255 * np.ones((height * scale, width * scale, 3), dtype = mi.dtype)
    
    for tri in triangles:
        # Triangle from to triangle to.
        tri1 = np.float32([[ip[tri[0]], ip[tri[1]], ip[tri[2]]]])
        tri2 = np.float32([[mp[tri[0]], mp[tri[1]], mp[tri[2]]]])        
        
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
        imgCropped = img[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
        
        # Given a pair of triangles, find the affine transform.
        warpMat = cv2.getAffineTransform( np.float32(tri1Cropped), np.float32(tri2Cropped) )
        
        # Apply the Affine Transform just found to the src image
        img2Cropped = cv2.warpAffine( imgCropped, warpMat, (r2[2], r2[3]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

        # Get mask by filling triangle
        mask = np.zeros((r2[3], r2[2], 3), dtype = np.float32)
        cv2.fillConvexPoly(mask, np.int32(tri2Cropped), (1.0, 1.0, 1.0), 16, 0);
        
        # Apply mask to cropped region
        img2Cropped = img2Cropped * mask
        
        # Copy triangular region of the rectangular patch to the output image
        img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * ( (1.0, 1.0, 1.0) - mask )
             
        img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] + img2Cropped
        
    cv2.imwrite(output_folder + "img_{0}.png".format(i), img2)
    print("{0}/{1}".format(i+1, len(files)))
