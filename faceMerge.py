import sys, os, cv2, glob
import numpy as np
import math

input_folder = "./pho2/"
output_folder = "./pho3/"
scale = 4
enhance = True

img2 = 255 * np.ones((512 * scale, 512 * scale, 3), dtype = np.uint8)
files = glob.glob(os.path.join("./pho2/", "*.png"))

for i in range(0, len(files)):
    img1 = cv2.imread(files[i])

    if i == 0:
        img2 = cv2.addWeighted(img2, 0, img1, 1, 0)
    else:
        div = (1/(len(files)+2))*2
        img2 = cv2.addWeighted(img2, 1-div, img1, div, 0)
    
    name = "./pho3/img_{0}.png".format(i)
    cv2.imwrite(name, img2)
    print("{0}/{1}".format(i+1, len(files)))

if enhance:
    from wand.image import Image

    with Image(filename=output_folder + "img_{0}.png".format(i)) as img:
        # Enhance color levels.
        img.level(0.05, 0.95, gamma=1)
        
        # Sharpen image.
        img.unsharp_mask(radius=12.0, sigma=10.0, amount=1, threshold=0.0)
        img.save(filename=output_folder + "enhanced.png")
        print("enhanced")
