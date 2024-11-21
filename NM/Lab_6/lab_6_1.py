import matplotlib.pyplot as plt
import numpy as np

def read_x_y_from_file(file_name):
    with open(file_name, 'r') as file:
        x_str = file.readline().split()
        y_str = file.readline().split()
    x = [float(x_value) for x_value in x_str]
    y = [float(y_value) for y_value in y_str]
    
    return x, y

def calc_coeffs(x, y):
    n = len(x)
    table = list()
    for i in range(n):
        table.append([0] * n)
        table[i][0] = y[i]
    for i in range(1, n):
        for j in range(n - i):
            table[j][i] = (table[j + 1][i - 1] - table[j][i - 1]) / (x[i + j] - x[j])
    return [table[0][i] for i in range(n)]

def print_coeffs(coeffs):
    print("Coefficient:")
    for i in range(len(coeffs)):
        print(f"a{i}: {round(coeffs[i], 3)}")

def newton_polynomial(x, y):
    coeffs = calc_coeffs(x, y)  
    print_coeffs(coeffs)
    polynomial_str = f"{round(coeffs[0], 3)}"
    term = ""
    for i in range(1, len(x)):
        term += f"(x - {x[i-1]})"  
        polynomial_str += f" + {round(coeffs[i], 3)} * {term}"
    print("Newton Polynomial:")
    print(polynomial_str)
    def polynomial(x_val):
        result = coeffs[0]
        term = 1
        for i in range(1, len(x)):
            term *= (x_val - x[i-1])  
            result += coeffs[i] * term  
        return result
    return polynomial

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
    plt.title("Newton Polynomial")

    plt.tight_layout()
    plt.show()

def check_equal_distance(x):
    diffs = np.diff(x)  
    if np.allclose(diffs, diffs[0]):  
        return True
    else:
        return False

FILE_NAME = "D:\\Studing\\Чисельні методи\\Лабораторна робота №6\\lab_6_1.txt"
x, y = read_x_y_from_file(FILE_NAME)
if(check_equal_distance(x)):
    polinomial = newton_polynomial(x, y)
    print("y:", polinomial(20.5))
    plot_points_and_polynomial(x, y, polinomial)
else:
    print("Error: Distances between x are not equal.")

