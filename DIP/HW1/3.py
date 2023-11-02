import cv2
import matplotlib.pyplot as plt
import numpy as np

def equalize_histogram(image):
  """Equalizes the histogram of an image.

  Args:
    image: The image to equalize the histogram of.

  Returns:
    The equalized image.
  """

  # Calculate the cumulative histogram.
  histogram = cv2.calcHist([image], [0], None, [256], [0, 255])
  cumulative_histogram = np.cumsum(histogram)

  # Calculate the equalized image.
  equalized_image = cv2.LUT(image, cumulative_histogram)

  return equalized_image

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
  

def main():
  # Load the image.
  image = cv2.imread("HW1\cameraman.jpg", cv2.IMREAD_GRAYSCALE)

  # Draw the original histogram.
  draw_histogram(image)

  # Apply histogram equalization.
  equalized_image = equalize_histogram(image)

  # Draw the equalized histogram.
  draw_histogram(equalized_image)
  plt.show()

if __name__ == "__main__":
  main()
