from math import log2

def get_x_pos(x_y_pos):
    x_pos = []
    
    for row in x_y_pos:
        x_pos.append(sum(row))

    return x_pos

def get_y_pos(x_y_pos):
    size = len(x_y_pos[0])
    y_pos = [0] * size

    for row in x_y_pos:
        for i in range(size):
            y_pos[i] += row[i]

    return y_pos

def get_x_y_full_cond_entropy(x_y_pos, y_pos):
    size = len(x_y_pos[0])
    result = 0

    for i in range(size):
        for k in range(size):
            if(x_y_pos[i][k] > 0):
                result += (x_y_pos[i][k] * log2(x_y_pos[i][k] / y_pos[k]))
    
    return -result

def get_x_entropy(x_pos):
    size = len(x_pos)
    result = 0

    for i in range(size):
        if x_pos[i] > 0:
            result += x_pos[i] * log2(x_pos[i])

    return -result

x_y_pos = [[0.170, 0.015, 0.050],
           [0.020, 0.255, 0.025],
           [0.010, 0.030, 0.425]]

x_pos = get_x_pos(x_y_pos)
y_pos = get_y_pos(x_y_pos)

x_entropy = get_x_entropy(x_pos)
x_y_cond_entropy = get_x_y_full_cond_entropy(x_y_pos, y_pos)

i_y_x = x_entropy - x_y_cond_entropy

print("Average information amount I(Y,X):", i_y_x)

