from collections import deque

N = 3
TARGET = "123456780"

def is_solvable(s):
    nums = [int(c) for c in s if c != '0']
    inv = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                inv += 1
    return inv % 2 == 0

def bfs(start, target):
    queue = deque([(start, 0)])
    visited = set([start])
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    while queue:
        state, steps = queue.popleft()
        if state == target:
            return steps
        
        zero_pos = state.index('0')
        x, y = divmod(zero_pos, 3)

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < N and 0 <= new_y < N:
            
                npos = new_x * N + new_y
                new_state = list(state)
                new_state[zero_pos], new_state[npos] = new_state[npos], new_state[zero_pos]
                new_state_str = ''.join(new_state)
                if new_state_str not in visited:
                    visited.add(new_state_str)
                    queue.append((new_state_str, steps + 1))
    else:
        return -1         

start = ""
for _ in range(N):
    start += input().strip()

if not is_solvable(start):
    print(-1)
else:
    print(bfs(start, TARGET))

# O((n^2)! / 2), same with memory
