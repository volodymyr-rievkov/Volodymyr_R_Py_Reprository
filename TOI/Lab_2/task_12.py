from PIL import Image
import numpy as np
from skimage.measure import shannon_entropy
from collections import Counter

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

def restore_image(image, step, method):
    width, height = image.size
    original_size = (width * step, height * step)
    restored_image = image.resize(original_size, getattr(Image, method.upper()))
    return restored_image

def calculate_relative_entropy(image1, image2):
    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())
    histogram1 = Counter(pixels1)
    histogram2 = Counter(pixels2)
    total_pixels1 = len(pixels1)
    total_pixels2 = len(pixels2)
    probability1 = {key: count / total_pixels1 for key, count in histogram1.items()}
    probability2 = {key: count / total_pixels2 for key, count in histogram2.items()}
    relative_entropy = 0
    for key in probability1:
        p = probability1[key]
        q = probability2.get(key, 0) 
        if p > 0 and q > 0:
            relative_entropy += p * np.log2(p / q)
    return abs(relative_entropy)

images_list = dict()
STEPS_LIST = [2, 4]
LEVELS_LIST = [8, 16, 64]
METHODS_LIST = ["nearest", "bilinear", "bicubic"]

#Task-1
sample_image = Image.open("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\image.jpg").convert('L')
images_list["S"] = []
images_list["S"].append(sample_image)
#Task-2
print("Sample image entropy:", round(shannon_entropy(images_list["S"]), 2))
#Task-3
images_list["D"] = []
for step in STEPS_LIST:
    discret_image = discretize_image(images_list["S"][0], step)
    discret_image.save("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\discretized images\\image_" + "D" + "_" + str(step) + ".jpg")
    images_list["D"].append(discret_image)
#Task-4
quant_images = []
i = 1
for level in LEVELS_LIST:
    for key in images_list.keys():
        for image in images_list[key]:
            quant_image = quantize_image(image, level)
            quant_image.save("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\quantized images\\image_" + "Q" + "_" + str(i) + "_" + str(level) + ".jpg")
            quant_images.append(quant_image)
            i += 1
images_list["Q"] = quant_images
#Task-5
for k in images_list.keys():
    if(k != "S"):
        for image in images_list[k]:
            print(k + " image entropy:", round(shannon_entropy(image), 2))
#Task-6
images_list["R"] = []
step = STEPS_LIST[0]
for image in images_list["D"]:
    for method in METHODS_LIST:
        rest_image = restore_image(image, step, method)
        rest_image.save("D:\\Programming\\PythonApplications\\TOI\\Lab_2\\restored images\\image_" + method + "_" + str(step) + ".jpg")
        images_list["R"].append(rest_image)
    step = STEPS_LIST[1]
#Task-7
for key in images_list.keys():
    if(key != "S"):
        for image in images_list[key]:
            print(key + " image relative entropy:", round(calculate_relative_entropy(sample_image, image), 6))
