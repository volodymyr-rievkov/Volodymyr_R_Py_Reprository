
def find_optimal_investing_strategy(costs, profits, budget):

    if(len(costs) != len(profits) or (len(costs[0]) != len(profits[0]))):
        raise Exception("Error: Costs/Profits Size Mismatch.")
    
    companies_count = len(costs)
    projects_count = len(costs[0])

    dp = [[0.0 for _ in range(budget + 1)] for _ in range(companies_count + 1)]
    strategy = [[-1 for _ in range(budget + 1)] for _ in range(companies_count + 1)]

    for i in range(1, companies_count + 1):
        for w in range(budget + 1):
            for j in range(projects_count):
                cost = costs[i - 1][j]
                profit = profits[i - 1][j]
                if(w >= cost):
                    new_profit = profit + dp[i - 1][w - cost]
                    if(new_profit >= dp[i][w]):
                        dp[i][w] = new_profit
                        strategy[i][w] = j

    selected_projects = []
    budget_copy = budget
    for i in range(companies_count, 0, -1):
        project_idx = strategy[i][budget_copy]
        if(project_idx != -1):
            selected_projects.append((i, project_idx + 1))
            budget_copy -= costs[i - 1][project_idx]

    print(f"Maximal profit: {dp[companies_count][budget]}")
    print("Selected projects:")
    total_cost = 0.0
    for company, project in reversed(selected_projects):
        cost = costs[company - 1][project - 1]
        profit = profits[company - 1][project - 1]
        print(f"Company #{company}: Project #{project} (Cost: {cost}, Profit: {profit})")
        total_cost += cost
    print(f"Total cost: {total_cost}")

BUDGET = 20

# Comp1: (0, 0), (4, 15), (8, 27) (12, 39) (16, 60) (20, 71)
# Comp2: (0, 0), (4, 21), (8, 40) (12, 42) (16, 54) (20, 69)
# Comp3: (0, 0), (4, 25), (8, 45) (12, 47) (16, 60) (20, 80)
# Comp4: (0, 0), (4, 19), (8, 39) (12, 52) (16, 82) (20, 90)

# COSTS = [[0,4,8,12,16,20],
#          [0,4,8,12,16,20],
#          [0,4,8,12,16,20],
#          [0,4,8,12,16,20]]

# PROFITS = [[0,15,27,39,60,71],
#            [0,21,40,42,54,69],
#            [0,25,45,47,60,80],
#            [0, 19, 39, 52, 82, 90]]

COSTS = [
    [2, 2, 2, 3, 4],
    [3, 4, 2, 3, 5],
    [3, 3, 1, 3, 3]
        ]

PROFITS = [
    [0.5, 0.4, 0.7, 0.9, 1],
    [0.8, 0.8, 0.7, 0.9, 1.3],
    [0.8, 0.6, 0.4, 0.9, 0.8]
         ]

find_optimal_investing_strategy(COSTS, PROFITS, BUDGET)
