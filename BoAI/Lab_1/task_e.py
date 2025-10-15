from collections import deque

def read_input():
    n, m, k = map(int, input().split())
    friends = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v = map(int, input().split())
        friends[u].append(v)
        friends[v].append(u)
    sick = list(map(int, input().split()))
    return n, friends, sick

def bfs_infection(n, friends, sick):
    infected = [False] * (n + 1)
    q = deque()
    for s in sick:
        if s != 1:
            infected[s] = True
            q.append(s)
    while q:
        cur = q.popleft()
        for nb in friends[cur]:
            if nb == 1:
                continue
            if not infected[nb]:
                infected[nb] = True
                q.append(nb)
    return infected

def find_dangerous(friends, infected):
    dangerous = [v for v in friends[1] if infected[v]]
    return sorted(dangerous)

def print_result(dangerous):
    print(len(dangerous))
    if dangerous:
        print(*dangerous)

def main():
    n, friends, sick = read_input()
    infected = bfs_infection(n, friends, sick)
    dangerous = find_dangerous(friends, infected)
    print_result(dangerous)

if __name__ == "__main__":
    main()

# O(n + m), same with memory