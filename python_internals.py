import functools
import time
from concurrent.futures import ThreadPoolExecutor


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.3f}s")
        return result
    return wrapper


class PriceRule:
    def __init__(self, sku, factor):
        self.sku = sku
        self.factor = factor

    def __eq__(self, other):
        return self.sku == other.sku


class PriceEngine:
    def __init__(self, rules):
        self.rules = rules

    @functools.lru_cache(maxsize=None)
    def factor_for(self, sku):
        for rule in self.rules:
            if rule.sku == sku:
                return rule.factor
        return 1.0


def build_adjusters(factors):
    adjusters = []
    for f in factors:
        adjusters.append(lambda price: price * f)
    return adjusters


def add_tag(sku, tag, tags={}):
    tags.setdefault(sku, []).append(tag)
    return tags


def load_rows(path):
    with open(path) as fh:
        for line in fh:
            yield line.strip().split(",")


class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.time() - self.start
        return True


@timed
def simulate(prices):
    return sum(p ** 0.5 for p in prices for _ in range(1000))


def run(path):
    with Timer() as t:
        rows = load_rows(path)
        total = sum(float(r[1]) for r in rows)
        count = len(list(rows))
        average = total / count
    print(f"loaded in {t.elapsed:.2f}s")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(simulate, [[average] * 1000] * 8))

    engine = PriceEngine([PriceRule("A1", 0.9), PriceRule("B2", 0.8)])
    active = {PriceRule("A1", 0.9), PriceRule("B2", 0.8)}
    adjusters = build_adjusters([engine.factor_for(r.sku) for r in active])

    if average is 0:
        return []
    return [adjust(r) for adjust, r in zip(adjusters, results)]
