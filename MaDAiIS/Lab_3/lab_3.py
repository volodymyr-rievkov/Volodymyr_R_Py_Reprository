import simpy
import random
import statistics

class Hospital:
    def __init__(self, env, num_admins, num_doctors, num_labs, num_pharmacists, max_queue=5, patience=(10, 20)):
        self.env = env
        self.admins = simpy.Resource(env, num_admins)
        self.doctors = simpy.Resource(env, num_doctors)
        self.labs = simpy.Resource(env, num_labs)
        self.pharmacists = simpy.Resource(env, num_pharmacists)
        self.max_queue = max_queue
        self.patience = patience

        self.served = 0
        self.rejected = 0
        self.wait_times = []

    def register(self):
        yield self.env.timeout(random.uniform(1, 3))

    def consult_doctor(self):
        yield self.env.timeout(random.uniform(5, 20)) 

    def do_lab_test(self):
        yield self.env.timeout(random.uniform(3, 6))

    def get_medicine(self):
        yield self.env.timeout(random.uniform(1, 4)) 


def patient(env, name, clinic: Hospital):
    arrival = env.now
    patience = random.uniform(*clinic.patience)

    if len(clinic.admins.queue) >= clinic.max_queue:
        clinic.rejected += 1
        return

    with clinic.admins.request() as req:
        res = yield req | env.timeout(patience)
        if req not in res:
            clinic.rejected += 1
            return
        yield env.process(clinic.register())

    if len(clinic.doctors.queue) >= clinic.max_queue:
        clinic.rejected += 1
        return

    with clinic.doctors.request() as req:
        res = yield req | env.timeout(patience)
        if req not in res:
            clinic.rejected += 1
            return
        yield env.process(clinic.consult_doctor())

    if random.random() < 0.3:
        if len(clinic.labs.queue) >= clinic.max_queue:
            clinic.rejected += 1
            return

        with clinic.labs.request() as req:
            res = yield req | env.timeout(patience)
            if req not in res:
                clinic.rejected += 1
                return
            yield env.process(clinic.do_lab_test())

    if random.random() < 0.3:
        if len(clinic.pharmacists.queue) >= clinic.max_queue:
            clinic.rejected += 1
            return

        with clinic.pharmacists.request() as req:
            res = yield req | env.timeout(patience)
            if req not in res:
                clinic.rejected += 1
                return
            yield env.process(clinic.get_medicine())

        clinic.served += 1
        clinic.wait_times.append(env.now - arrival)


def patient_generator(env, clinic, arrival_rate):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1/arrival_rate))
        i += 1
        env.process(patient(env, f"Пацієнт {i}", clinic))


def run_simulation(num_admins, num_doctors, num_labs, num_pharmacists, arrival_rate, sim_time, seed=None):
    if seed is not None:
        random.seed(seed)
    
    env = simpy.Environment()
    clinic = Hospital(env, num_admins, num_doctors, num_labs, num_pharmacists)
    env.process(patient_generator(env, clinic, arrival_rate))
    env.run(until=sim_time)

    avg_wait = statistics.mean(clinic.wait_times) if clinic.wait_times else 0
    total = clinic.served + clinic.rejected
    p_refusal = clinic.rejected / total if total > 0 else 0

    return {
        "served": clinic.served,
        "rejected": clinic.rejected,
        "avg_wait": avg_wait,
        "p_refusal": p_refusal
    }


def calculate_wait_time(time_in_minutes):
    minutes = int(time_in_minutes)
    seconds = int((time_in_minutes - minutes) * 60)
    return f"{minutes} хв {seconds} сек"


def optimize_hospital_staff(
    target_minutes=20,
    max_workers=8,
    seed=42,
    arrival_rate=3.5,
    sim_time=480,
    fixed_admin=None,
    fixed_doctors=None,
    fixed_labs=None,
    fixed_pharmacists=None
):
    successful = []
    best_config = None
    best_time = float('inf')
    best_refusal = float('inf')

    admin_range = [fixed_admin] if fixed_admin is not None else range(1, max_workers + 1)
    doctors_range = [fixed_doctors] if fixed_doctors is not None else range(1, max_workers + 1)
    labs_range = [fixed_labs] if fixed_labs is not None else range(1, max_workers + 1)
    pharm_range = [fixed_pharmacists] if fixed_pharmacists is not None else range(1, max_workers + 1)

    for a in admin_range:
        for d in doctors_range:
            for l in labs_range:
                for p in pharm_range:
                    result = run_simulation(num_admins=a, num_doctors=d, num_labs=l, num_pharmacists=p, arrival_rate=arrival_rate, sim_time=sim_time, seed=seed)
                    if result["avg_wait"] <= target_minutes:
                        successful.append((a, d, l, p, result["avg_wait"], result["p_refusal"]))
                        print(f"✅ [Адміни: {a}, Лікарі: {d},  Лаборанти: {l}, Аптекарі: {p}] → {calculate_wait_time(result['avg_wait'])}, Відхилення: {result['p_refusal'] * 100}%")
                        if (result["p_refusal"] < best_refusal) or (
                            abs(result["p_refusal"] - best_refusal) < 1e-6 and result["avg_wait"] < best_time):
                            best_refusal = result["p_refusal"]
                            best_time = result["avg_wait"]
                            best_config = (a, d, l, p, result["avg_wait"], result["p_refusal"])

    print(f"Знайдено {len(successful)} комбінацій, де час ≤ {target_minutes} хв.")
    
    return successful, best_config


def main():

    successful, best = optimize_hospital_staff()
    if best:
        print("\n=== Найкраща комбінація ===")
        print(f"Адміни: {best[0]}, Лікарі: {best[1]},  Лаборанти: {best[2]}, Аптекарі: {best[3]}")
        print(f"Середній час: {calculate_wait_time(best[4])}")
        print(f"Відхилення: {best[5] * 100}%")
    else:
        print("\nЖодна комбінація не досягла цільового часу.")

    input("\nPress Enter to continue...")
    print("\n=== Оптимізація з фіксованим рейтом ===")
    result = run_simulation(num_admins=3, num_doctors=4, num_labs=2, num_pharmacists=2, arrival_rate=2, sim_time=480, seed=42)
    print(f"Обслужено: {result['served']}, Відхилено: {result['rejected']} → {calculate_wait_time(result['avg_wait'])}, Відхилення: {result['p_refusal'] * 100}%")


if __name__ == "__main__":
    main()