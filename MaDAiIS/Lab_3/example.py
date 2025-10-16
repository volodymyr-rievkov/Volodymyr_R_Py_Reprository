import simpy
import random
import statistics

class Theater:
    def __init__(self, env, num_cashiers, num_ushers, num_servers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)   
        self.usher = simpy.Resource(env, num_ushers)       
        self.server = simpy.Resource(env, num_servers)     

    def purchase_ticket(self):
        yield self.env.timeout(random.uniform(1, 3))  

    def check_ticket(self):
        yield self.env.timeout(0.05)  

    def sell_food(self):
        yield self.env.timeout(random.uniform(1, 5)) 


def go_to_movies(env, name, theater, waiting_times):
    arrival_time = env.now 

    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket())

    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket())

    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food())

    wait_time = env.now - arrival_time
    waiting_times.append(wait_time)

def run_theater(env, num_cashiers, num_ushers, num_servers, waiting_times):
    theater = Theater(env, num_cashiers, num_ushers, num_servers)

    for i in range(3):
        env.process(go_to_movies(env, f"Глядач {i}", theater, waiting_times))

    i = 3
    while True:
        yield env.timeout(0.2)
        i += 1
        env.process(go_to_movies(env, f"Глядач {i}", theater, waiting_times))

def get_average_wait_time(waiting_times):
    return statistics.mean(waiting_times) if waiting_times else 0

def calculate_wait_time(time_in_minutes):
    minutes = int(time_in_minutes)
    seconds = int((time_in_minutes - minutes) * 60)
    return f"{minutes} хв {seconds} сек"

def run_simulation(num_cashiers, num_ushers, num_servers, seed=None):
    if seed is not None:
        random.seed(seed)

    env = simpy.Environment()
    waiting_times = []

    env.process(run_theater(env, num_cashiers, num_ushers, num_servers, waiting_times))
    env.run(until=120) 

    average_wait = get_average_wait_time(waiting_times)
    formatted_time = calculate_wait_time(average_wait)
    return average_wait, formatted_time

def get_user_input():
    print("\n=== Параметри моделі ===")
    num_cashiers = int(input("Введіть кількість касирів: "))
    num_ushers = int(input("Введіть кількість швейцарів: "))
    num_servers = int(input("Введіть кількість офіціантів: "))
    return num_cashiers, num_ushers, num_servers

def full_optimize_staff(
    target_minutes=10,
    max_workers=10,
    seed=42,
    fixed_cashiers=None,
    fixed_ushers=None,
    fixed_servers=None
):
    successful = []
    best_config = None
    best_time = float('inf')

    cashiers_range = [fixed_cashiers] if fixed_cashiers is not None else range(1, max_workers + 1)
    ushers_range = [fixed_ushers] if fixed_ushers is not None else range(1, max_workers + 1)
    servers_range = [fixed_servers] if fixed_servers is not None else range(1, max_workers + 1)

    for cashiers in cashiers_range:
        for ushers in ushers_range:
            for servers in servers_range:
                avg_time, _ = run_simulation(cashiers, ushers, servers, seed=seed)

                if avg_time <= target_minutes:
                    successful.append((cashiers, ushers, servers, avg_time))
                    print(f"✅ [{cashiers}, {ushers}, {servers}] → {calculate_wait_time(avg_time)}")

                    total_staff = cashiers + ushers + servers
                    if (avg_time < best_time) or (
                        abs(avg_time - best_time) < 1e-6 and total_staff < sum(best_config[:3])):
                        best_time = avg_time
                        best_config = (cashiers, ushers, servers, avg_time)

    print("Пошук завершено.")
    print(f"Знайдено {len(successful)} таких комбінацій.")
    return successful, best_config

def main():

    # successful, best = full_optimize_staff()
    # if best:
    #     print("\n=== Найкраща комбінація ===")
    #     print(f"Касири: {best[0]}, Швейцари: {best[1]}, Офіціанти: {best[2]}")
    #     print(f"Середній час: {calculate_wait_time(best[3])}")
    # else:
    #     print("\nЖодна комбінація не досягла цільового часу.")

    # input("\nPress Enter to continue...")

    # successful, best = full_optimize_staff(target_minutes=9, fixed_cashiers=10)
    # if best:
    #     print("\n=== Найкраща комбінація ===")
    #     print(f"Касири: {best[0]}, Швейцари: {best[1]}, Офіціанти: {best[2]}")
    #     print(f"Середній час: {calculate_wait_time(best[3])}")
    # else:
    #     print("\nЖодна комбінація не досягла цільового часу.")

    # # input("\nPress Enter to continue...")

    # successful, best = full_optimize_staff(target_minutes=5)
    # if best:
    #     print("\n=== Найкраща комбінація ===")
    #     print(f"Касири: {best[0]}, Швейцари: {best[1]}, Офіціанти: {best[2]}")
    #     print(f"Середній час: {calculate_wait_time(best[3])}")
    # else:
    #     print("\nЖодна комбінація не досягла цільового часу.")
    
    input("\nPress Enter to continue...")

    num_cashiers=7
    num_ushers=10
    num_servers=8
    _, formatted_time = run_simulation(num_cashiers=num_cashiers, num_ushers=num_ushers, num_servers=num_servers, seed=42)
    print(f"Касири: {num_cashiers}, Швейцарі: {num_ushers}, Офіціанти: {num_servers}")
    print(f"Середній час: {formatted_time}")

if __name__ == "__main__":
    main()