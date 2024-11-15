from sympy import symbols, diff, lambdify, sympify
import numpy as np

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        equation = file.readline().strip() 
        roots = [] 
        for root in file:  
            roots.append(float(root.strip()))
    return equation, roots  

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

FILE_PATH = "D:\\Studing\\Чисельні методи\\Лабораторна робота №5\\lab_5_2.txt"
TOLERANCE = 1e-6

equation, roots = read_data_from_file(FILE_PATH)
print(f"Equation: {equation}")
print(f"Roots: {roots}")

    



