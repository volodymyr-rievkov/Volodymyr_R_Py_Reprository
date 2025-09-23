# import sys
# from collections import deque

# data = sys.stdin.read().strip().split(); ptr = 0

# n = int(data[ptr]); ptr += 1
# m = int(data[ptr]); ptr += 1

# grid = []
# for _ in range(n):
#     row = list(data[ptr]); ptr += 1
#     grid.append(row)


    
# dirty_pos = []
# dirty_pos_bit = {}
# for i in range(n):
#     for j in range(m):
#         if grid[i][j] == '*':
#             dirty_pos.append((i, j))
#             dirty_pos_bit[(i, j)] = len(dirty_pos) - 1



# def bfs(n, m, grid, dirty_pos, dirty_pos_bit, start_pos=(0, 0)):
#     k = len(dirty_pos)
#     if k == 0:
#         return 0

#     start_mask = 0
#     for idx, _ in enumerate(dirty_pos):
#         start_mask |= (1 << idx)

#     queue = deque()
#     queue.append((start_pos[0], start_pos[1], start_mask, 0))
#     visited = set()
#     visited.add((start_pos[0], start_pos[1], start_mask))

#     while queue:
#         x, y, mask, dist = queue.popleft()

#         if mask == 0:
#             return dist

#         if (x, y) in dirty_pos_bit:
#             bit = dirty_pos_bit[(x, y)]
#             if (mask >> bit) & 1:
#                 new_mask = mask & ~(1 << bit)
#                 new_state = (x, y, new_mask)
#                 if new_state not in visited:
#                     visited.add(new_state)
#                     queue.append((x, y, new_mask, dist+1))

#         possible_steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
#         for dx, dy in possible_steps:
#             new_x, new_y = x + dx, y + dy
#             if(0 <= new_x < n) and (0 <= new_y < m):
#                 new_state = (new_x, new_y, mask)
#                 if(new_state not in visited):
#                     visited.add(new_state)
#                     queue.append((new_x, new_y, mask, dist+1))



# print(bfs(n, m, grid, dirty_pos, dirty_pos_bit))



# import sys
# from collections import deque

# data = sys.stdin.read().strip().split(); ptr = 0

# n = int(data[ptr]); ptr += 1
# m = int(data[ptr]); ptr += 1

# grid = []
# for _ in range(n):
#     row = list(data[ptr]); ptr += 1
#     grid.append(row)


# dirty_pos = []
# for i in range(n):
#     for j in range(m):
#         if(grid[i][j] == '*'):
#             dirty_pos.append((i, j))

# k = len(dirty_pos)
# START_POS = (0, 0)
# positions = [START_POS] + dirty_pos


# def dist_bfs(n, m, start_pos):
#     queue = deque()
#     queue.append(start_pos)
#     visited = [[-1] * m for _ in range(n)]
#     visited[start_pos[0]][start_pos[1]] = 0
#     while queue:
#         (x, y) = queue.popleft()
#         possible_steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
#         for px, py in possible_steps:
#             new_x, new_y = x + px, y + py
#             if(0 <= new_x < n) and (0 <= new_y < m) and visited[new_x][new_y] == -1:
#                 visited[new_x][new_y] = visited[x][y] + 1
#                 queue.append((new_x, new_y))
#     return visited


# all_dist = []
# for x, y in positions:
#     all_dist.append(dist_bfs(n, m, (x, y)))

# dist = [[0]*(k+1) for _ in range(k+1)]

# for i in range(k + 1):
#     for j in range(k + 1):
#         xi, yi = positions[j]
#         dist[i][j] = all_dist[i][xi][yi]


# INF = int(1e9)
# dp = [[INF]*(k+1) for _ in range(1<<k)]
# dp[0][0] = 0 

# for mask in range(1<<k):
#     for u in range(k+1):
#         if dp[mask][u] == INF:
#             continue
#         for v in range(1,k+1):
#             if not (mask & (1<<(v-1))):
#                 new_mask = mask | (1<<(v-1))
#                 dp[new_mask][v] = min(dp[new_mask][v], dp[mask][u]+dist[u][v]+1)  # +1 щоб прибрати

# ans = min(dp[(1<<k)-1][1:])
# print(ans)