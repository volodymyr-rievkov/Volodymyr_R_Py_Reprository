from sympy import symbols, diff, lambdify
from scipy.optimize import root_scalar

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
            print("Error: Statement 'f(a) * f(b) < 0' is incorrect.")
            return False

def convert_str_to_func(func_str):
    x = symbols('x')
    return lambdify(x, func_str, modules=['numpy'])

def separate_roots(f, a, b):
    STEP = 0.1
    intervals = []
    current_a = a

    while current_a < b:
        current_b = current_a + STEP
        if current_b > b:
            current_b = b

        if f(current_a) * f(current_b) < 0:
            intervals.append((current_a, current_b))

        current_a = current_b

    return intervals

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

def find_valid_initial_point(g_str, a, b):
    STEP = 0.1
    g_prime = convert_str_to_func(get_first_deravative(g_str))
    
    x = a
    while x <= b:
        if abs(g_prime(x)) < 1:  
            print(f"X_0: {round(x, 3)}")
            return x
        x += STEP
    print(f"|g'(x)| = {round(abs(g_prime(x)), 3)} >= 1.")
    return None

def simple_iter_method(g_str, a, b, tolerance):
    g = convert_str_to_func(g_str)
    x_0 = find_valid_initial_point(g_str, a, b)
    if(x_0 is None):
        return None, None
    iterations = 0
    x = x_0
    while(True):
        iterations += 1
        x_new = g(x)
        if(abs(x - x_new) < tolerance):
            return x_new, iterations
        x = x_new

FILE_PATH = "D:\\Studing\\Чисельні методи\\Розрахункова робота\\task_1.txt"
TOLERANCE = 1e-5

equation, g, a, b = read_data_from_file(FILE_PATH)
print(f"Equation: {equation}")
print(f"g(x): {g}")
print(f"a: {a}, b: {b}")
func = convert_str_to_func(equation)
if(check_intervals(func, a, b)):
    intervals = separate_roots(func, a, b)
    for interval in intervals:
        print(f"Intervals: a: {round(interval[0], 3)}, b: {round(interval[1], 3)}.")

        print("---Chord method---")
        root_1, iterations_1 = chord_method(equation, interval[0], interval[1], TOLERANCE)
        print(f"X: {round(root_1, 3)}")
        print(f"Iterations: {iterations_1}")

        print("---Simple iter method---")
        root_2, iterations_2 = simple_iter_method(g, interval[0], interval[1], TOLERANCE)
        print(f"X: {round(root_2, 3)}" if(root_2 != None) else f"Error: Simple iterations method is non convergent!")
        print(f"Iterations: {iterations_2}")
        
        YELLOW = "\033[33m"
        print(f"{YELLOW}---Built-in function---")
        print(f"{YELLOW}X: {round(root_scalar(func, method='secant', x0=interval[0], x1=interval[1], xtol=TOLERANCE).root, 3)}")
        RESET = "\033[0m"
        print(RESET)
