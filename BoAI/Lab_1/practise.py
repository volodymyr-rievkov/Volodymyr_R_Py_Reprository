# from collections import deque
   
# def bfs(graph, start):
#     queue = deque([start])
#     visited = set()

#     while queue:
#         vertex = queue.popleft()

#         if vertex not in visited:
#             visited.add(vertex)
#             print(f"{vertex}->", end="")

#             for neighbour in graph[vertex]:
#                 if neighbour not in visited:
#                     queue.append(neighbour)
#     print()

# def goal_bfs(graph, start, goal):
#     queue = deque([[start]])
#     visited = set()

#     while queue:
#         path = queue.popleft()
#         vertex = path[-1]

#         if vertex == goal:
#             return path
        
#         if vertex not in visited:
#             visited.add(vertex)
#             for neighbour in graph[vertex]:
#                 if neighbour not in visited:
#                     queue.append(path + [neighbour])
#     return None

# def bfs_paths(graph, start):
#     queue = deque([[start]])
#     visited = set()
#     paths = {}

#     while queue:
#         path = queue.popleft()
#         vertex = path[-1]

#         if vertex not in visited:
#             visited.add(vertex)
#             paths[vertex] = path

#             for neighbour in graph[vertex]:
#                 if neighbour not in visited:
#                     queue.append(path + [neighbour])
#     return paths

# def dfs(graph, start):
#     stack = [start]
#     visited = set()

#     while stack:
#         vertex = stack.pop()

#         if vertex not in visited:
#             visited.add(vertex)
#             print(f"{vertex}->", end="")
#             for neighbour in reversed(graph[vertex]):
#                 if neighbour not in visited:
#                     stack.append(neighbour)

# def dfs_recursive(graph, start, visited=None):
#     if visited is None:
#         visited = set()

#     if start not in visited:
#         visited.add(start)
#         print(f"{start}->", end="")
#         for neighbour in graph[start]:
#             if neighbour not in visited:
#                 dfs_recursive(graph, neighbour, visited)

# def goal_dfs(graph, start, goal):
#     stack = [[start]]
#     visited = set()

#     while stack:
#         path = stack.pop()
#         vertex = path[-1]

#         if vertex == goal:
#             return path
        
#         if vertex not in visited:
#             visited.add(vertex)
#             for neighbour in reversed(graph[vertex]):
#                 if neighbour not in visited:
#                     stack.append(path + [neighbour])
#     return None

# def goal_dfs_recursive(graph, start, goal, visited=None, path=None):
#     if visited is None:
#         visited = set()
#     if path is None:
#         path = [start]

#     if start == end:
#         return path

#     if start not in visited:
#         visited.add(start)
#         for neighbour in graph[start]:
#             if neighbour not in visited:
#                 new_path = goal_dfs_recursive(graph, neighbour, goal, visited, path + [neighbour])
#                 if new_path:
#                     return new_path
#     return None

# def dfs_paths(graph, start):
#     stack = [[start]]
#     visited = set()
#     paths = {}

#     while stack:
#         path = stack.pop()
#         vertex = path[-1]

#         if vertex not in visited:
#             visited.add(vertex)
#             paths[vertex] = path

#             for neighbour in reversed(graph[vertex]):
#                 if neighbour not in visited:
#                     stack.append(path + [neighbour])
#     return paths

# def dfs_paths_recursive(graph, start, visited=None, path=None, paths=None):
#     if(visited is None):
#         visited = set()
#     if(path is None):
#         path = [start]
#     if(paths is None):
#         paths = {}

#     if start not in visited:
#         visited.add(start)
#         paths[start] = path
#         for neighbour in graph[start]:
#             if neighbour not in visited:
#                 dfs_paths_recursive(graph, neighbour, visited, path + [neighbour], paths)
#     return paths
    
# def dijkstra(graph, start):
#     n = len(graph)
#     dist = [float("inf")] * n
#     dist[start] = 0
#     visited = [False] * n

#     while True:
#         u = None
#         min_dist = float("inf")
#         for i in range(n):
#             if(not visited[i] and dist[i] < min_dist):
#                 min_dist = dist[i]
#                 u = i
#         if u is None:
#             break

#         visited[u] = True

#         for v in range(n):
#             weight = graph[u][v]
#             if weight != 0 and not visited[v]:
#                 if dist[u] + weight < dist[v]:
#                     dist[v] = dist[u] + weight

#     return dist

# def dist_bfs(start, goal, graph):
#     if(start == goal):
#         return 0
#     n = len(graph)
#     distance = [-1] * n
#     distance[start] = 0
#     queue = deque([start]) 

#     while queue:
#         vertex = queue.popleft()
#         for neighbour in graph[vertex]:
#             if(distance[neighbour] != -1):
#                 distance[neighbour] = distance[vertex] + 1
#                 if(neighbour == goal):
#                     return distance[neighbour]
#                 queue.append(neighbour)

#     return -1

# if __name__ == "__main__":

#     graph = [[1, 2, 3], [0, 2, 4], [1, 2, 4], [0, 3], []]
#     start = 0
#     end = 4

#     bfs(graph, start)
#     print(goal_bfs(graph, start, end))
#     paths = bfs_paths(graph, start)
#     for vertex, path in paths.items():
#         print(f"{start} -> {vertex}: {path}") 

#     dfs(graph, start)
#     print()
#     dfs_recursive(graph, start)
#     print()
#     print(goal_dfs(graph, start, end))
#     print(goal_dfs_recursive(graph, start, end))
#     paths = dfs_paths(graph, start)
#     for vertex, path in paths.items():
#         print(f"{start} -> {vertex}: {path}") 
#     paths = dfs_paths_recursive(graph, start)
#     for vertex, path in paths.items():
#         print(f"{start} -> {vertex}: {path}") 

#     graph = [
#         [0, 2, 5, 0],
#         [2, 0, 6, 1],
#         [5, 6, 0, 3],
#         [0, 1, 3, 0]
#     ]

#     print(dijkstra(graph, 0))























