import numpy as np

def read_matrix_from_file(file_path):
    matrix = np.loadtxt(file_path, dtype=float)
    return matrix[:, :-1], matrix[:, -1]

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

def print_rounded_matrix(matrix):
    rounded_matrix = np.round(matrix, 2)
    print(rounded_matrix)

def multiply_matrices(matrix_1, matrix_2):
    return np.round(np.dot(matrix_1, matrix_2))

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

def write_matrix_to_file(matrix, file_path):
    with open(file_path, 'a') as file:
        file.write('\n')
        np.savetxt(file, matrix, fmt='%f')

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №2\\file_4.txt"
matrix, b = read_matrix_from_file(file_path)
print("Matrix:")
print(matrix)
print("B:")
print(b)
l_matrix, u_matrix = get_l_u_matrices(matrix)
print("L matrix: ")
print_rounded_matrix(l_matrix)
print("U matrix: ")
print_rounded_matrix(u_matrix)
print("L * U:")
print(multiply_matrices(l_matrix, u_matrix))
y = get_y(b, l_matrix)
print("Y: ")
print_rounded_matrix(y)
x = get_x(y, u_matrix)
print("X:")
print_rounded_matrix(x)
write_matrix_to_file(x, file_path)
print("Built-in func to solve system of linear equations:")
print(np.round(np.linalg.solve(matrix, b), 2))