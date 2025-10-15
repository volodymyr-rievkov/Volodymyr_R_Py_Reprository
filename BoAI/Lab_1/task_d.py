import heapq

INF = 10**12

def dijkstra(n, adj, edges):
    dist = [INF] * (n + 1)
    parent = [-1] * (n + 1)
    dist[1] = 0
    pq = [(0, 1)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for eid, v in adj[u]:
            w = edges[eid][2]
            if dist[v] > dist[u] + w:
                dist[v] = dist[u] + w
                parent[v] = eid
                heapq.heappush(pq, (dist[v], v))
    return dist, parent

def solve():
    n, m, W = map(int, input().split())
    edges = []
    for _ in range(m):
        u, v, w = map(int, input().split())
        edges.append([u, v, w])

    adj = [[] for _ in range(n + 1)]
    for i, (u, v, _) in enumerate(edges):
        adj[u].append((i, v))
        adj[v].append((i, u))

    backup = [e[:] for e in edges]

    for e in edges:
        if e[2] == -1:
            e[2] = 10**9
    dist1, _ = dijkstra(n, adj, edges)
    if dist1[n] < W:
        print(-1)
        return

    edges = [b[:] for b in backup]
    for e in edges:
        if e[2] == -1:
            e[2] = 1
    dist2, _ = dijkstra(n, adj, edges)
    if dist2[n] > W:
        print(-1)
        return
    if dist2[n] == W:
        for e in edges:
            print(e[2])
        return

    while True:
        dist, parent = dijkstra(n, adj, edges)
        if dist[n] == W:
            break
        if dist[n] > W:
            break

        need = W - dist[n]

        path = []
        cur = n
        while cur != 1 and parent[cur] != -1:
            eid = parent[cur]
            path.append(eid)
            u, v, _ = edges[eid]
            cur = v if cur == u else u
        if cur != 1:
            print(-1)
            return

        increased = False
        for eid in path:
            if backup[eid][2] == -1:
                curw = edges[eid][2]
                if curw < 200:
                    delta = min(200 - curw, need)
                    edges[eid][2] += delta
                    increased = True
                    break
        if not increased:
            print(-1)
            return

    dist, _ = dijkstra(n, adj, edges)
    if dist[n] != W:
        print(-1)
        return

    for e in edges:
        print(e[2])

if __name__ == "__main__":
    solve()