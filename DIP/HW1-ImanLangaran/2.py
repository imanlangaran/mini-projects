import cv2
import matplotlib.pyplot as plt

image = cv2.imread("DIP/HW1/cameraman.jpg", cv2.IMREAD_GRAYSCALE)


histogram = [0] * 256
for pixel in image.flatten():
    histogram[pixel] += 1

plt.figure("For Loop")
plt.plot(histogram)
plt.xlabel("Intensity")
plt.ylabel("Count")
plt.show()


histogram = cv2.calcHist([image], [0], None, [256], [0, 255])

plt.figure("Builtin Function")
plt.plot(histogram)
plt.xlabel("Intensity")
plt.ylabel("Count")
plt.show()