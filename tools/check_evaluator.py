"""S234 preregistered exact diagnostic, not a full-policy implementation.

256 fixtures, seed 234, F4, n<=9,m<=5,D<=6,r<=5.
Run once under an external 120-second subprocess timeout. No dependencies.
"""

import hashlib
import itertools
import json
from pathlib import Path
import random
import time


def mul(a, b):
    """F2[t]/(t^2+t+1); low two bits store the polynomial."""
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def determinant(matrix):
    """Reference: exact Gaussian elimination, not an exterior calculation."""
    rows = [row[:] for row in matrix]
    result = 1
    for j in range(len(rows)):
        pivot = next((i for i in range(j, len(rows)) if rows[i][j]), None)
        if pivot is None:
            return 0
        rows[j], rows[pivot] = rows[pivot], rows[j]
        pivot_value = rows[j][j]
        result = mul(result, pivot_value)
        inverse = mul(pivot_value, pivot_value)
        for k in range(j, len(rows)):
            rows[j][k] = mul(rows[j][k], inverse)
        for i in range(j + 1, len(rows)):
            scale = rows[i][j]
            for k in range(j, len(rows)):
                rows[i][k] ^= mul(scale, rows[j][k])
    return result


def truth_table_reference(case):
    """Boolean source evaluation, Mobius reduction, then determinants."""
    n, m, monomials, a, rows, h = (
        case[key] for key in ('n', 'm', 'monomials', 'a', 'rows', 'h')
    )
    coefficients = []
    for z in range(1 << m):
        x = [a[i] ^ ((rows[i] & z).bit_count() & 1) for i in range(n)]
        value = 0
        for monomial in monomials:
            value ^= int(all(x[i] for i in monomial))
        coefficients.append(value)
    for j in range(m):
        for mask in range(1 << m):
            if mask & (1 << j):
                coefficients[mask] ^= coefficients[mask ^ (1 << j)]
    result = 0
    r = len(h)
    for mask, coefficient in enumerate(coefficients):
        if coefficient and mask.bit_count() == r:
            columns = [j for j in range(m) if mask & (1 << j)]
            result ^= determinant([[direction[j] for j in columns] for direction in h])
    actual_degree = max((mask.bit_count() for mask, c in enumerate(coefficients) if c), default=0)
    return result, actual_degree


def partition_evaluator(case):
    """Proposed evaluator: grouping factor fibers BEFORE exterior products."""
    m, monomials, a, rows, h = (
        case[key] for key in ('m', 'monomials', 'a', 'rows', 'h')
    )
    r = len(h)
    result = 0
    for monomial in monomials:
        degree = len(monomial)
        vectors = [[0] * r for _ in range(1 << degree)]
        for block in range(1, 1 << degree):
            common = (1 << m) - 1
            for position, original in enumerate(monomial):
                if block & (1 << position):
                    common &= rows[original]
            for j in range(m):
                if common & (1 << j):
                    for i in range(r):
                        vectors[block][i] ^= h[i][j]
        table = [[0] * (1 << r) for _ in range(1 << degree)]
        table[0][0] = 1
        # Proper subsets are smaller as binary integers, hence available.
        for subset in range(1, 1 << degree):
            least = subset & -subset
            block = subset
            while block:
                if block & least:
                    previous = table[subset ^ block]
                    for mask, coefficient in enumerate(previous):
                        if coefficient:
                            for i, scalar in enumerate(vectors[block]):
                                if scalar and not mask & (1 << i):
                                    table[subset][mask | (1 << i)] ^= mul(coefficient, scalar)
                block = (block - 1) & subset
        for subset in range(1 << degree):
            if all(a[original] for position, original in enumerate(monomial)
                   if not subset & (1 << position)):
                result ^= table[subset][-1]
    return result


def fixture(name, n, m, monomials, a, rows, h, expected=None):
    return dict(name=name, n=n, m=m, monomials=monomials, a=a, rows=rows,
                h=h, expected=expected)


