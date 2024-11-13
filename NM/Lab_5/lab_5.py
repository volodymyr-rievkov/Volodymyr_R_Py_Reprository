from sympy import symbols, diff, lambdify, sympify
import numpy as np

def find_separated_intervals(a, b, f):
    intervals = []
    x_vals = np.linspace(a, b, 100)
    y_vals = np.vectorize(f)(x_vals)
    for i in range(1, len(x_vals)):
        if (y_vals[i-1] * y_vals[i]) < 0:
            intervals.append((x_vals[i-1], x_vals[i]))  
    return intervals

def read_data_from_file(file_path):

    with open(file_path, 'r') as file:
        equation = file.readline().strip()
        a = float(file.readline().strip())
        b = float(file.readline().strip())
    return equation, a, b

def get_derivative(equation):

    x = symbols('x')
    f = sympify(equation)
    f_prime = diff(f, x)
    return f_prime

def chord_method(equation, a, b, tolerance):

    x = symbols('x')
    f_symb = sympify(equation)
    f = lambdify(x, f_symb, modules=['sympy'])
    if(f(a) * f(b) < 0):
        iterations = 0
        f_prime = get_derivative(equation)
        f_double_prime = get_derivative(f_prime)
        f_prime = lambdify(x, f_prime, modules=['sympy']) 
        f_double_prime = lambdify(x, f_double_prime, modules=['math'])  

        while(True):
            x = a - ((f(a) * (b - a)) / (f(b) - f(a)))
            iterations += 1
            if (f_prime(x) * f_double_prime(x) >= 0):
                a, b = b, a
            if(abs(x - a) < tolerance):
                return x, iterations
            else:
                a = x
    else:
        print("Error: Function does not have root on current bounds or has more than one root.")
        return None, None

def run_chord_method_for_all(equation, a, b):
    x = symbols('x')
    f_symb = sympify(equation)
    f = lambdify(x, f_symb, modules=['sympy'])

    subintervals = find_separated_intervals(a, b, f)
    for i in range(len(subintervals)):
        sub_a = subintervals[i][0]
        sub_b = subintervals[i][1]
        x, iterations = chord_method(equation, sub_a, sub_b, TOLERANCE)
        print(f"Subinterval №{i + 1}")
        print(f"a: {sub_a}, b: {sub_b}")
        print(f"Iterations: {iterations}")
        print(f"x = {x}")
        print(f"f(x): {f(x)}")

FILE_PATH = "D:\\Studing\\Чисельні методи\\Лабораторна робота №5\\lab_5_2.txt"
TOLERANCE = 1e-6

equation, a, b = read_data_from_file(FILE_PATH)
print(f"Equation: {equation}")
print(f"a: {a}, b: {b}")

run_chord_method_for_all(equation, a, b)
