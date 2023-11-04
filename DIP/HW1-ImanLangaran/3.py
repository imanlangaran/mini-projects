import cv2
import matplotlib.pyplot as plt
import numpy as np


image = cv2.imread("DIP/HW1/cameraman.jpg",
                   cv2.IMREAD_GRAYSCALE)

histogram = cv2.calcHist(
    [image], [0], None, [256], [0, 255])

cumulative_histogram = np.cumsum(histogram)
equalized_image = cv2.LUT(image, cumulative_histogram)
equalized_histogram = cv2.calcHist(
    [equalized_image], [0], None, [256], [0, 255])

plt.figure("Histogram")
plt.plot(histogram)
plt.xlabel("Intensity")
plt.ylabel("Count")

plt.figure('Equalized Histogram')
plt.plot(equalized_histogram)
plt.xlabel("Intensity")
plt.ylabel("Count")

plt.show()