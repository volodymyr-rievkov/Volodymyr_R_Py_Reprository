import numpy as np

def read_matrix_from_file(file_path):
    matrix = np.loadtxt(file_path, dtype=float)
    return matrix[:, :-1], matrix[:, -1]

def write_matrix_to_file(matrix, file_path):
    with open(file_path, 'a') as file:
        file.write('\n')
        np.savetxt(file, matrix, fmt='%f')

def is_diagonaly_dominant(matrix):
    n = len(matrix)
    for i in range(n):
        row_sum = sum(abs(matrix[i][j]) for j in range(n) if j != i)
        if abs(matrix[i][i]) <= row_sum:
            print("Error: Matrix is not diagonaly dominant.")
            return False
    return True    

def is_symmetric(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != matrix[j][i]:
                print("Error: Matrix is not symmetric.")
                return False
    return True

def is_positively_defined(matrix):
    n = len(matrix)
    for i in range(1, n + 1):
        sub_matrix = matrix[:i, :i]
        if(np.linalg.det(sub_matrix) <= 0):
            print("Error: Matrix is not positively defined.")
            return False
    return True

def is_determinant(matrix):
    if (np.linalg.det(matrix) == 0):
        print("Error: Matrix's determinant equals zero.")
        return False
    return True

def make_diagonaly_dominant(matrix, b):
    n = len(matrix)
    for i in range(n):
        if (abs(matrix[i][i]) <= sum(abs(matrix[i][j]) for j in range(n) if j != i)):
            for j in range(i + 1, n):
                if (abs(matrix[j][i]) > sum(abs(matrix[j][k]) for k in range(n) if k != i)):
                    matrix[[i, j]] = matrix[[j, i]]
                    b[i], b[j] = b[j], b[i]
                    break
            else:
                for j in range(n):
                    if ((j != i) and (matrix[j][i] != 0)):
                        scale_factor = abs(matrix[i][i]) / abs(matrix[j][i])
                        matrix[i] += scale_factor * matrix[j]
                        b[i] += scale_factor * b[j]
    if(is_diagonaly_dominant(matrix)):
        return True
    else:
        return False

def seidel_method(matrix, b, tolerance):
    n = len(matrix)
    x = np.zeros(n)
    if(not is_determinant(matrix) or not is_symmetric(matrix)or not is_positively_defined(matrix)):
       return x
    if(not is_diagonaly_dominant(matrix)):
        if(not make_diagonaly_dominant(matrix, b)):
            return x
    while True:
        x_new = x.copy()
        for i in range(n):
            sum1 = sum(matrix[i][j] * x_new[j] for j in range(i))
            sum2 = sum(matrix[i][j] * x[j] for j in range(i + 1, n))
            x_new[i] = (b[i] - sum1 - sum2) / matrix[i][i]
        error = max(abs(x_new[i] - x[i]) for i in range(n))
        if (error < tolerance):
            return x_new  
        x = x_new

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №3\\lab_3_3.txt"
matrix, b = read_matrix_from_file(file_path)
TOLERANCE = 1e-10
x = seidel_method(matrix, b, TOLERANCE)
write_matrix_to_file(x, file_path)