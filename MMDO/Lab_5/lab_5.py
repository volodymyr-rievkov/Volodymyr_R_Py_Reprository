from collections import Counter
import copy

def check_task(C, a, b):
    sum_b = sum(b)
    sum_a = sum(a)
    diff = sum_a - sum_b

    if(diff > 0):
        b.append(diff)
        for row in C:
            row.append(0)
    elif(diff < 0):
        a.append(abs(diff))
        C.append([0] * len(C[0]))

def print_matrix(C):
    for row in C:
        print("|", " ".join(map(str, row)), "|")

def min_value_method(C, a, b):
    rows = len(C)
    cols = len(C[0])
    a_copy = copy.deepcopy(a) 
    b_copy = copy.deepcopy(b)
    C_copy = copy.deepcopy(C)
    result = [[0] * cols for _ in range(rows)]

    while((sum(b_copy) > 0) and (sum(a_copy) > 0)):
        min_value = float('inf')
        min_i = min_j = -1

        for i in range(rows):
            for j in range(cols):
                if((C_copy[i][j] != -1) and (C_copy[i][j] < min_value) and (a_copy[i] > 0) and (b_copy[j] > 0) and (result[i][j] == 0)):
                    min_value = C_copy[i][j]
                    min_i, min_j = i, j

        transfer_value = min(a_copy[min_i], b_copy[min_j])
        result[min_i][min_j] = transfer_value
        a_copy[min_i] -= transfer_value
        b_copy[min_j] -= transfer_value

        if(a_copy[min_i] == 0):
            for j in range(cols):
                C_copy[min_i][j] = -1

        if(b_copy[min_j] == 0):
            for i in range(rows):
                C_copy[i][min_j] = -1
        
    return result

def check_degeneracy(X):
    rows = len(X)
    cols = len(X[0])

    count = 0
    for i in range(rows):
        for j in range(cols):
            if(X[i][j] != 0):
                count += 1
    
    if(not ((rows + cols - 1) == count)):
        print("Error: Non-degeneracy check failed.")
        return False
    return True

def calc_total(X, C):
    rows = len(X)
    cols = len(X[0])
    value = 0.0

    for i in range(rows):
        for j in range(cols):
            if(X[i][j] != 0):
                value += X[i][j] * C[i][j]

    return value 

def calc_potentials(X, C):
    rows = len(X)
    cols = len(X[0])
    u = [None] * rows
    v = [None] * cols
    u[0] = 0

    while None in u or None in v:
        for i in range(rows):
            for j in range(cols):
                if X[i][j] != 0:
                    if u[i] is not None and v[j] is None:
                        v[j] = C[i][j] - u[i]
                    elif u[i] is None and v[j] is not None:
                        u[i] = C[i][j] - v[j]
    
    return u, v

def calc_delta(X, C, u, v):
    rows = len(X)
    cols = len(X[0])
    delta = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            if X[i][j] == 0:
                delta[i][j] = C[i][j] - (u[i] + v[j]) 
    
    return delta

def find_min_delta(delta):
    rows = len(delta)
    cols = len(delta[0])
    min = float('inf')
    min_i = min_j = -1
    for i in range(rows):
        for j in range(cols):
            if delta[i][j] < min:
                min = delta[i][j]
                min_i, min_j = i, j
    return min, min_i, min_j

def find_cycle(X, start_i, start_j):
    n = len(X)  
    m = len(X[0])  
    T = copy.deepcopy(X)
    T[start_i][start_j] = 1  

    while True:
        i_s, j_s = [], []
        for i in range(n):
            for j in range(m):
                if T[i][j] != 0:
                    i_s.append(i)
                    j_s.append(j)
        
        xcount = Counter(i_s)
        ycount = Counter(j_s)

        for i, count in xcount.items():
            if count <= 1:
                for j in range(m):
                    T[i][j] = 0  
        for j, count in ycount.items():
            if count <= 1:
                for i in range(n):
                    T[i][j] = 0 

        if all(x > 1 for x in xcount.values()) and all(y > 1 for y in ycount.values()):
            break

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    
    print("X:")
    print_matrix(X)
    print("T:")
    print_matrix(T)
    fringe = set((x, y) for x in range(n) for y in range(m) if T[x][y] > 0)
    print("Fringe: ", fringe)
    size = len(fringe)
    path = [(start_i, start_j)]  
    while len(path) < size:
        last = path[-1]
        if last in fringe:
            fringe.remove(last)
        next_point = min(fringe, key=lambda point: dist(last[0], last[1], point[0], point[1]))
        path.append(next_point)

    return path

def improve_plan(X, cycle):
    plus_positions = cycle[::2]
    minus_positions = cycle[1::2]

    min_value = min(X[i][j] for i, j in minus_positions)

    for i, j in plus_positions:
        X[i][j] += min_value
    for i, j in minus_positions:
        X[i][j] -= min_value

def potential_method(X, C):
    u, v = calc_potentials(X, C)
    delta = calc_delta(X, C, u, v)

    print("u: ", u)
    print("v: ", v)
    print("Δ:")
    print_matrix(delta)

    min_delta, min_i, min_j = find_min_delta(delta)
    if(min_delta >= 0):
        return X
     
    cycle = find_cycle(X, min_i, min_j)
    print("Cycle: ", cycle)
    improve_plan(X, cycle)

    return potential_method(X, C)

C = [
    [2, 3, 6, 8, 2, 10],
    [8, 1, 2, 3, 5, 6],
    [7, 4, 4, 1, 4, 8],
    [2, 8, 5, 1, 3, 6]
    ]

a = [130, 90, 100, 140]

b = [110, 50, 30, 80, 100, 90]

C = [
    [12, 16, 21, 19, 32],
    [4, 4, 9, 5, 24],
    [3, 8, 14, 10, 26],
    [24, 33, 36, 34, 49],
    [9, 25, 30, 20, 31]
]
a = [85, 75, 125, 65, 170]
b = [105, 105, 95, 130, 85]

check_task(C, a, b)
print("a: ", a)
print("b: ", b)
print("C: ")
print_matrix(C)

print("----- Min value method -----")
X = min_value_method(C, a, b)
total = calc_total(X, C)
print("X: ")
print_matrix(X)
print("Total: ", total)

if(check_degeneracy(X)):
    print("----- Potential method -----")
    X = potential_method(X, C)
    total = calc_total(X, C)
    print("X: ")
    print_matrix(X)
    print("Total: ", total)