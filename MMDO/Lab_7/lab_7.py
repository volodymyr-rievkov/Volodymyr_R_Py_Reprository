import math
from sympy import symbols, sympify, lambdify

def read_function(filename):
    x = symbols('x')

    with open(filename, 'r') as f:
        expression_str = f.read().strip()

    expression = sympify(expression_str)

    func = lambdify(x, expression, modules=['math']) 

    return func

def golden_section_search(a, b, f, epsilon):
    t = (math.sqrt(5) - 1) / 2  
    x_1 = a + (1 - t) * (b - a)
    x_2 = a + t * (b - a)
    iteration = 0
    while (b - a) > epsilon:
        iteration += 1
        print(f"Iteration # {iteration} \nInterval [{a};{b}] \nx_1 = {x_1}, x_2 = {x_2}")
        print(f"f(x1) = {f(x_1)}, f(x2) = {f(x_2)}")
        
        if f(x_1) < f(x_2):
            b = x_2
            x_2 = x_1
            x_1 = a + (1 - t) * (b - a)
        else:
            a = x_1
            x_1 = x_2
            x_2 = a + t * (b - a)
        
        
    
    result = (a + b) / 2
    print(f"\nResult \ninterval: [{a};{b}]")
    print(f"Min ({result};{f(result)}")
    return result

FUNCTION = "D:/Programming/PythonApplications/MMDO/Lab_7/func.txt"
a = 1.0  
b = 1.5 
epsilon = 0.000005

f = read_function(FUNCTION)
minimum = golden_section_search(a, b, f, epsilon)

