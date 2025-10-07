import numpy as np
import pandas as pd
from scipy.optimize import linprog
import copy 
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx


def balance_transport_problem(suppliers, consumers, supply, demand, costs):
    total_supply = supply.sum()
    total_demand = demand.sum()

    if total_supply > total_demand:
        consumers.append("Dummy_Consumer")
        demand = np.append(demand, total_supply - total_demand)
        extra_col = np.zeros((costs.shape[0], 1))
        costs = np.hstack([costs, extra_col])
    elif total_demand > total_supply:
        suppliers.append("Dummy_Supplier")
        supply = np.append(supply, total_demand - total_supply)
        extra_row = np.zeros((1, costs.shape[1]))
        costs = np.vstack([costs, extra_row])

    return suppliers, consumers, supply, demand, costs

def build_constraints(supply, demand):
    n_suppliers = len(supply)
    n_consumers = len(demand)
    n_vars = n_suppliers * n_consumers

    A_supply = np.zeros((n_suppliers, n_vars))
    for i in range(n_suppliers):
        A_supply[i, i*n_consumers:(i+1)*n_consumers] = 1
    b_supply = supply

    A_demand = np.zeros((n_consumers, n_vars))
    for j in range(n_consumers):
        A_demand[j, j::n_consumers] = 1
    b_demand = demand

    return A_supply, b_supply, A_demand, b_demand

def solve_transport(costs, supply, demand):

    c = costs.flatten()

    num_suppliers = len(supply)
    num_consumers = len(demand)

    # bounds = [(0, None) for _ in range(num_suppliers * num_consumers)]

    # i, j = 1, 1  
    # route_index = i * num_consumers + j
    # bounds[route_index] = (0, 0) 

    bounds = (0, None)

    A_supply, b_supply, A_demand, b_demand = build_constraints(supply, demand)

    res = linprog(
        c,
        A_ub=A_supply, b_ub=b_supply,
        A_eq=A_demand, b_eq=b_demand,
        bounds=bounds,
        method="highs"
    )

    if not res.success:
        raise ValueError("The transport problem has no solution.")

    plan = res.x.reshape(len(supply), len(demand))
    total_cost = res.fun

    shadow_prices = res.eqlin.marginals if hasattr(res.eqlin, 'marginals') else None

    if hasattr(res.lower, 'marginals') and hasattr(res.upper, 'marginals'):
        lower_marginals = res.lower.marginals.reshape(len(supply), len(demand))
        upper_marginals = res.upper.marginals.reshape(len(supply), len(demand))
    else:
        lower_marginals = None
        upper_marginals = None

    return plan, total_cost, shadow_prices, lower_marginals, upper_marginals

def display_plan(plan, suppliers, consumers, supply=None, demand=None):

    df = pd.DataFrame(plan, index=suppliers, columns=consumers)

    df['Supply'] = df.sum(axis=1) if supply is None else supply

    demand_row = df[consumers].sum(axis=0) if demand is None else demand
    demand_row = pd.Series(list(demand_row) + [None], index=df.columns)  
    demand_row.name = 'Demand'
    df = pd.concat([df, demand_row.to_frame().T])

    print(df.round(2))

def parametric_analysis(costs, supply, demand, suppliers, consumers, routes, percent_range=(-20, 20), steps=5):
    base_plan, *_ = solve_transport(costs, supply, demand)
    base_nonzero = set(zip(*np.where(base_plan > 1e-6)))

    percents = np.linspace(percent_range[0], percent_range[1], steps)

    for p in percents:
        new_costs = copy.deepcopy(costs)

        for (i, j) in routes:
            new_costs[i, j] = costs[i, j] * (1 + p/100)

        plan, total_cost, *_ = solve_transport(new_costs, supply, demand)
        nonzero = set(zip(*np.where(plan > 1e-6)))

        if nonzero != base_nonzero:
            print(f"\n=== Percentage: {p:.1f}% ===")
            print("Optimal transport cost:", total_cost)
            print("Optimal transport plan:")

            changed_routes = []
            for i in range(plan.shape[0]):
                for j in range(plan.shape[1]):
                    was_nonzero = (i, j) in base_nonzero
                    is_nonzero = plan[i, j] > 1e-6
                    if was_nonzero and is_nonzero:
                        if abs(plan[i,j] - base_plan[i,j]) > 1e-6:
                            changed_routes.append(f"\033[93m{suppliers[i]} -> {consumers[j]} ({base_plan[i,j]:.1f} → {plan[i,j]:.1f})\033[0m")
                    elif not was_nonzero and is_nonzero:
                        changed_routes.append(f"\033[94m{suppliers[i]} -> {consumers[j]} (0 → {plan[i,j]:.1f})\033[0m")

            print("Modified routes:")
            for r in changed_routes:
                print(r)

            display_plan(plan, suppliers, consumers)

