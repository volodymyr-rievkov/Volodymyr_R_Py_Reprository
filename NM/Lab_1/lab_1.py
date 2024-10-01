import numpy as np

def read_matrix_from_file(file_path):
    return np.loadtxt(file_path, dtype=int)

def write_matrix_to_file(matrix, file_path):
    with open(file_path, 'a') as file:
        file.write('\n')
        np.savetxt(file, matrix, fmt='%f')

def inverse_matrix(matrix):
    n = matrix.shape[0]
    augmented_matrix = np.zeros((n, 2 * n))
    augmented_matrix[:, :n] = matrix.astype(float)  
    np.fill_diagonal(augmented_matrix[:, n:], 1.0)  

    for i in range(n):
        max_row = np.argmax(np.abs(augmented_matrix[i:, i])) + i
        if augmented_matrix[max_row][i] == 0.0:
            print("Error: Zero pivot detected.")
            return None
        if max_row != i:
            augmented_matrix[[i, max_row]] = augmented_matrix[[max_row, i]]
        for j in range(n):
            if i != j:
                ratio = augmented_matrix[j][i] / augmented_matrix[i][i]
                augmented_matrix[j] -= ratio * augmented_matrix[i]

    for i in range(n):
        divisor = augmented_matrix[i][i]
        augmented_matrix[i] /= divisor

    return np.round(augmented_matrix[:, n:], 1)

def multiply_matrices(a, b):
    return np.round(np.dot(a, b))

file_path = "D:\\Studing\\Чисельні методи\\Лабораторна робота №1\\lab_1_3.txt"
matrix = read_matrix_from_file(file_path)
print("Matrix:")
print(matrix)
inversed_matrix = inverse_matrix(matrix)
print("Inversed matrix:")
print(inversed_matrix)
write_matrix_to_file(inversed_matrix, file_path)
print("Matrix * inversed matrix:")
print(multiply_matrices(matrix, inversed_matrix))