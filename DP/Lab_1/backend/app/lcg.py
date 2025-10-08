from config import M, A, C, X0

def lcg_generate(n: int):
    seq = [0] * n
    x = X0
    for i in range(n):
        x = (A * x + C) % M
        seq[i] = x
    return seq

def lcg_stream(n: int, chunk_size: int = 10000):
    buffer = []
    for s in map(str, lcg_generate(n)):  
        buffer.append(s)
        if len(buffer) >= chunk_size:
            yield "\n".join(buffer) + "\n"
            buffer.clear()
    if buffer:
        yield "\n".join(buffer) + "\n"

def find_period():
    seen = set()
    x = X0
    period = 0
    while x not in seen:
        seen.add(x)
        x = (A * x + C) % M
        period += 1
    return period

def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a

def cesaro_test(sequence: list):
    count = 0
    num_pairs = len(sequence) // 2
    for i in range(0, len(sequence), 2):
        if i + 1 < len(sequence) and gcd(sequence[i], sequence[i + 1]) == 1:
            count += 1
    p = count / num_pairs if num_pairs > 0 else 0
    return (6 / p) ** 0.5 if p > 0 else None