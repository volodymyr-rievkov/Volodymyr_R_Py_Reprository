import numpy as np

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

def read_matrix_from_file(file_path):
    return np.loadtxt(file_path, dtype=int)

def is_singular(matrix):
    return np.linalg.det(matrix) == 0  # Виправлено на правильне логічне значення

def is_symmetric(matrix):
    return np.array_equal(matrix, matrix.T)

def sp_inverse_iteration_method(matrix, tolerance):
    n = len(matrix)
    if(is_singular(matrix)):
        print("Error: Matrix is singular(det = 0).")
        return None, None
    if(not is_symmetric(matrix)):
        print("Warning: Matrix is not symmetric, eigens may be complex.")
    
    y = np.ones(n)
        
    lambda_old = 0
    iterations = 1
    y_norm = np.linalg.norm(y)
    x = y / y_norm

    while True:
        y = l_u_method(matrix, x)
        s = np.dot(y.conj(), y)
        t = np.dot(y.conj(), x)
        y_norm = np.linalg.norm(y)
        x = y / y_norm
        lambda_new = t / s
        if(abs(lambda_new - lambda_old) < tolerance):
            print("Number of iterations:", iterations)
            break

        lambda_old = lambda_new
        iterations += 1
    return lambda_new, x 

def check(matrix, value, vector):
    matrix_vec = np.dot(matrix, vector)
    value_vec = value * vector
    print("Statement 'matrix * vector = value * vector':")
    print(f"{np.round(matrix_vec, 3)} = {np.round(value_vec, 3)}")

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №4\\lab_4_1.txt"

matrix = read_matrix_from_file(file_path)
TOLERANCE = 1e-6

print("Matrix:")
print(matrix)

min_eigen_val, min_eigen_vec = sp_inverse_iteration_method(matrix, TOLERANCE)
if((min_eigen_val is not None) and (min_eigen_vec is not None)):
    print(f"Min eigen value: {np.round(min_eigen_val, 4)} \nMin eigen vector: {np.round(min_eigen_vec, 4)}")

check(matrix, min_eigen_val, min_eigen_vec)