def parametric_supply_demand(costs, supply, demand, suppliers, consumers, 
                             vary_type='supply', index=0, percent_range=(-20,20), steps=5):

    base_plan, *_ = solve_transport(costs, supply, demand)
    base_nonzero = set(zip(*np.where(base_plan > 1e-6)))

    percents = np.linspace(percent_range[0], percent_range[1], steps)

    for p in percents:
        new_supply = supply.copy()
        new_demand = demand.copy()

        if vary_type == 'supply':
            new_supply[index] = supply[index] * (1 + p/100)
        elif vary_type == 'demand':
            new_demand[index] = demand[index] * (1 + p/100)
        else:
            raise ValueError("vary_type must be 'supply' or 'demand'")

        s_list = suppliers.copy()
        c_list = consumers.copy()
        s_list, c_list, new_supply, new_demand, new_costs = balance_transport_problem(
            s_list, c_list, new_supply, new_demand, costs
        )

        plan, total_cost, *_ = solve_transport(new_costs, new_supply, new_demand)
        nonzero = set(zip(*np.where(plan > 1e-6)))

        if nonzero != base_nonzero:
            print(f"\n=== {vary_type.capitalize()} {index} change: {p:.1f}% ===")
            print("Optimal transport cost:", total_cost)
            print("Optimal transport plan:")

            changed_routes = []
            for i in range(plan.shape[0]):
                for j in range(plan.shape[1]):
                    was_nonzero = (i, j) in base_nonzero
                    is_nonzero = plan[i, j] > 1e-6
                    if was_nonzero and is_nonzero:
                        if abs(plan[i,j] - base_plan[i,j]) > 1e-6:
                            changed_routes.append(f"\033[93m{s_list[i]} -> {c_list[j]} ({base_plan[i,j]:.1f} → {plan[i,j]:.1f})\033[0m   y")
                    elif not was_nonzero and is_nonzero:
                        changed_routes.append(f"\033[94m{s_list[i]} -> {c_list[j]} (0 → {plan[i,j]:.1f})\033[0m   b")

            print("Modified routes:")
            for r in changed_routes:
                print(r)

            display_plan(plan, s_list, c_list)

def visualize_heatmaps(costs, plan, suppliers, consumers):
    # Теплокарта вартостей
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    sns.heatmap(costs, annot=True, fmt=".0f", xticklabels=consumers, yticklabels=suppliers, cmap="YlOrRd")
    plt.title("Cost matrix")

    # Теплокарта плану
    plt.subplot(1, 2, 2)
    sns.heatmap(plan, annot=True, fmt=".1f", xticklabels=consumers, yticklabels=suppliers, cmap="YlGnBu")
    plt.title("Optimal transport plan")

    plt.tight_layout()
    plt.show()

def visualize_network(plan, suppliers, consumers, shadow_prices=None):
    G = nx.DiGraph()

    for s in suppliers:
        G.add_node(s, type='supplier', shadow=0)
    for j, c in enumerate(consumers):
        shadow = shadow_prices[j] if shadow_prices is not None else 0
        G.add_node(c, type='consumer', shadow=shadow)

    for i, s in enumerate(suppliers):
        for j, c in enumerate(consumers):
            if plan[i, j] > 1e-6:
                G.add_edge(s, c, weight=plan[i, j])

    pos = {s: (0, -i) for i, s in enumerate(suppliers)}
    pos.update({c: (2, -j) for j, c in enumerate(consumers)})

    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1500)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, width=2)

    node_labels = {n: f"{n}\n{d['shadow']:.2f}" for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)

    edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_color='red', font_size=10,
        label_pos=0.5, rotate=False 
    )

    plt.title("Transport Network")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    suppliers = ["Rivne", "Yevpatoria", "Voznesensk"]
    consumers = ["Vinnytsia", "Odesa", "Lviv", "Obolon", "Dnipro"]

    supply = np.array([50, 70, 40])
    demand = np.array([50, 50, 40, 35, 30])

    costs = np.array([
        [316, 744, 211, 333, 814],
        [1090, 907, 1462, 1935, 1349],
        [343, 188, 714, 405, 315]
    ])

    suppliers, consumers, supply, demand, costs = balance_transport_problem(
        suppliers, consumers, supply, demand, costs
    )

    print("Balanced transport problem:")
    display_plan(costs, suppliers, consumers, supply=supply, demand=demand)
    print("Total supply =", supply.sum(), "| Total demand =", demand.sum())

    plan, total_cost, eqlin_marginals, lower_marginals, upper_marginals = solve_transport(costs, supply, demand)

    print("\nOptimal transport cost:", total_cost)
    print("\nOptimal transport plan:")
    display_plan(plan, suppliers, consumers)
    print("\nEqlin marginals:\n", eqlin_marginals)
    print("\nLower marginals:\n", lower_marginals)
    print("\nUpper marginals:\n", upper_marginals)

    # routes = [(0, 0), (2, 1)]  
    # parametric_analysis(costs, supply, demand, suppliers, consumers, routes, percent_range=(-30, 30), steps=7)

    # parametric_supply_demand(costs, supply, demand, suppliers, consumers, 
    #                      vary_type='supply', index=0, percent_range=(-30,30), steps=7)

    visualize_heatmaps(costs, plan, suppliers, consumers)
    visualize_network(plan, suppliers, consumers, shadow_prices=eqlin_marginals)