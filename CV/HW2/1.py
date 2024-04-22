
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
import os

image = cv.imread(os.path.join(os.getcwd(), "./1.png"), cv.IMREAD_COLOR)


image = cv.medianBlur(image, 5)
gimage = cv.cvtColor(image,cv.COLOR_BGR2GRAY)

circles = cv.HoughCircles(gimage, cv.HOUGH_GRADIENT, 1, 20, param1=50, param2= 30, minRadius=0, maxRadius=0)

circles = np.uint16(np.around(circles))

t = 0
clr = (t,t,t)
for i in circles[0,:]:
    cv.circle(image, (i[0],i[1]), i[2]+2, clr, -1)

plt.imshow(image), plt.title("e")


dst = cv.Canny(image, 100, 200, None, 3)

for d in range(1,180):
    linesP = cv.HoughLinesP(dst, 5, d*(np.pi / 180),20)
    
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        cv.line(image, (l[0], l[1]), (l[2], l[3]), (255,255,255), 1, cv.LINE_AA)

plt.imshow(image), plt.title("e")
