from PIL import Image
import numpy as np
from skimage.measure import shannon_entropy

def discretize_image(image, step):
    width, height = image.size
    new_size = (width // step, height // step)
    discretized_image = image.resize(new_size, Image.NEAREST)
    return discretized_image

def quantize_image(image, level):
    data = np.array(image)
    step = 256 / level
    quantized_data = (data // step * step + step / 2).clip(0, 255).astype(np.uint8)
    quantized_image = Image.fromarray(quantized_data)
    return quantized_image

def restore_image(image, level, method):
    width, height = image.size
    original_size = (width * level, height * level)
    restored_image = image.resize(original_size, getattr(Image, method.upper()))
    return restored_image


images_list = []
STEPS_LIST = [2, 4]
LEVELS_LIST = [8, 16, 64]
METHODS_LIST = ["nearest", "bilinear", "bicubic"]

image = Image.open("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\image.jpg").convert('L')
images_list.append(image)
print("Task 1 - Image is converted to grayscale")
print("Task 2 - Entropy of image is", round(shannon_entropy(image), 2))
for step in STEPS_LIST:
    d_image = discretize_image(image, step)
    images_list.append(d_image)
    d_image.save("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\discretized images\\image_" + str(step) + ".jpg")
print("Task 3 - Image is discreted with steps 2 and 4")
img_l_len = len(images_list)
for i in range(img_l_len):
    for level in LEVELS_LIST:
        q_image = quantize_image(images_list[i], level)
        images_list.append(q_image)
        q_image.save("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\quantized images\\image_" + str(i+1) + "_" + str(level) + ".jpg")
print("Task 4 - Images are quantized with levels 8, 16 and 64")
print("Task 5 - Entropyies of discretized and quantized images are:")
for i in range(1, len(images_list)):
    print("Entropy of image №" + str(i), round(shannon_entropy(images_list[i]), 2))
step = 0
for i in range(1, 3):
    for method in METHODS_LIST:
        restored_image = restore_image(images_list[i], STEPS_LIST[step], method)
        images_list.append(restored_image)
        restored_image.save("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\restored images\\image_" + str(i + 1) + "_" + method + ".jpg")
    step += 1