from sympy import symbols, diff, lambdify
from scipy.optimize import brentq

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        equation = file.readline().strip() 
        g = file.readline().strip()
        intervals = file.readline().split()
    return equation, g, float(intervals[0]), float(intervals[1])

def check_intervals(func, a, b):
        if(func(a) * func(b) < 0):
            return True
        else:
            print("Error: Statement 'f(a) * f(b) < 0' is incorrect.\n You should seperate roots")
            return False

def seperate_roots(func, a, b):
    STEP = 0.1
    intervals = []
    x = a
    while x < b:
        next_x = x + STEP
        if func(x) * func(next_x) < 0:
            intervals.append((x, next_x))
        x = next_x
    return intervals

def convert_str_to_func(func_str):
    x = symbols('x')
    return lambdify(x, func_str, modules=['numpy'])

def get_first_deravative(equation):
    x = symbols('x')
    return diff(equation, x)

def get_first_and_second_derivatives(equation):
    x = symbols('x')
    f_prime = diff(equation, x)
    f_double_prime = diff(f_prime, x)
    f_prime = lambdify(x, f_prime, modules=['numpy']) 
    f_double_prime = lambdify(x, f_double_prime, modules=['numpy']) 
    return f_prime, f_double_prime

def chord_method(equation, a, b, tolerance):
    iterations = 0
    f_prime, f_double_prime = get_first_and_second_derivatives(equation) 
    f = convert_str_to_func(equation)
    while(True):
        x = a - ((f(a) * (b - a)) / (f(b) - f(a)))
        iterations += 1
        primes = f_prime(x) * f_double_prime(x)
        if (primes >= 0):
            a, b = b, a
        if(abs(x - a) < tolerance):
            return x, iterations
        else:
            a = x

def simple_iter_method(g_str, x_0, tolerance):
    prime_str = get_first_deravative(g_str)
    prime = convert_str_to_func(prime_str)
    if(abs(prime(x_0)) >= 1):
        return None, None
    g = convert_str_to_func(g_str)
    iterations = 0
    x = x_0
    while(True):
        iterations += 1
        y = g(x)
        if(abs(x - y) < tolerance):
            return y, iterations
        x = y

FILE_PATH = "D:\\Studing\\Чисельні методи\\Розрахункова робота\\task_1.txt"
TOLERANCE = 1e-5

equation, g, a, b = read_data_from_file(FILE_PATH)
print(f"Equation: {equation}")
print(f"g(x): {g}")
print(f"a: {a}, b: {b}")
func = convert_str_to_func(equation)
if(check_intervals(func, a, b)):
    root_1, iterations_1 = chord_method(equation, a, b, TOLERANCE)
    x_0 = 1.0
    root_2, iterations_2 = simple_iter_method(g, x_0, TOLERANCE)
    print(f"X: {round(root_1, 3)} was found through {iterations_1} iterations, using chord method.")
    print(f"X: {round(root_2, 3)} was found through {iterations_2} iterations, using simple iterations method."if(root_2 != None) else "Error: Simple iterations method is non convergent!")
    YELLOW = "\033[33m"
    print(f"{YELLOW}X: {round(brentq(func, a, b), 3)} was found using built-in function.")
    RESET = "\033[0m"
    print(RESET)
