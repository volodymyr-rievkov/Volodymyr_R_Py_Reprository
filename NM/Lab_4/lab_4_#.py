import numpy as np
import math

def read_matrix_from_file(file_path):
    return np.loadtxt(file_path, dtype=float)

def is_symmetric(matrix):
    return np.array_equal(matrix, matrix.T)

def jacobi_rotation(A, B, V, n):
    if(not is_symmetric(matrix)):
        print("Error: Matrix is not symmetric.")
    iterations = 0
    while True:
        iterations += 1
        max_i, max_j = 1, 0
        maximum = abs(A[max_i][max_j])
        for i in range(2, n):
            for j in range(n):
                if i > j:
                    if abs(A[i][j]) > maximum:
                        maximum = abs(A[i][j])
                        max_i, max_j = i, j

        if abs(maximum) < 1e-10:
            break

        p = 2 * A[max_i][max_j]
        q = A[max_i][max_i] - A[max_j][max_j]
        d = math.sqrt(p ** 2 + q ** 2)

        if q == 0:
            c, s, = math.sqrt(2) / 2, math.sqrt(2) / 2
        else:
            r = abs(q) / (2 * d)
            c = math.sqrt(0.5 + r)
            s = math.sqrt(0.5 - r) * math.copysign(1, p * q)

        B[max_i][max_i] = c ** 2 * A[max_i][max_i] + s ** 2 * A[max_j][max_j] + 2 * c * s * A[max_i][max_j]
        B[max_j][max_j] = s ** 2 * A[max_i][max_i] + c ** 2 * A[max_j][max_j] - 2 * c * s * A[max_i][max_j]
        B[max_i][max_j], B[max_j][max_i] = 0, 0

        for m in range(n):
            if m != max_i and m != max_j:
                B[max_i][m] = c * A[m][max_i] + s * A[m][max_j]
                B[m][max_i] = B[max_i][m]

                B[max_j][m] = -s * A[m][max_i] + c * A[m][max_j]
                B[m][max_j] = B[max_j][m]

        for m in range(n):
            temp = c * V[m][max_i] + s * V[m][max_j]
            V[m][max_j] = -s * V[m][max_i] + c * V[m][max_j]
            V[m][max_i] = temp

        A = np.copy(B)

    print('\nIterations:', iterations)
    return B, V

def print_eigens(B, V):
    print('Eigenvalues:', [float(B[i][i]) for i in range(n)], '\n')
    print('Eigenvectors:')
    for i in range(n):
        print([float(V[j][i]) for j in range(n)])

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №4\\lab_4_1.txt"

matrix = read_matrix_from_file(file_path)

n = matrix.shape[0]
matrix_copy = np.copy(matrix)
d_matrix = np.eye(n)

B, V = jacobi_rotation(matrix, matrix_copy, d_matrix , n)

print_eigens(B, V)