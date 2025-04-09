import sympy as sp

N = 5

def read_function(filename):
    with open(filename, 'r') as file:
        func_str = file.read().strip()
    print("Function:", func_str)
    return func_str

def is_convex(func_str):
    f = sp.sympify(func_str)
    variables = sorted(list(f.free_symbols), key=str)

    grad = [sp.diff(f, var) for var in variables]
    hessian = sp.Matrix([[sp.diff(g, var) for var in variables] for g in grad])

    print("----- Hessian matrix -----\n")
    sp.pprint(hessian)

    n = len(variables)
    for i in range(1, n + 1):
        minor = hessian[:i, :i].det()
        if(minor < 0):
            print(f"Minor #{i}: {minor} < 0")
            print(" ! Function is not convex. Method of gradient descent cannot be used. ! ")
            return False
        print(f"Minor #{i}: {minor} > 0")
    return True

def find_derivatives(f, variables):
    derivatives = [sp.diff(f, var) for var in variables]
    print("----- Derivatives -----")
    for der in derivatives:
        print(der)
    return derivatives

def calc_gradient(derivatives, point):
    gradient = [der.evalf(subs=point) for der in derivatives]
    print("Gradient:", [round(val, N) for val in gradient])
    return gradient

def calc_beta(f, gradient, point, variables):
    beta = sp.symbols('B')
    new_point = {var: point[var] - beta * gradient[i] for i, var in enumerate(variables)}
    new_f = f.subs(new_point)
    new_f_derivative = sp.diff(new_f, beta)
    beta_value = sp.solve(new_f_derivative, beta)
    print("Beta:", round(beta_value[0], N))
    return beta_value[0]

def calc_norm_of_diff(point_0, point_1):
    vector_0 = sp.Matrix([point_0[var] for var in point_0]) 
    vector_1 = sp.Matrix([point_1[var] for var in point_1])
    diff_vector = vector_1 - vector_0
    return sp.sqrt(sum([val**2 for val in diff_vector]))

def gradien_descent_method(func_str, start_point, eps):

    f = sp.sympify(func_str)
    variables = sorted(list(f.free_symbols), key=str)
    derivatives = find_derivatives(f, variables)

    point_0 = dict(zip(variables, start_point))
    print("Start point:", [round(point_0[val], N) for val in point_0])

    iterations = 0
    while(True):
        iterations += 1
        print(f"----- Iteration #{iterations} -----")
        gradient = calc_gradient(derivatives, point_0)
        beta = calc_beta(f, gradient, point_0, variables)
        point_1 = {var: point_0[var] - beta * gradient[i] for i, var in enumerate(variables)}
        print(f"Point #{iterations}: {[round(point_0[val], N) for val in point_0]}")
        print(f"Point #{iterations + 1}: {[round(point_1[val], N) for val in point_1]}")
        norm = calc_norm_of_diff(point_0, point_1)
        if(norm < eps):
            print(f"{[round(point_1[val], N) for val in point_1]} - {[round(point_0[val], N) for val in point_0]} = {norm} > {eps}")
            print("----- Result -----")
            print([round(point_0[val], N) for val in point_0])
            print("F:", round(f.evalf(subs=point_0), N))
            break
        print(f"{[round(point_1[val], N) for val in point_1]} - {[round(point_0[val], N) for val in point_0]} = {norm} < {eps}")
        point_0 = point_1
    return point_0, iterations

FUNCTION = "D:/Programming/PythonApplications/MMDO/Lab_8/func.txt"
func_str = read_function(FUNCTION)

EPS = 1e-6
start_point = [0, 0, 0]

if(is_convex(func_str)):
    gradien_descent_method(func_str, start_point, EPS)