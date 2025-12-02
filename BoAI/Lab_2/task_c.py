import sys
input = sys.stdin.readline

def read_known(n):
    f = []
    p = []
    for _ in range(n):
        f.append(tuple(map(int, input().split())))
        p.append(int(input()))
    return f, p

def predict(target, known_f, known_p, N, K):
    dists = []
    tx0,tx1,tx2,tx3,tx4,tx5 = target
    for idx in range(N):
        fx0,fx1,fx2,fx3,fx4,fx5 = known_f[idx]
        dx0 = tx0 - fx0; dx1 = tx1 - fx1; dx2 = tx2 - fx2
        dx3 = tx3 - fx3; dx4 = tx4 - fx4; dx5 = tx5 - fx5
        dists.append((dx0*dx0 + dx1*dx1 + dx2*dx2 + dx3*dx3 + dx4*dx4 + dx5*dx5, idx))
    dists.sort()
    s = 0
    for i in range(K):
        s += known_p[dists[i][1]]
    return s / K

def main():
    N, M, K = map(int, input().split())
    known_f, known_p = read_known(N)
    for _ in range(M):
        target = tuple(map(int, input().split()))
        print(predict(target, known_f, known_p, N, K))

if __name__ == "__main__":
    main()

# O(NlogN + K)