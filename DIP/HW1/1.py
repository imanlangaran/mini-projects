import cv2

def convert_grayscale_to_8uint(image):
  """Converts a grayscale image to 8uint format.

  Args:
    image: The grayscale image to convert.

  Returns:
    The converted image in 8uint format.
  """

  # Convert the image to uint8 format.
  image = image.astype("uint8")

  # Scale the image to the range [0, 255].
  image = image * 255

  return image

def main():
  # Load the image.
  image = cv2.imread("HW1\cameraman.jpg", cv2.IMREAD_GRAYSCALE)

  # Convert the image to 8uint format.
  image = convert_grayscale_to_8uint(image)

  # Display the image.
  cv2.imshow("Image", image)
  cv2.waitKey(0)

if __name__ == "__main__":
  main()
