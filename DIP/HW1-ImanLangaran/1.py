import cv2

image = cv2.imread("DIP/HW1/cameraman.jpg")

print(image.dtype)
# output : uint8
# with opencv, all the images i've tried are in uint8 format!

cv2.imshow("Image", image)
cv2.waitKey(0)