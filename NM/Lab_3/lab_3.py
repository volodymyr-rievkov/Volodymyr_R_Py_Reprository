import numpy as np

def read_matrix_from_file(file_path):
    matrix = np.loadtxt(file_path, dtype=float)
    return matrix[:, :-1], matrix[:, -1]

def write_matrix_to_file(matrix, file_path):
    with open(file_path, 'a') as file:
        file.write('\n')
        np.savetxt(file, matrix, fmt='%f')

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

def check_matrix(matrix, b):
    check = True
    if(not is_determinant(matrix)):
       print("Error: System of equations can not be solved(det = 0).")
       check = False
    if(not is_diagonally_dominant(matrix)):
        if(not make_diagonally_dominant(matrix, b)):
            print("Error: The matrix is not diagonally dominant. The convergence of the Seidel method is not guaranteed.")
            check = False
    if(not is_symmetric(matrix)):
        print("Warning: Matrix is not symmetric. The convergence of the Seidel method is not guaranteed.")
    if(not is_positively_defined(matrix)):
        print("Warning: Matrix is not positively defined. The convergence of the Seidel method is not guaranteed.")
    return check

def calculate_norm_c(matrix):
    D = np.diag(np.diag(matrix))  
    L = np.tril(matrix, -1)       
    U = np.triu(matrix, 1)        
    
    D_L_inv = np.linalg.inv(D + L)
    C = -D_L_inv.dot(U)
    
    norm_c = np.linalg.norm(C, np.inf)
    return min(norm_c, 0.99)

def seidel_method(matrix, b, tolerance):
    n = len(matrix)
    x = np.zeros(n)
    q = calculate_norm_c(matrix)
    iterations = 0
    while True:
        x_new = x.copy()
        for i in range(n):
            sum1 = sum(matrix[i][j] * x_new[j] for j in range(i))
            sum2 = sum(matrix[i][j] * x[j] for j in range(i + 1, n))
            x_new[i] = (b[i] - sum1 - sum2) / matrix[i][i]
        error = max(abs(x_new[i] - x[i]) for i in range(n))
        if (((1 - q) / q) * error < tolerance):
            print("Number of iterations:", iterations)
            return x_new  
        x = x_new
        iterations += 1

def calculate_error(matrix, b, x):
    Ax = np.dot(matrix, x)
    error = np.linalg.norm(Ax - b)
    return error

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №3\\lab_3_3.txt"
matrix, b = read_matrix_from_file(file_path)

print("Matrix:")
print(matrix)
print("Vector:")
print(b)

if(check_matrix(matrix, b)):

    TOLERANCE = 1e-10
    x = seidel_method(matrix, b, TOLERANCE)
    error = calculate_error(matrix, b, x)

    print("X:")
    print(x)

    print("Error: ")
    print(error)

    write_matrix_to_file(x, file_path)