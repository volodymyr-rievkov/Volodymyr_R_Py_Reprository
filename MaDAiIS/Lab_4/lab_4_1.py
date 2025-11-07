import simpy
import random
import statistics
import numpy as np

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
SIM_TIME = 60 * 24 * 30
SEED = 42

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

        self.Kp = KP
        self.Kg = KG
        self.Kprig = KPRIG

    def service_time(self, chain_idx):
        if chain_idx == 0:
            return np.random.binomial(15, 0.8) * 0.01
        elif chain_idx == 1:
            return random.expovariate(1 / 0.5)
        elif chain_idx == 2:
            return np.random.binomial(12, 0.7) * 0.01
    
    def parse_stage(self, chain):
        m = len(chain)
        if m > 1:
            p_first = self.Kg / self.Kp
            p_other = self.Kprig / self.Kp / (m - 1)
            probs = [p_first] + [p_other] * (m - 1)
        else:
            probs = [1.0]
        return random.choices(range(m), weights=probs)[0]

    def receiving_stage(self):  
        chain = self.chain_resources[0]
        channel = chain[self.parse_stage(chain)]
        if len(channel.users) == channel.capacity:
            self.recieve_refusals += 1
            return False
        with channel.request() as req:
            yield req
            st = self.service_time(0)
            yield self.env.timeout(st)
        return True

    def processing_stage(self):  
        chain = self.chain_resources[1]
        channel = chain[self.parse_stage(chain)]
        if len(channel.users) == channel.capacity:
            self.process_refusals += 1
            return False
        with channel.request() as req:
            yield req
            st = self.service_time(1)
            yield self.env.timeout(st)
        return True

    def delivering_stage(self): 
        chain = self.chain_resources[2]
        channel = chain[self.parse_stage(chain)]
        if len(channel.users) == channel.capacity:
            self.delivery_refusals += 1
            return False
        with channel.request() as req:
            yield req
            st = self.service_time(2)
            yield self.env.timeout(st)
        return True

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

    avg_service_time = statistics.mean(server.total_service_times) if server.total_service_times else 0
    print(f"\n{YELLOW}Average total service time: {avg_service_time:.4f} minutes{RESET}")

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


if __name__ == "__main__":
    run_simulation()
    