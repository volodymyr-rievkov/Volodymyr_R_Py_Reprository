import numpy as np

def read_matrix_from_file(file_path):
    matrix = np.loadtxt(file_path, dtype=float)
    return matrix[:, :-1], matrix[:, -1]

def validate_matrix_1(matrix):
    if matrix.shape[0] != matrix.shape[1]:
        print("Error: Matrix is not square.")
        return False
    n = len(matrix)
    if(np.linalg.det(matrix) == 0):
        print("Matrix determinant equals zero.")
        return False
    for i in range(1, n + 1):
        sub_matrix = matrix[:i, :i]
        if(np.linalg.det(sub_matrix) == 0):
            print("Error matrix contains zero minor.")
            return False
    return True

def get_l_u_matrices(matrix):
    n = len(matrix) 
    l_matrix = np.zeros((n, n))
    u_matrix = np.zeros((n, n))
    for s in range(n):
        for j in range(s, n):
            sum = 0
            for k in range(s):
                sum += l_matrix[s][k] * u_matrix[k][j]
            u_matrix[s][j] = matrix[s][j] - sum
        for i in range(s, n):
            if(s == i):
                l_matrix[s][s] = 1
            else:
                sum = 0
                for k in range(s):
                    sum += l_matrix[i][k] * u_matrix[k][s]
                l_matrix[i][s] = (matrix[i][s] - sum) / u_matrix[s][s]
    return l_matrix, u_matrix

def get_y(b, l_matrix):
    n = len(b)
    y = np.zeros_like(b)
    for i in range(n):
        sum = 0
        for s in range(i):
            sum += l_matrix[i][s] * y[s]
        y[i] = b[i] - sum
    return y

def get_x(y, u_matrix):
    n = len(y)
    x = np.zeros_like(y)
    for i in range(n - 1, -1, -1):
        sum = 0
        for s in range(i + 1, n):
            sum += u_matrix[i][s] * x[s]
        x[i] = (y[i] - sum) / u_matrix[i][i]
    return x

def l_u_method(matrix, b):
    l_matrix, u_matrix = get_l_u_matrices(matrix)
    y = get_y(b, l_matrix)
    x = get_x(y, u_matrix)
    return x


def is_diagonally_dominant(matrix):
    n = len(matrix)
    for i in range(n):
        row_sum = sum(abs(matrix[i][j]) for j in range(n) if j != i)
        if abs(matrix[i][i]) < row_sum:
            return False
    return True    

def is_symmetric(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != matrix[j][i]:
                return False
    return True

def is_positively_defined(matrix):
    n = len(matrix)
    for i in range(1, n + 1):
        sub_matrix = matrix[:i, :i]
        if(np.linalg.det(sub_matrix) <= 0):
            return False
    return True

def is_determinant(matrix):
    if (np.linalg.det(matrix) == 0):
        return False
    return True

def make_diagonally_dominant(matrix, b):
    n = len(matrix)
    for i in range(n):
        max_index = np.argmax(np.abs(matrix[i:n, i])) + i  
        if (max_index != i): 
            matrix[[i, max_index]] = matrix[[max_index, i]]  
            b[i], b[max_index] = b[max_index], b[i] 
    return is_diagonally_dominant(matrix) 

def validate_matrix_2(matrix, b):
    check = True
    if(not is_determinant(matrix)):
       print("Error: System of equations can not be solved(det = 0).")
       check = False
    if(not is_diagonally_dominant(matrix)):
        if(not make_diagonally_dominant(matrix, b)):
            print("Error: The matrix is not diagonally dominant. The convergence of the Simple iterations method is not guaranteed.")
            check = False
    if(not is_symmetric(matrix)):
        print("Warning: Matrix is not symmetric. The convergence of the Simple iterations method is not guaranteed.")
    if(not is_positively_defined(matrix)):
        print("Warning: Matrix is not positively defined. The convergence of the Simple iterations method is not guaranteed.")
    return check

def calculate_norm_c(matrix):
    D = np.diag(np.diag(matrix))  
    L = np.tril(matrix, -1)       
    U = np.triu(matrix, 1)        
    
    D_L_inv = np.linalg.inv(D + L)
    C = -D_L_inv.dot(U)
    
    norm_c = np.linalg.norm(C, np.inf)
    return min(norm_c, 0.99)

def simple_iter_method(matrix, b, x_0, tolerance):
    n = len(matrix)
    q = calculate_norm_c(matrix)
    iterations = 1
    while True:
        x_new = x_0.copy()
        for j in range(n):
            sigma = sum(matrix[j][k] * x[k] for k in range(n) if k != j)
            x_new[j] = (b[j] - sigma) / matrix[j][j]
        error = max(abs(x_new[i] - x_0[i]) for i in range(n))
        if (((1 - q) / q) * error < tolerance):
            return x_new, iterations
        x_0 = x_new
        iterations += 1


FILE_PATH = "D:\\Studing\\Чисельні методи\\Розрахункова робота\\task_2.txt"
TOLERANCE = 1e-2

matrix, b = read_matrix_from_file(FILE_PATH)
print("Matrix:")
print(matrix)
print("B:")
print(b)
if(validate_matrix_1(matrix)):
    x = l_u_method(matrix, b)
    print("---LU method---")
    print(f"X: {np.round(x, 3)}")
matrix_m = np.array([[7, 2, -1], [0, -58, 8], [0, 5, 57]])
b_m = np.array([-1, 57, 1])
print(matrix_m)
print(b_m)
if(validate_matrix_2(matrix_m, b_m)):
    x_0 = np.array([0.5, -0.5, 0.2])
    x, iterations = simple_iter_method(matrix_m, b_m, x_0, TOLERANCE)
    print("---Simple iterations method---")
    print(f"X: {np.round(x, 3)}.")
    print(f"Iterations: {iterations}")
YELLOW = "\033[33m"
RESET = "\033[0m"
print(f"{YELLOW}---Built-in function---")
print(f"{YELLOW}X: {np.round(np.linalg.solve(matrix_m, b_m), 3)}{RESET}")    