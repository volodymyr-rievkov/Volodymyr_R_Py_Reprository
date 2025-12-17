import cv2
from cmath import pi

def load_and_preprocess(file_path):
    image = cv2.imread(file_path)
    if image is None:
        return None

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.medianBlur(gray_image, 5)
    _, binary_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel, iterations=2)

    return binary_image
    
def count_shapes_on_image(binary_image):
    stats = {"quads": 0, "circles": 0}

    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return stats
    
    hierarchy = hierarchy[0]

    for i, contour in enumerate(contours):
        depth = 0
        current_parent = hierarchy[i][3]

        while current_parent != -1:
            depth += 1
            current_parent = hierarchy[current_parent][3]

        if depth % 2 != 0: 
            continue

        contour_area = cv2.contourArea(contour)
        if contour_area < 40: 
            continue

        contour_perimeter = cv2.arcLength(contour, True)
        epsilon = 0.03 * contour_perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True) 
        vertices = len(approx)

        if vertices > 4:
            circularity = 4 * pi * contour_area / contour_perimeter**2
            if circularity > 0.8:
                stats['circles'] += 1

        elif vertices == 4:
            stats['quads'] += 1

    return stats

def main():
    TEST_PATH = 'D:/Programming/PythonApplications/BoAI/Lab_4/test_images'
    file_path = f'{TEST_PATH}/test_11.png'

    binary_image = load_and_preprocess(file_path)

    if binary_image is not None:
        results = count_shapes_on_image(binary_image)
        print(results)
    else:
        print(f"Error loading file: {file_path}")

if __name__ == "__main__":
    main()
    