'''
import cv2
import matplotlib.pyplot as plt

def draw_histogram(image):
  """Draws the histogram of an image.

  Args:
    image: The image to draw the histogram of.

  Returns:
    None.
  """

  # Calculate the histogram.
  histogram = [0] * 256
  for pixel in image.flatten():
    histogram[pixel] += 1

  # Plot the histogram.
  plt.figure(figsize=(10, 5))
  plt.plot(histogram)
  plt.xlabel("Intensity")
  plt.ylabel("Count")
  plt.show()

def main():
  # Load the image.
  image = cv2.imread("HW1\cameraman.jpg", cv2.IMREAD_GRAYSCALE)

  # Draw the histogram.
  draw_histogram(image)

if __name__ == "__main__":
  main()
'''




'''
import cv2
import matplotlib.pyplot as plt

def draw_histogram(image):
  """Draws the histogram of an image.

  Args:
    image: The image to draw the histogram of.

  Returns:
    None.
  """

  # Calculate the histogram.
  histogram = cv2.calcHist([image], [0], None, [256], [0, 255])

  # Plot the histogram.
  plt.figure(figsize=(10, 5))
  plt.plot(histogram)
  plt.xlabel("Intensity")
  plt.ylabel("Count")
  plt.show()

def main():
  # Load the image.
  image = cv2.imread("HW1\cameraman.jpg", cv2.IMREAD_GRAYSCALE)

  # Draw the histogram.
  draw_histogram(image)

if __name__ == "__main__":
  main()
'''
