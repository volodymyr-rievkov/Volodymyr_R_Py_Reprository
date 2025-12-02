import sys
import math
import random

input = sys.stdin.readline

def get_start_point(segments):
    n = len(segments)
    x = sum((s[0] + s[3]) * 0.5 for s in segments) / n
    y = sum((s[1] + s[4]) * 0.5 for s in segments) / n
    z = sum((s[2] + s[5]) * 0.5 for s in segments) / n
    return (x, y, z)

def calc_point_segment_dist(P, segment):
    A = segment[:3]
    B = segment[3:]
    ABx = B[0] - A[0]
    ABy = B[1] - A[1]
    ABz = B[2] - A[2]

    APx = P[0] - A[0]
    APy = P[1] - A[1]
    APz = P[2] - A[2]

    AB2 = ABx*ABx + ABy*ABy + ABz*ABz

    if (AB2 == 0):
        return math.sqrt(APx*APx + APy*APy + APz*APz)
    
    t = (ABx * APx + ABy * APy + ABz * APz) / AB2
    t = max(0, min(1, t))
    
    Cx = A[0] + ABx * t
    Cy = A[1] + ABy * t
    Cz = A[2] + ABz * t 

    Dx = P[0] - Cx
    Dy = P[1] - Cy
    Dz = P[2] - Cz

    return math.sqrt(Dx*Dx + Dy*Dy + Dz*Dz)

def calc_total_dist(P, segments):
    return sum((calc_point_segment_dist(P, s) for s in segments))

def minimize_segments(segments):
    P = get_start_point(segments)
    best_val = calc_total_dist(P, segments)

    step = 50.0
    eps = 1e-5

    while step > eps:
        improved = False
        for _ in range(50):
            newP = []
            newP.append(P[0] + (random.random() * 2 - 1) * step)
            newP.append(P[1] + (random.random() * 2 - 1) * step)
            newP.append(P[2] + (random.random() * 2 - 1) * step)

            v = calc_total_dist(newP, segments)

            if (v < best_val):
                best_val = v
                improved = True
                P = tuple(newP)
        
        if not improved:
            step *= 0.5

    return best_val

if __name__ == "__main__":
    
    N = int(input())

    segments = []

    for _ in range(N):
        segments.append(tuple(map(int, input().split())))

    print(minimize_segments(segments))

# O(N + N + Log2(step/eps) * 50 * Т) = O(Log2(steps/eps) * 50 * N)

# def gradient_descent(f_prime, x_0, lr = 0.1, eps=1e-6, max_iter=1000):
#     x = x_0

#     for _ in range(max_iter):
#         grad = f_prime(x)
#         x_new = x - lr * grad

#         if(abs(x - x_new) <= eps):
#             break
#         x = x_new

#     return x