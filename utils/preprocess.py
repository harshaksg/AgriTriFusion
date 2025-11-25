from PIL import Image
import numpy as np

def preprocess_image_pil(image, size=(224,224)):
    image = image.convert('RGB').resize(size)
    arr = np.array(image).astype('float32') / 255.0
    return arr

def quality_check(image, min_size=(100,100)):
    return image.size[0] >= min_size[0] and image.size[1] >= min_size[1]
