from math import log2

def get_y_entropy(q, p_e, p_c):
    return -((q + p_e) * log2((q + p_e) / 2) - p_e * log2(p_c))

def get_y_x_full_cond_entropy(q, p_e, p_c):
    return -(q * log2(q) - p_e * log2(p_e) - p_c * log2(p_c))

def get_channel_info_capacity(q, p_n, p_b):
    H_Y = get_y_entropy(q, p_n, p_b)
    H_Y_X = get_y_x_full_cond_entropy(q, p_n, p_b)
    return H_Y - H_Y_X

Q = 0.90
P_E = 0.02
P_C = 0.08

print("Channel's information capacity:", get_channel_info_capacity(Q, P_E, P_C))