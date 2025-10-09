from config import M, A, C, X0

def lcg_generate_stream(n: int):
    x = X0
    for _ in range(n):
        x = (A * x + C) % M
        yield x

def lcg_stream(n: int, chunk_size: int = 10000):
    buffer = []
    for num in lcg_generate_stream(n):
        buffer.append(str(num))
        if len(buffer) >= chunk_size:
            yield "\n".join(buffer) + "\n"
            buffer.clear()
    if buffer:
        yield "\n".join(buffer) + "\n"

def get_lcg_params() -> dict:
    return {
        "M": M,
        "A": A,
        "C": C,
        "X0": X0
    }

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

def cesaro_test_stream(n: int):
    if n % 2 != 0:
        raise ValueError("N must be even for Cesaro test")
    count = 0
    num_pairs = n // 2
    gen = lcg_generate_stream(n)
    try:
        while True:
            a = next(gen)
            b = next(gen)
            if gcd(a, b) == 1:
                count += 1
    except StopIteration:
        pass
    p = count / num_pairs if num_pairs > 0 else 0
    return (6 / p) ** 0.5 if p > 0 else None