def fixtures():
    cases = [
        fixture('z_squared_plus_z', 2, 1, [(0, 1), (0,)], [0, 0], [1, 1], [[2]], 0),
        fixture('quartic_to_cubic', 4, 3, [(0, 1, 2, 3)], [0]*4, [1, 1, 2, 4],
                [[2, 0, 0], [0, 1, 0], [0, 0, 1]], 2),
        fixture('above_order_component', 3, 3, [(0, 1, 2), (0,)], [0]*3, [1, 2, 4],
                [[2, 2, 2]], 2),
        fixture('below_order', 2, 2, [(0,), (1,), ()], [1, 0], [1, 2],
                [[2, 0], [0, 3]], 0),
        fixture('repeated_directions', 3, 3, [(0, 1, 2)], [0]*3, [1, 2, 4],
                [[2, 1, 3], [2, 1, 3], [1, 2, 0]], 0),
        fixture('zero_direction', 3, 3, [(0, 1, 2)], [0]*3, [1, 2, 4],
                [[0, 0, 0], [1, 2, 3], [3, 2, 1]], 0),
        fixture('affine_offsets', 3, 2, [(0, 1), (2,), ()], [1, 1, 0], [1, 2, 3],
                [[2, 0], [0, 3]], 1),
        fixture('offset_cancellation', 2, 1, [(0, 1), (0,)], [1, 1], [1, 1], [[3]], 0),
        fixture('constant_source', 0, 0, [()], [], [], [[]], 0),
        fixture('order_exceeds_dimension', 2, 1, [(0, 1)], [1, 0], [1, 1], [[1], [2]], 0),
    ]
    rng = random.Random(234)
    while len(cases) < 256:
        n, m = rng.randint(1, 9), rng.randint(1, 5)
        degree = rng.randint(1, min(n, 6))
        possible = [tuple(indices) for order in range(degree + 1)
                    for indices in itertools.combinations(range(n), order)]
        monomials = rng.sample(possible, min(len(possible), rng.randint(1, 20)))
        a = [rng.randrange(2) for _ in range(n)]
        rows = [rng.randrange(1 << m) for _ in range(n)]
        r = rng.randint(1, 5)
        h = [[rng.randrange(4) for _ in range(m)] for _ in range(r)]
        cases.append(fixture('seed234_%03d' % len(cases), n, m, monomials, a, rows, h))
    return cases


def main():
    started = time.perf_counter()
    expected_table = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]
    assert [[mul(a, b) for b in range(4)] for a in range(4)] == expected_table
    cases = fixtures()
    digest = hashlib.sha256(json.dumps(cases, sort_keys=True).encode('utf-8')).hexdigest()
    degree_relations = {'below': 0, 'equal': 0, 'above': 0}
    controls = []
    for index, case in enumerate(cases):
        assert case['n'] <= 9 and case['m'] <= 5 and 1 <= len(case['h']) <= 5
        assert max(map(len, case['monomials']), default=0) <= 6
        actual = partition_evaluator(case)
        reference, degree = truth_table_reference(case)
        if actual != reference or (case['expected'] is not None and actual != case['expected']):
            print(json.dumps({'status': 'FAIL', 'index': index, 'case': case,
                              'actual': actual, 'reference': reference}, sort_keys=True))
            raise SystemExit(1)
        r = len(case['h'])
        relation = 'below' if degree < r else ('equal' if degree == r else 'above')
        degree_relations[relation] += 1
        if index < 10:
            controls.append({'name': case['name'], 'value': actual, 'canonical_degree': degree, 'r': r})
    print(json.dumps({
        'status': 'PASS', 'fixtures': len(cases), 'seed': 234,
        'field': 'F2[t]/(t^2+t+1)', 'fixture_sha256': digest,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'caps': {'n': 9, 'm': 5, 'source_monomial_degree': 6, 'r': 5, 'fixtures': 256},
        'degree_relations': degree_relations, 'controls': controls,
        'elapsed_seconds': time.perf_counter() - started,
        'scope': 'Exact evaluator diagnostic only; no full-policy implementation or asymptotic verification.'
    }, sort_keys=True))


if __name__ == '__main__':
    main()
