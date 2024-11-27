from sympy import diff, lambdify, symbols
import numpy as np
from scipy.optimize import fsolve

def read_functions(file_path):
    with open(file_path, 'r') as file:
        funcs = []
        for func in file:
            funcs.append(func.strip())
    return funcs

def convert_str_func_to_func(funcs):
    x = symbols('x')
    y = symbols('y')
    F = []
    for func in funcs:
        F.append(lambdify((x, y), func, modules=['sympy']))
    return F

def print_functions(funcs):
    print("----- System of non-linear equations -----\n")
    for func in funcs:
        print(f"f(x, y) = {func}")
    print()

def calc_derivatives(funcs):
    x = symbols('x')
    y = symbols('y')
    derivatives = []
    for func in funcs:
        df_dx = diff(func, x)
        df_dy = diff(func, y)
        derivatives.append((df_dx, df_dy))
    return derivatives

def convert_derivatives_to_jacobian(derivatives):
    x = symbols('x')
    y = symbols('y')
    J = []
    for derivative_pair in derivatives:
        jacobian_row = []
        for derivative in derivative_pair:
            jacobian_row.append(lambdify((x, y), derivative, 'sympy'))  
        J.append(jacobian_row)
    return J

def print_jacobian(derivatives):
    print("----- Jacobian -----\n")
    print("-" * 67)
    for row in derivatives:
        print(f"| {str(row[0]).center(30)} | {str(row[1]).center(30)} |")
        print("-" * 67)
    print()

def newton_method(F, J, tolerance):

    X = np.array([1.0, 1.0], dtype=float)
    iterations = 0

    while(True):

        iterations += 1

        F_values = []
        for func in F:
            F_values.append(func(X[0], X[1]))
        F_values = np.array(F_values, dtype=float)

        if np.all(np.abs(F_values) < tolerance):  
            return X, iterations
        
        J_values = []
        for derivative_pair in J:
            J_values_row = []
            for derivative in derivative_pair:
                J_values_row.append(derivative(X[0], X[1]))
            J_values.append(J_values_row)
        J_values = np.array(J_values, dtype=float)

        X -= np.linalg.inv(J_values).dot(F_values)

def print_check(F, X,):
    for func in F:
        print(f"F({round(X[0], 5)}, {round(X[1], 5)}) = {round(func(X[0], X[1]), 2)}")
    print()

def system_of_equations(X, F):
    x, y = X
    return [func(x, y) for func in F]

FILE_PATH = "D:\\Studing\\Чисельні методи\\Розрахункова робота\\task_3.txt"
TOLERANCE = 1e-2

funcs = read_functions(FILE_PATH)
print_functions(funcs)
F = convert_str_func_to_func(funcs)
derivatives = calc_derivatives(funcs)
print_jacobian(derivatives)
J = convert_derivatives_to_jacobian(derivatives)
X, iterations = newton_method(F, J, TOLERANCE)
print(f"Iterations: {iterations}")
print_check(F, X)
X_0 = np.array([1.0, 1.0])
X = fsolve(system_of_equations, X_0, args=(F,))
YELLOW = "\033[33m"
RESET = "\033[0m"
print(f"{YELLOW}Built-in function:")
print_check(F, X)
print(RESET)