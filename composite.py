'''
Layers a list of images.
They must all be the same size.

TODO: Add more options.
'''

import cv2
import numpy as np
from PIL import Image
from wand.image import Image as imImage

def from_list(file_list, save_path = '', levels = False, sharpen = False):
    total = len(file_list)
    s = np.array(Image.open(file_list[0]).convert('RGBA'))
    final_image = np.zeros((s.shape[0], s.shape[1], 4), dtype = s.dtype)
    amount = 1.0/float(total)

    print(amount)
    
    for i in range(0, total):
        img = np.array(Image.open(file_list[i]).convert('RGBA'))
        final_image = cv2.addWeighted(final_image, 1, img, amount, 0)
    
    # ImageMagik effects.
    if levels or sharpen:
        enhanced = imImage.fromarray(final_image)
        
        # Enhance color levels.
        if levels: img.level(0.05, 0.95, gamma=1)
        
        # Sharpen image.
        if sharpen: img.unsharp_mask(radius=12.0, sigma=10.0, amount=1, threshold=0.0)

        # Back to numpy.
        final_image = np.array(enhanced)
    
    # Save image.
    if save_path != '':
        saved_image = Image.fromarray(final_image)
        saved_image.save(save_path)
    
    return final_image
