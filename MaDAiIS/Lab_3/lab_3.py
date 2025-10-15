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

def get_user_input():
    print("\n=== Параметри моделі ===")
    num_cashiers = int(input("Введіть кількість касирів: "))
    num_ushers = int(input("Введіть кількість швейцарів: "))
    num_servers = int(input("Введіть кількість офіціантів: "))
    return num_cashiers, num_ushers, num_servers


def main():
    num_cashiers, num_ushers, num_servers = get_user_input()

    env = simpy.Environment()
    waiting_times = []

    env.process(run_theater(env, num_cashiers, num_ushers, num_servers, waiting_times))
    env.run(until=120) 

    average_wait = get_average_wait_time(waiting_times)
    formatted_time = calculate_wait_time(average_wait)

    print("\n=== Результати моделювання ===")
    print(f"Середній час очікування: {formatted_time}")
    print("==============================")

if __name__ == "__main__":
    main()
