import numpy as np
import matplotlib.pyplot as plt

def read_x_y_from_file(file_name):
    with open(file_name, 'r') as file:
        x_str = file.readline().split()
        y_str = file.readline().split()
    x = [float(x_value) for x_value in x_str]
    y = [float(y_value) for y_value in y_str]
    
    return x, y

def create_normal_equation_matrix(x, m):
    matrix = np.zeros((m + 1, m + 1))  
    
    for i in range(m + 1):
        for j in range(m + 1):
            matrix[i][j] = sum(x_value ** (i + j) for x_value in x)
    return matrix

def create_vector(x, y, m):
    vector = np.zeros(m + 1)

    for i in range(m + 1):
        vector[i] = sum((x ** i) * y for x, y in zip(x, y))
    return vector

def gaussian_elimination(matrix, vector):
    n = len(vector)
    augmented_matrix = np.hstack((matrix, vector.reshape(-1, 1)))
    for i in range(n):
        max_row = max(range(i, n), key=lambda r: abs(augmented_matrix[r][i]))
        augmented_matrix[[i, max_row]] = augmented_matrix[[max_row, i]]  
        
        for j in range(i + 1, n):
            factor = augmented_matrix[j][i] / augmented_matrix[i][i]
            augmented_matrix[j, i:] -= factor * augmented_matrix[i, i:]
    
    solution = np.zeros(n)
    for i in range(n - 1, -1, -1):
        solution[i] = (augmented_matrix[i, -1] - np.dot(augmented_matrix[i, i+1:n], solution[i+1:])) / augmented_matrix[i, i]
    
    return solution

def print_coeffs(coeffs):
    print("Coefficient:")
    for i in range(len(coeffs)):
        print(f"a{i}: {round(coeffs[i], 3)}")

def polynomial_approximation(x, y, tolerance):
    m = 2  

    while True:
        matrix = create_normal_equation_matrix(x, m)
        vector = create_vector(x, y, m)
        coeffs = gaussian_elimination(matrix, vector)
        def polynomial(x_value):
            result = coeffs[0]
            for i in range(1, m + 1):
                result += coeffs[i] * x_value ** i
            return result

        approximated_y = [polynomial(x_value) for x_value in x]
        max_error = max(abs(y_real - y_approx) for y_real, y_approx in zip(y, approximated_y))
        
        if max_error < tolerance:
            polynomial_str = f"{round(coeffs[0], 3)}"
            for i in range(1, len(coeffs)):
                polynomial_str += f" + {round(coeffs[i], 3)} * x^{i}"
            print("Polynomial approximation:")
            print(polynomial_str)
            return polynomial
        m += 1
        
def plot_points_and_polynomial(x, y, polynomial):
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(x, y, color='red', zorder=5)
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.7)  
    plt.axvline(0, color='black', linewidth=0.5, linestyle='--', alpha=0.7)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Current Points Plot')
    plt.grid(alpha=0.5)
    
    x_values = np.linspace(min(x), max(x), 1000)
    y_values = np.vectorize(polynomial)(x_values)
    plt.subplot(1, 2, 2)
    plt.plot(x_values, y_values, color='blue')
    plt.axhline(0, color='blue', linewidth=1)
    plt.axvline(0, color='blue', linewidth=1)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title("Polynomial Approximation")

    plt.tight_layout()
    plt.show()

FILE_NAME = "D:\\Studing\\Чисельні методи\\Лабораторна робота №6\\lab_6_1.txt"
TOLERANCE = 1e-10
x, y = read_x_y_from_file(FILE_NAME)
polynomial = polynomial_approximation(x, y, TOLERANCE)
plot_points_and_polynomial(x, y, polynomial)
