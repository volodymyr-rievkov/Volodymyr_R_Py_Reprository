from sympy import symbols, diff, lambdify
import numpy as np
import matplotlib.pyplot as plt

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        equation = file.readline().strip() 
        roots = [] 
        for root in file:  
            roots.append(float(root.strip()))
    return equation, roots  

def print_roots(roots):
    print("Roots:")
    i = 1
    for root in roots:
        print(f"X{i}: {root}")
    print()

def print_graph(func):
    x_values = np.linspace(-10, 10, 1000)
    y_values  = np.vectorize(func)(x_values)

    plt.ion()
    plt.plot(x_values, y_values)
    plt.axhline(0, color='black',linewidth=1)  
    plt.axvline(0, color='black',linewidth=1)  

    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.title('Graph of f(x)')
    plt.show()

def read_intervals(func):
    while(True):
        print("Please input intervlas due to graph")
        a = float(input("a: "))
        b = float(input("b: "))
        if(func(a) * func(b) < 0):
            return a, b
        else:
            print("Error: Statement 'f(a) * f(b) < 0' is incorrect.")

def get_derivative(equation):

    x = symbols('x')
    f_prime = diff(equation, x)
    return f_prime

def chord_method(equation, x, f, a, b, tolerance):
    iterations = 0
    f_prime = get_derivative(equation)
    f_double_prime = get_derivative(f_prime)
    f_prime = lambdify(x, f_prime, modules=['sympy']) 
    f_double_prime = lambdify(x, f_double_prime, modules=['sympy'])  
    while(True):
        x = a - ((f(a) * (b - a)) / (f(b) - f(a)))
        iterations += 1
        if (f_prime(x) * f_double_prime(x) >= 0):
            a, b = b, a
        if(abs(x - a) < tolerance):
            return x, iterations
        else:
            a = x

FILE_PATH = "D:\\Studing\\Чисельні методи\\Лабораторна робота №5\\lab_5_1.txt"
TOLERANCE = 1e-6

equation, roots = read_data_from_file(FILE_PATH)
print(f"Equation: {equation}")
print_roots(roots)
x = symbols('x')
func = lambdify(x, equation, modules=['sympy'])
print_graph(func)
a, b = read_intervals(func)
root, iterations = chord_method(equation, x, func, a, b, TOLERANCE)
print(f"X: {round(root, 3)} was found through {iterations} iterations, using {TOLERANCE} as tolerance.")

    



