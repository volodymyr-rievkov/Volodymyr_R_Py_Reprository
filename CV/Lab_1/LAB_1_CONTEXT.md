# Context: Image Processing using AI Methods - Laboratory Work 1
**Topic:** Image Preprocessing

## ⚠️ CRITICAL CONSTRAINTS (MANDATORY)
1. **NO EXTERNAL LIBRARIES FOR PROCESSING:** Third-party image processing libraries (such as OpenCV, PIL/Pillow, scikit-image, etc.) **MUST NOT** be used for algorithmic implementation. 
2. **ALLOWED USAGE:** Libraries (like OpenCV or Matplotlib) are permitted **EXCLUSIVELY** for reading images from disk, displaying them on the screen, and saving them. 
3. **PENALTY:** Using external libraries for the core logic will result in a maximum grade of 1 point.
4. **ALLOWED LANGUAGES:** Python, C++, Java, C#, Matlab. (Assume Python with `numpy` as the standard array manipulation tool unless specified otherwise).

## Task Assignment Logic
The specific task is determined by the student's sequence number in the group roster.
* Formula: `Variant = Student_Number mod 15` (If the number is $\le 15$, the variant is the number itself. If the result of modulo is 0, assume variant 15).
* **Base Requirement for all tasks:** Select two images with different levels of object detail and two images with different contrast levels from the internet. Apply the assigned algorithm and perform a comparative analysis of the results.

## List of Variants (Tasks)
1. Implement 1D linear filtering with different $K$ and $L$ values.
2. Implement 2D linear filtering with different kernel values.
3. Implement Box-filtering with different kernel sizes.
4. Implement Median filtering with different kernel sizes.
5. Implement Gaussian filtering with different blur kernel parameters.
6. Implement Histogram Shift to the left.
7. Implement Histogram Shift to the right.
8. Implement Histogram Contrast increase.
9. Implement Histogram Contrast decrease.
10. Implement Histogram Gamma increase.
11. Implement Histogram Gamma decrease.
12. Implement Edge Detection using **Roberts** and **Sobel** operators.
13. Implement Edge Detection using **Sobel** and **Prewitt** operators.
14. Implement Edge Detection using the **Canny** operator.
15. Implement Edge Detection using **Kirsch** and **Laplacian** operators.

*Additional Bonus Task (Optional):* Choose one morphological image processing method and implement it from scratch without external libraries.

## Theoretical Background & Mathematical Foundations

### 1. 1D Linear Filtering (Point Operation)
Applies a scalar transformation to every pixel independently:
$$g(i,j) = K \times f(i,j) + L$$
Where $f(i,j)$ is the input pixel intensity, $g(i,j)$ is the output, $K$ controls contrast, and $L$ controls brightness. Ensure output values are clipped to $[0, 255]$.

### 2. 2D Linear Filtering (Convolution)
Requires applying a kernel (matrix) over the image using a sliding window. 
* Boundary handling (Padding) is required (e.g., zero-padding, edge mirroring, or constant value padding).

#### Box Filter Kernel (Example $3 \times 3$)
$$H = \frac{1}{9}\begin{bmatrix} 1 & 1 & 1 \\ 1 & 1 & 1 \\ 1 & 1 & 1 \end{bmatrix}$$

#### Gaussian Filter
Calculates weights based on the Gaussian function:
$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

### 3. Edge Detection Kernels
Calculated by convolving the image with specific matrices to approximate derivatives.

**Roberts Operator:**
$$G_x = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}, \quad G_y = \begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix}$$

**Sobel Operator:**
$$G_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad G_y = \begin{bmatrix} 1 & 2 & 1 \\ 0 & 0 & 0 \\ -1 & -2 & -1 \end{bmatrix}$$

**Prewitt Operator:**
$$G_x = \begin{bmatrix} -1 & 0 & 1 \\ -1 & 0 & 1 \\ -1 & 0 & 1 \end{bmatrix}, \quad G_y = \begin{bmatrix} 1 & 1 & 1 \\ 0 & 0 & 0 \\ -1 & -1 & -1 \end{bmatrix}$$

**Laplacian Operator (Example):**
$$L_1 = \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix} \quad \text{or} \quad L_2 = \begin{bmatrix} 1 & 1 & 1 \\ 1 & -8 & 1 \\ 1 & 1 & 1 \end{bmatrix}$$

### 4. Non-Linear Filtering (Median)
For a given window (e.g., $3 \times 3$), collect all pixel values, sort them, and replace the central pixel with the median value. Excellent for "salt and pepper" noise reduction.

## Agent Instructions for Code Generation
When prompted to solve a specific variant:
1. Define the core algorithm purely using standard array/math operations (e.g., nested loops or matrix vectorization via `numpy` in Python).
2. Manually implement convolution operations, padding, and histogram calculations.
3. Keep the code modular (separate functions for padding, convolution, specific filters).
4. Use `matplotlib` or `cv2.imshow` solely for comparing the `Input Image` vs `Processed Image`.
```eof