import os
import simpy
import random
import statistics
import numpy as np
import matplotlib.pyplot as plt


PLOTS_PATH = "PythonApplications/MaDAiIS/Lab_4/plots"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

CHANELS_PER_CHAIN = [2, 3, 1]

KP = 6
KG = 2
KPRIG = 4

MAILS_NUM = KP * 2500
RATE = 0.4
TEST_RATES = [1, 2, 5, 10, 20, 50, 100]
SIM_TIME = 60 * 24 * 30
SEED = 42

MAX_QUEUE_WAIT = 0.2


class MailServer:
    def __init__(self, env, channels_per_chain=CHANELS_PER_CHAIN):
        self.env = env
        self.chain_resources = []

        for m in channels_per_chain:
            chain = [simpy.Resource(env, capacity=1) for _ in range(m)]
            self.chain_resources.append(chain)

        self.total_arrived = 0
        self.served = 0
        self.recieve_refusals = 0
        self.process_refusals = 0
        self.delivery_refusals = 0
        self.total_service_times = []

        self.queue_lengths = {i: [] for i in range(len(CHANELS_PER_CHAIN))}
        self.max_queue_lengths = {i: 0 for i in range(len(CHANELS_PER_CHAIN))}
        self.wait_times = {i: [] for i in range(len(CHANELS_PER_CHAIN))}
        self.max_wait_times = {i: 0 for i in range(len(CHANELS_PER_CHAIN))}

        self.Kp = KP
        self.Kg = KG
        self.Kprig = KPRIG

    def parse_stage(self, chain):
        m = len(chain)
        if m > 1:
            p_first = self.Kg / self.Kp
            p_other = self.Kprig / self.Kp / (m - 1)
            probs = [p_first] + [p_other] * (m - 1)
        else:
            probs = [1.0]
        return random.choices(range(m), weights=probs)[0]

    def service_time(self, chain_idx):
        if chain_idx == 0:
            return np.random.binomial(15, 0.8) * 0.01
        elif chain_idx == 1:
            return random.expovariate(1 / 0.5)
        elif chain_idx == 2:
            return np.random.binomial(12, 0.7) * 0.01

    def handle_stage(self, chain_idx):
        chain = self.chain_resources[chain_idx]
        channel_index = self.parse_stage(chain)
        channel = chain[channel_index]

        start_wait = self.env.now

        req = channel.request()

        result = yield req | self.env.timeout(MAX_QUEUE_WAIT)

        if req not in result:
            if chain_idx == 0:
                self.recieve_refusals += 1
            elif chain_idx == 1:
                self.process_refusals += 1
            else:
                self.delivery_refusals += 1

            req.cancel()
            return False

        q_len = len(channel.queue)
        self.queue_lengths[chain_idx].append(q_len)
        if q_len > self.max_queue_lengths[chain_idx]:
            self.max_queue_lengths[chain_idx] = q_len

        wait_time = self.env.now - start_wait
        self.wait_times[chain_idx].append(wait_time)
        if wait_time > self.max_wait_times[chain_idx]:
            self.max_wait_times[chain_idx] = wait_time

        st = self.service_time(chain_idx)
        yield self.env.timeout(st)

        channel.release(req)
        return True

    def receiving_stage(self):
        return self.handle_stage(0)

    def processing_stage(self):
        return self.handle_stage(1)

    def delivering_stage(self):
        return self.handle_stage(2)


def mail_process(env, name, server):
    server.total_arrived += 1
    arrival = env.now
    rejected = False

    if not (yield env.process(server.receiving_stage())):
        rejected = True
    elif not (yield env.process(server.processing_stage())):
        rejected = True
    elif not (yield env.process(server.delivering_stage())):
        rejected = True

    if not rejected:
        server.served += 1
        server.total_service_times.append(env.now - arrival)


def mail_generator(env, server, num_mails, arrival_rate):
    server.num_mails = num_mails
    server.rate = arrival_rate
    for i in range(num_mails):
        yield env.timeout(random.expovariate(arrival_rate))
        env.process(mail_process(env, f"Mail {i}", server))


def print_results(server):
    print(f"\n{YELLOW}=== General Statistics ==={RESET}") 
    print(f"Rate: {server.rate}")
    print(f"1 mail per {(1 / server.rate ):.2f} minutes")
    print(f"Per 1 minute {server.rate / 1:.2f} mails")

    print(f"Total mails generated: {server.total_arrived}/{server.num_mails} mails")
    served_percent = server.served / server.total_arrived if server.total_arrived > 0 else 0
    print(f"{GREEN}Successfully served: {server.served}/{server.total_arrived} = {served_percent * 100:.2f}%{RESET}")
    total_ref = server.recieve_refusals + server.process_refusals + server.delivery_refusals
    refusal_percent = total_ref / server.total_arrived if server.total_arrived > 0 else 0
    print(f"{RED}Total refusals: {total_ref}/{server.total_arrived} = {refusal_percent * 100:.2f}%{RESET}")

    print(f"\n{YELLOW}=== Refusal Details ==={RESET}")
    print(f"{RED}Receiving refusals: {server.recieve_refusals} mails{RESET}")
    print(f"{RED}Processing refusals: {server.process_refusals} mails{RESET}")
    print(f"{RED}Delivery refusals: {server.delivery_refusals} mails{RESET}")

    print(f"\n{YELLOW}=== Queue Statistics ==={RESET}")
    for i in range(len(server.chain_resources)):
        non_zero_queues = [q for q in server.queue_lengths[i] if q > 0]
        avg_q = statistics.mean(non_zero_queues) if non_zero_queues else 0

        non_zero_wait = [w for w in server.wait_times[i] if w > 0]
        avg_w = statistics.mean(non_zero_wait) if non_zero_wait else 0

        print(f"\n{YELLOW}Chain {i + 1}{RESET}:")
        print(f"  Average queue length: {avg_q:.2f} mails")
        print(f"  Max queue length: {server.max_queue_lengths[i]} mails")
        print(f"  Average waiting time: {avg_w:.2f} minutes")
        print(f"  Max waiting time: {server.max_wait_times[i]:.2f} minutes")

    avg_service_time = statistics.mean(server.total_service_times) if server.total_service_times else 0
    print(f"\n{YELLOW}Average total service time: {avg_service_time:.2f} minutes{RESET}")


