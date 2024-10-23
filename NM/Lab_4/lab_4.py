import numpy as np

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
        print("Warning: Matrix is not symmetric.")
        y = np.ones(n, dtype = complex)
    else:
        y = np.ones(n)
    lambda_old = 0
    iterations = 1
    y_norm = np.linalg.norm(y)
    x = y / y_norm

    while True:
        y = np.linalg.solve(matrix, x)
        s = np.dot(y.conj().T, y)
        t = np.dot(y.conj().T, x)
        lambda_new = t / s
        y_norm = np.linalg.norm(y)

        if(abs(lambda_new - lambda_old) < tolerance):
            print("Number of iterations:", iterations)
            break

        lambda_old = lambda_new
        x = y / y_norm
        iterations += 1
    return lambda_new, y 

def check(matrix, value, vector):
    matrix_vec = np.dot(matrix, vector)
    value_vec = value * vector
    print("Statement 'matrix * vector = value * vector':")
    print(f"{np.round(matrix_vec, 3)} = {np.round(value_vec, 3)}")

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №4\\lab_4_2.txt"

matrix = read_matrix_from_file(file_path)
TOLERANCE = 1e-6

print("Matrix:")
print(matrix)

min_eigen_val, min_eigen_vec = sp_inverse_iteration_method(matrix, TOLERANCE)
if((min_eigen_val is not None) and (min_eigen_vec is not None)):
    print(f"Min eigen value: {np.round(min_eigen_val, 4)} \nMin eigen vector: {np.round(min_eigen_vec, 4)}")

check(matrix, min_eigen_val, min_eigen_vec)
