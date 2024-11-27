import matplotlib.pyplot as plt
import numpy as np

def read_x_y_from_file(file_name):
    with open(file_name, 'r') as file:
        x_str = file.readline().split()
        y_str = file.readline().split()
    x = [float(x_value) for x_value in x_str]
    y = [float(y_value) for y_value in y_str]
    
    return x, y

def lagrange_polynomial(x, y):
    n = len(x)

    polynomial_str = ""
    for i in range(n):
        term = f"{y[i]}"
        for j in range(n):
            if j != i:
                term += f" * (x - {x[j]}) / ({x[i]} - {x[j]})"
        polynomial_str += f"({term}) + " if (i != n-1) else f"({term})"
    print(f"Lagrange polynomial: {polynomial_str}")
                
    def L(x_val, i):
        L = 1
        for j in range(n):
            if(j != i):
                L *= ((x_val - x[j]) / (x[i] - x[j]))
        return L

    def polinomial(x_val):
        result = 0
        for i in range(n):
            result += y[i] * L(x_val, i)
        return result
  
    return polinomial

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
    y_values = np.array([polynomial(x_val) for x_val in x_values])
    plt.subplot(1, 2, 2)
    plt.plot(x_values, y_values, color='blue')
    plt.axhline(0, color='blue', linewidth=1)
    plt.axvline(0, color='blue', linewidth=1)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title("Lagrange Polynomial")

    plt.tight_layout()
    plt.show()

FILE_NAME = "D:\\Studing\\Чисельні методи\\Розрахункова робота\\task_4.txt"
x, y = read_x_y_from_file(FILE_NAME)
polynomial = lagrange_polynomial(x, y)
plot_points_and_polynomial(x, y, polynomial)
