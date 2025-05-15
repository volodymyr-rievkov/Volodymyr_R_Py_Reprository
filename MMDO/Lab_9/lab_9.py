import sympy as sp
from scipy.optimize import linprog
import numpy as np
import math

EPS = 1e-8
DECIMAL_PLACES = 10

def golden_section_search(a, b, f, epsilon):
    t = (math.sqrt(5) - 1) / 2  
    x_1 = a + (1 - t) * (b - a)
    x_2 = a + t * (b - a)
    iteration = 0
    while (b - a) > epsilon:
        iteration += 1
        
        if f(x_1) < f(x_2):
            b = x_2
            x_2 = x_1
            x_1 = a + (1 - t) * (b - a)
        else:
            a = x_1
            x_1 = x_2
            x_2 = a + t * (b - a)
        
    result = (a + b) / 2
    return result

def read_function_and_constraints(filename):
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    func_str = lines[0]
    constraints_str = lines[1:-1]
    start_point = [float(val) for val in lines[-1].split()]
    return func_str, constraints_str, start_point

def find_derivatives(f, variables):
    return [sp.diff(f, var) for var in variables]

def calc_gradient(derivatives, point, variables):
    subs_dict = dict(zip(variables, point))
    return [float(der.evalf(subs=subs_dict)) for der in derivatives]

def linear_programming_step(gradient, constraints, variables):
    c = gradient
    A = []
    b = []

    for constraint in constraints:
        if isinstance(constraint, sp.LessThan):
            expr = constraint.lhs - constraint.rhs
        elif isinstance(constraint, sp.GreaterThan):
            expr = -(constraint.lhs - constraint.rhs)
        elif isinstance(constraint, sp.Equality):
            expr = constraint.lhs - constraint.rhs
            coeffs = [float(expr.coeff(var, 1)) if var in expr.free_symbols else 0 for var in variables]
            const_term = float(expr.subs({var: 0 for var in variables}))
            A.append(coeffs)
            b.append(-const_term)
            A.append([-c for c in coeffs])
            b.append(const_term)
            continue
        else:
            raise ValueError(f"Error: Wrong constraint type: '{type(constraint)}'!")

        coeffs = [float(expr.coeff(var, 1)) if var in expr.free_symbols else 0 for var in variables]
        subs_result = expr.subs({var: 0 for var in variables})
        try:
            const_term = float(subs_result)
        except TypeError:
            raise ValueError(f"Error: Coudn't get vector b for: {expr}. Result : {subs_result}")
        A.append(coeffs)
        b.append(-const_term)

    res = linprog(c, A_ub=A, b_ub=b, method='highs')
    if res.success:
        return res.x
    else:
        raise ValueError("Error: Couldn't solve linear programming problem!")

def line_search(f, x_k, s_k, variables):
    direction = np.array(s_k) - np.array(x_k)
    
    def f_alpha(alpha):
        point = np.array(x_k) + alpha * direction
        subs_dict = dict(zip(variables, point))
        return float(f.subs(subs_dict))
    
    return golden_section_search(0, 1, f_alpha, epsilon=1e-6), direction

def frank_wolfe(func_str, constraints_str, start_point, eps):
    f = sp.sympify(func_str)
    variables = sorted(list(f.free_symbols), key=str)
    derivatives = find_derivatives(f, variables)
    constraints = [sp.sympify(c, evaluate=False) for c in constraints_str]
    x_k = np.array(start_point, dtype=float)
    k = 0
    
    while True:
        gradient = calc_gradient(derivatives, x_k, variables)
        s_k = linear_programming_step(gradient, constraints, variables)

        alpha, direction = line_search(f, x_k, s_k, variables)
        
        x_k_next = x_k + alpha * direction
        
        if np.linalg.norm(x_k_next - x_k) < eps:
            break
        
        x_k = x_k_next
        k += 1
        print(f"Iteration {k}: x = {np.round(x_k, DECIMAL_PLACES)}, f(x) = {round(float(f.subs(dict(zip(variables, x_k)))), DECIMAL_PLACES)}")
    
    return x_k, float(f.subs(dict(zip(variables, x_k))))

PROBLEM = "D:\\Programming\\PythonApplications\\MMDO\\Lab_9\\problem.txt"
func_str, constraints_str, start_point = read_function_and_constraints(PROBLEM)
result, value = frank_wolfe(func_str, constraints_str, start_point, EPS)
print(f"Min point: {np.round(result, DECIMAL_PLACES)}")
print(f"Function value: {round(value, DECIMAL_PLACES)}")