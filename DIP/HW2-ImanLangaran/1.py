import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.util import random_noise
from skimage.metrics import peak_signal_noise_ratio
from skimage.util import img_as_ubyte
import os


image = img_as_ubyte(imread(os.path.join(os.getcwd(),"../cameraman.jpg"), as_gray=True))

gaussian_image = img_as_ubyte(random_noise(image, mode='gaussian', seed=1, var=0.05, mean=0))
sp_image = img_as_ubyte(random_noise(image, mode="s&p", amount=0.1, salt_vs_pepper=0.5))

g_PSNR = peak_signal_noise_ratio(image_true=image, image_test=gaussian_image)
sp_PSNR = peak_signal_noise_ratio(image_true=image, image_test=sp_image)

print(f"Gaussian PSNR:{g_PSNR:.2f} , Salt & Pepper PSNR:{sp_PSNR:.2f}")


plt.figure(figsize=(15,7))

plt.subplot(131), plt.imshow(image, cmap='gray'), plt.title('Origin')
plt.subplot(132), plt.imshow(gaussian_image, cmap='gray'), plt.title('Gaussian')
plt.subplot(133), plt.imshow(sp_image, cmap='gray'), plt.title('Salt & Pepper')

plt.savefig("1-result.jpg")

plt.show()