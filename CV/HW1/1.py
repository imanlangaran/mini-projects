import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import os


image = cv.imread(os.path.join(os.getcwd(), "./1.jpg"), cv.IMREAD_GRAYSCALE)
image[image < 125] = 0
image[image >= 125] = 255
inv_image = cv.bitwise_not(image)

def get45(img):
    k45 = (1/3)*np.array([[0,0,1],
                          [0,1,0],
                          [1,0,0]])
    ret = cv.filter2D(img,-1,k45)
    ret[ret<255] = 0
    
    return ret
    
def get135(img):
    k135 = (1/3)*np.array([[1,0,0],
                           [0,1,0],
                           [0,0,1]])
    ret = cv.filter2D(img,-1,k135)
    ret[ret<255] = 0
    
    return ret

inv_image45 = get45(inv_image)
image45 = cv.bitwise_not(inv_image45)

inv_image135 = get135(inv_image)
image135 = cv.bitwise_not(inv_image135)

# plt.figure(figsize=(10,10))
plt.imshow(image45, cmap="gray"), plt.title("45 degree lines")
plt.savefig("45s.jpg")

plt.imshow(image135, cmap="gray"), plt.title("135 degree lines")
plt.savefig("135s.jpg")

plt.figure(figsize=(15, 15))
plt.subplot(221), plt.imshow(image, cmap="gray"), plt.title("original image")
plt.subplot(223), plt.imshow(image45, cmap="gray"), plt.title("45 degree lines")
plt.subplot(224), plt.imshow(image135, cmap="gray"), plt.title("135 degree lines")
plt.tight_layout()
plt.show()