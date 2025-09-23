import sys
from collections import defaultdict, deque



data = sys.stdin.read().strip().split(); ptr = 0

n = int(data[ptr]); ptr += 1
start = int(data[ptr]); ptr += 1
goal = int(data[ptr]); ptr += 1

triangles = []
for _ in range(n):
    triangle = []
    for _ in range(3):
        x = float(data[ptr]); ptr += 1
        y = float(data[ptr]); ptr += 1
        z = float(data[ptr]); ptr += 1
        vrtx = (round(x, 3), round(y, 3), round(z, 3))
        triangle.append(vrtx)
    triangles.append(triangle)



vrtx_ids = {}
vrtx_id = 0
tri_vrtx_ids = []

for triangle in triangles:
    vrtx_id_list = []
    for vrtx in triangle:
        if vrtx not in vrtx_ids:
            vrtx_ids[vrtx] = vrtx_id
            vrtx_id += 1
        vrtx_id_list.append(vrtx_ids[vrtx])
    tri_vrtx_ids.append(vrtx_id_list)



edge_dict = defaultdict(list)   

for idx, vrtx_id in enumerate(tri_vrtx_ids, start=1):
    v1, v2, v3 = vrtx_id
    edges = [
        tuple(sorted([v1, v2])),
        tuple(sorted([v2, v3])),
        tuple(sorted([v3, v1])),
    ]
    for edge in edges:
        edge_dict[edge].append(idx)

adj = [[] for _ in range(n + 1)]

for tri_list in edge_dict.values():
    if(len(tri_list) > 1):
        for a in tri_list:
            for b in tri_list:
                if a != b:
                    adj[a].append(b)



def bfs(start, goal, adj):
    if start == goal:
        return 0
    dist = [-1] * len(adj)
    dist[start] = 0
    q = deque([start])
    while q:
        vrtx = q.popleft()
        for neighbor in adj[vrtx]:
            if dist[neighbor] == -1:
                dist[neighbor] = dist[vrtx] + 1
                if neighbor == goal:
                    return dist[neighbor]
                q.append(neighbor)
    return -1

print(bfs(start, goal, adj))