def run_simulation(num_mails=MAILS_NUM, sim_time=SIM_TIME, arrival_rate=RATE, seed=SEED):
    if seed:
        random.seed(seed)
        np.random.seed(seed)

    env = simpy.Environment()
    server = MailServer(env)

    env.process(mail_generator(env, server, num_mails, arrival_rate))
    env.run(until=sim_time)

    print_results(server)
    return server


def build_combined_rate_analysis(results, folder=PLOTS_PATH):
    os.makedirs(folder, exist_ok=True)

    first_server = next(iter(results.values()))
    num_chains = len(first_server.queue_lengths)
    rate_multipliers = sorted(results.keys())
    n_rates = len(rate_multipliers)

    def collect_data(get_value_fn):
        values = [[] for _ in range(num_chains)]
        for rate in rate_multipliers:
            server = results[rate]
            for chain_idx in range(num_chains):
                values[chain_idx].append(get_value_fn(server, chain_idx))
        return values

    max_queues = collect_data(lambda s, i: s.max_queue_lengths[i])
    refusals = collect_data(
        lambda s, i: [
            s.recieve_refusals,
            s.process_refusals,
            s.delivery_refusals
        ][i]
    )

    def plot_grouped_bars(data, title, ylabel, filename):
        colors = plt.cm.viridis(np.linspace(0.2, 0.9, num_chains))
        x = np.arange(n_rates)
        width = 0.8 / num_chains
        plt.figure(figsize=(10, 6))
        for i in range(num_chains):
            plt.bar(
                x + i * width,
                data[i],
                width=width,
                color=colors[i],
                edgecolor="black",
                alpha=0.9,
                label=f"Chain {i + 1}"
            )
        plt.xticks(x + width * (num_chains / 2 - 0.5), [str(r) for r in rate_multipliers])
        plt.title(title, fontsize=14, fontweight="bold")
        plt.xlabel("Rate multiplier", fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.legend(title="Chains")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        path = f"{folder}/{filename}"
        plt.savefig(path, dpi=200)
        plt.close()
        print(f"Saved: {path}")

    plot_grouped_bars(max_queues, "Max Queue Length vs Rate (All Chains)",
                      "Max queue length", "combined_max_queue_vs_rate.png")
    plot_grouped_bars(refusals, "Refusals vs Rate (All Chains)",
                      "Number of refusals", "combined_refusals_vs_rate.png")


def build_queue_load_vs_rate(results, folder=PLOTS_PATH):
    os.makedirs(folder, exist_ok=True)

    first_server = next(iter(results.values()))
    num_chains = len(first_server.queue_lengths)
    rate_multipliers = sorted(results.keys())

    queue_loads = [[] for _ in range(num_chains)]
    for rate in rate_multipliers:
        server = results[rate]
        for chain_idx in range(num_chains):
            data = server.queue_lengths[chain_idx]
            non_zero_count = sum(1 for q in data if q > 0)
            queue_loads[chain_idx].append(non_zero_count)

    plt.figure(figsize=(10, 6))
    colors = plt.cm.plasma(np.linspace(0.2, 0.9, num_chains))

    for i in range(num_chains):
        plt.plot(
            rate_multipliers,
            queue_loads[i],
            marker="o",
            linestyle="-",
            linewidth=2,
            color=colors[i],
            label=f"Chain {i + 1}"
        )

    plt.title("Queue Activity vs Rate (All Chains)", fontsize=14, fontweight="bold")
    plt.xlabel("Rate multiplier", fontsize=12)
    plt.ylabel("Queue occurrences (times queue > 0)", fontsize=12)
    plt.grid(alpha=0.3)
    plt.legend(title="Chains")
    plt.tight_layout()

    path = f"{folder}/combined_queue_load_vs_rate.png"
    plt.savefig(path, dpi=200)
    plt.close()
    print(f"Saved: {path}")


def test_simulation(test_rates=TEST_RATES):
    test_result = {i: [] for i in test_rates}
    for rate in test_rates:
        test_result[rate] = run_simulation(arrival_rate=RATE * rate)
        input("Press Enter to continue...")
    return test_result


if __name__ == "__main__":
    results = test_simulation()
    
    build_combined_rate_analysis(results)
    build_queue_load_vs_rate(results)
