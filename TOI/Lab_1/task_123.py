from PIL import Image
from collections import Counter
from skimage.measure import shannon_entropy
import matplotlib.pyplot as plt
import math

def calculate_entropy(image):
    image = image.convert('L')
    pixels = list(image.getdata())
    histogram = Counter(pixels)
    total_pixels = len(pixels)
    entropy = 0
    for count in histogram.values():
        probability = count / total_pixels
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy

def print_histogram_and_etropy(image):
    image = image.convert('L')
    pixels = list(image.getdata())
    histogram = Counter(pixels)
    pixel_values = list(histogram.keys())
    frequencies = list(histogram.values())
    plt.figure(figsize = (10, 5))
    plt.bar(pixel_values, frequencies, width=1.0, color='black')
    plt.title('Image Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.text(0.5, 0.95, "Manual Entropy: " + str(round(calculate_entropy(image), 2)), 
             fontsize=12, color='black', ha='right', va='top', 
             transform=plt.gca().transAxes)
    plt.text(0.5, 0.90, "Built-in Entropy: " + str(round(shannon_entropy(image), 2)), 
             fontsize=12, color='black', ha='right', va='top', 
             transform=plt.gca().transAxes)
    plt.show()

image = Image.open('D:/Programming/PythonApplications/TOI/Lab_1/image_1.bmp')
print_histogram_and_etropy(image)
image = Image.open('D:/Programming/PythonApplications/TOI/Lab_1/image_2.png')
print_histogram_and_etropy(image)
image = Image.open('D:/Programming/PythonApplications/TOI/Lab_1/image_3.jpg')
print_histogram_and_etropy(image)
