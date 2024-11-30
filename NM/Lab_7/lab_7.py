from sympy import symbols, lambdify

def read_file(file_name):
    with open(file_name, 'r') as file:
        func = file.readline().strip()
        bounds = file.readline().split()
    return func, float(bounds[0]), float(bounds[1])

def convert_str_to_func(func_str):
    x = symbols('x')
    return lambdify(x, func_str, modules=['sympy'])

def simpson_method(func, a, b, n):
    h = (b - a) / (2 * n)
    s = func(a) - func(b)
    e = 1
    for i in range(1, (2 * n) - 1):
        s += (3 + e) * func(a + i * h)
        e = -e
    s *= (h / 3)
    return s

def trapezoid_method(func, a, b, n):
    h = (b - a) / n
    s = (func(a) + func(b)) / 2
    x = a + h
    for _ in range(n - 1):
        s += func(x)
        x += h
    s *= h
    return s
    
def calc_integral_with_tolerance(func, a, b, n, method, tolerance):
    s_old = method(func, a, b, n)
    while(True):
        n *= 2
        s_new = method(func, a, b, n)
        if(abs(s_old - s_new) < tolerance):
            return s_new, n
        s_old = s_new

FILE_NAME = "D:\\Studing\\Чисельні методи\\Лабораторна робота №7\\lab_7_1.txt"
TOLERANCE = 0.5 * 10e-5

func_str, a, b = read_file(FILE_NAME)
func = convert_str_to_func(func_str)
n = 2

print(f"Integral:\n{func_str}\nWith bounds a: {a}, b: {b}.")

s, n = calc_integral_with_tolerance(func, a, b, n, simpson_method, TOLERANCE)
print("Simpson method: ")
print(f"S = {s}, with n = {n}.")

s, n = calc_integral_with_tolerance(func, a, b, n, trapezoid_method, TOLERANCE)
print("Trapezoid method: ")
print(f"S = {s}, with n = {n}.")

