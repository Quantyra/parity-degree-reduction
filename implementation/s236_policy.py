"""Reconstruction of S235. Inputs: explicit ANF, precision, random bits, parity oracle.

No reference checker, spectrum, generic rank, hidden input, or residual ANF is used.
Python operation counters describe this implementation, not unit-cost bit complexity.
"""
from dataclasses import dataclass, field


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def parity(value):
    return value.bit_count() & 1


def ceil_log2(value):
    return (value - 1).bit_length()


@dataclass
class Counters:
    values: dict = field(default_factory=dict)

    def inc(self, name, value=1):
        self.values[name] = self.values.get(name, 0) + value

    def maximum(self, name, value):
        self.values[name] = max(self.values.get(name, 0), value)


class Poly:
    """Exact binary polynomial/rational arithmetic with normalized fractions."""
    def __init__(self, counters):
        self.c = counters

    def track(self, value):
        self.c.maximum('max_polynomial_degree', max(0, value.bit_length() - 1))
        return value

    def mul(self, a, b):
        self.c.inc('polynomial_multiplications')
        out = 0
        while b:
            if b & 1:
                out ^= a
            a <<= 1
            b >>= 1
        return self.track(out)

    def divmod(self, a, b):
        if not b:
            raise ZeroDivisionError('zero polynomial divisor')
        self.c.inc('polynomial_divisions')
        out = 0
        while a and a.bit_length() >= b.bit_length():
            shift = a.bit_length() - b.bit_length()
            out ^= 1 << shift
            a ^= b << shift
        return out, a

    def exact(self, a, b):
        q, remainder = self.divmod(a, b)
        if remainder:
            raise ArithmeticError('inexact polynomial quotient')
        return q

    def fraction(self, a, b=1):
        if not b:
            raise ZeroDivisionError('zero rational denominator')
        if not a:
            return (0, 1)
        x, y = a, b
        while y:
            x, y = y, self.divmod(x, y)[1]
        out = self.exact(a, x), self.exact(b, x)
        self.c.maximum('max_normalized_rational_degree', max(v.bit_length() - 1 for v in out))
        return out

    def addf(self, a, b):
        self.c.inc('rational_operations')
        if not a[0]:
            return b
        if not b[0]:
            return a
        return self.fraction(self.mul(a[0], b[1]) ^ self.mul(b[0], a[1]),
                             self.mul(a[1], b[1]))

    def mulf(self, a, b):
        self.c.inc('rational_operations')
        if not a[0] or not b[0]:
            return (0, 1)
        return self.fraction(self.mul(a[0], b[0]), self.mul(a[1], b[1]))

    def divf(self, a, b):
        self.c.inc('rational_operations')
        return self.fraction(self.mul(a[0], b[1]), self.mul(a[1], b[0]))


def rank_minor(matrix, arith):
    """Full-pivot Schur elimination; returns actual rank and original minor indices."""
    m = len(matrix)
    work = [[(x, 1) for x in row] for row in matrix]
    row_ids, col_ids = list(range(m)), list(range(m))
    determinant = (1, 1)
    rank = 0
    D = max([x.bit_length() - 1 for row in matrix for x in row] + [0])
    arith.c.maximum('matrix_slots', m * m)
    while rank < m:
        found = next(((i, j) for i in range(rank, m) for j in range(rank, m)
                      if work[i][j][0]), None)
        if found is None:
            break
        i, j = found
        work[rank], work[i] = work[i], work[rank]
        row_ids[rank], row_ids[i] = row_ids[i], row_ids[rank]
        for row in work:
            row[rank], row[j] = row[j], row[rank]
        col_ids[rank], col_ids[j] = col_ids[j], col_ids[rank]
        pivot = work[rank][rank]
        determinant = arith.mulf(determinant, pivot)
        for i in range(rank + 1, m):
            if not work[i][rank][0]:
                continue
            scale = arith.divf(work[i][rank], pivot)
            for j in range(rank + 1, m):
                if work[rank][j][0]:
                    work[i][j] = arith.addf(work[i][j], arith.mulf(scale, work[rank][j]))
        rank += 1
        if determinant[1] != 1 or determinant[0].bit_length() - 1 > rank * D:
            raise ArithmeticError('pivot product degree/polynomial invariant')
        for i in range(rank, m):
            for j in range(rank, m):
                numerator, denominator = work[i][j]
                if numerator.bit_length() - 1 > (rank + 1) * D or denominator.bit_length() - 1 > rank * D:
                    raise ArithmeticError('Schur complement degree invariant')
    return rank, row_ids[:rank], col_ids[:rank], determinant[0]


def determinant(matrix, arith):
    if not matrix:
        return 1
    rank, _, _, value = rank_minor(matrix, arith)
    return value if rank == len(matrix) else 0


def rref(rows, variables):
    out = list(rows)
    pivots = []
    position = 0
    for j in range(variables):
        index = next((i for i in range(position, len(out)) if out[i] >> j & 1), None)
        if index is None:
            continue
        out[position], out[index] = out[index], out[position]
        for i in range(len(out)):
            if i != position and (out[i] >> j & 1):
                out[i] ^= out[position]
        pivots.append(j)
        position += 1
    return out, pivots


def nullspace(rows, variables):
    reduced, pivots = rref(rows, variables)
    pivot_set = set(pivots)
    output = []
    for j in range(variables):
        if j not in pivot_set:
            value = 1 << j
            for row, pivot in zip(reduced, pivots):
                if row >> j & 1:
                    value |= 1 << pivot
            output.append(value)
    return output


def particular(rows, answers, variables):
    augmented = [row | (((answers >> i) & 1) << variables) for i, row in enumerate(rows)]
    reduced, pivots = rref(augmented, variables)
    if len(pivots) != len(rows):
        raise ArithmeticError('dependent batch equations')
    return sum(((row >> variables) & 1) << pivot for row, pivot in zip(reduced, pivots))


def left_inverse(C, m):
    basis = {}
    for i, original_row in enumerate(C):
        row, certificate = original_row, 1 << i
        while row:
            lead = row.bit_length() - 1
            if lead not in basis:
                basis[lead] = row, certificate
                break
            row ^= basis[lead][0]
            certificate ^= basis[lead][1]
    if len(basis) != m:
        raise ArithmeticError('affine map is not injective')
    inverse = []
    for j in range(m):
        row, certificate = 1 << j, 0
        while row:
            lead = row.bit_length() - 1
            row ^= basis[lead][0]
            certificate ^= basis[lead][1]
        inverse.append(certificate)
    return inverse


def combination(rows, mask):
    out = 0
    for j in bits(mask):
        out ^= rows[j]
    return out


def column_dependency(G):
    m = len(G)
    nu = len(G[0]) if m else 0
    basis = {}
    for j in range(nu):
        column = sum((G[i][j] & 1) << i for i in range(m))
        certificate = 1 << j
        while column:
            lead = column.bit_length() - 1
            if lead not in basis:
                basis[lead] = column, certificate
                break
            column ^= basis[lead][0]
            certificate ^= basis[lead][1]
        if not column:
            return certificate
    return 0


def kernel_descent(matrix, rank, selected_rows, selected_cols, D, arith):
    m, nu = len(matrix), len(matrix) - rank
    if rank == m:
        return [0] * m, {'repairs': 0, 'initial': tuple(() for _ in range(m)),
                        'final': tuple(() for _ in range(m)), 'fixed_rows': (), 'delta': 1}
    free_cols = [j for j in range(m) if j not in selected_cols]
    G = [[0] * nu for _ in range(m)]
    if rank == 0:
        delta = 1
        for j in range(m):
            G[j][j] = 1
    else:
        P = [[matrix[i][j] for j in selected_cols] for i in selected_rows]
        delta = determinant(P, arith)
        if not delta:
            raise ArithmeticError('zero attaining minor')
        adj = [[determinant([[P[i][j] for j in range(rank) if j != a]
                             for i in range(rank) if i != b], arith)
                for b in range(rank)] for a in range(rank)]
        for j, free_col in enumerate(free_cols):
            for i, pivot_col in enumerate(selected_cols):
                value = 0
                for l in range(rank):
                    value ^= arith.mul(adj[i][l], matrix[selected_rows[l]][free_col])
                G[pivot_col][j] = value
            G[free_col][j] = delta
    initial = tuple(tuple(row) for row in G)
    repairs = 0
    while True:
        dependence = column_dependency(G)
        if not dependence:
            break
        j = (dependence & -dependence).bit_length() - 1
        for i in range(m):
            value = combination(G[i], dependence)
            if value & 1:
                raise ArithmeticError('repair is not divisible by t')
            G[i][j] = value >> 1
        repairs += 1
        if repairs > nu * rank * D or repairs >= m * m * (D + 1):
            raise ArithmeticError('repair exceeds proved budget')
    if any(value.bit_length() - 1 > rank * D for row in G for value in row):
        raise ArithmeticError('kernel basis degree grew')
    arith.c.inc('repairs', repairs)
    arith.c.maximum('max_basis_degree', max([x.bit_length() - 1 for row in G for x in row] + [0]))
    V = [sum((value & 1) << j for j, value in enumerate(row)) for row in G]
    return V, {'repairs': repairs, 'initial': initial, 'final': tuple(tuple(row) for row in G),
               'fixed_rows': tuple(free_cols), 'delta': delta}


def prepare_factors(source, a, C, m, r):
    prepared = []
    support = 0
    for monomial in source:
        factors = list(bits(monomial))
        if len(factors) < r:
            continue
        q = len(factors)
        common = [0] * (1 << q)
        common[0] = (1 << m) - 1
        for subset in range(1, 1 << q):
            low = subset & -subset
            common[subset] = common[subset ^ low] & C[factors[low.bit_length() - 1]]
        constants = []
        for subset in range(1 << q):
            constants.append(all((a >> factors[l]) & 1 for l in range(q) if not (subset >> l & 1)))
        for index in factors:
            support |= C[index]
        prepared.append((q, common, constants))
    return prepared, support


def contraction(prepared, support, anchors, m, r, k, arith):
    """S234 recurrence, with exact zero-entry pruning and symmetric reuse."""
    matrix = [[0] * m for _ in range(m)]
    coefficient_caps = [(mask & ((1 << (r - 2)) - 1)).bit_count() * (k - 1)
                        for mask in range(1 << r)]
    anchor_vectors = []
    for q, common, constants in prepared:
        vectors = []
        for subset in range(1 << q):
            vectors.append([combination(h, common[subset]) for h in anchors])
        anchor_vectors.append((q, common, constants, vectors))
    active = list(bits(support))
    for ii, i in enumerate(active):
        for j in active[ii + 1:]:
            accumulator = 0
            for q, common, constants, vectors in anchor_vectors:
                F = [[0] * (1 << r) for _ in range(1 << q)]
                F[0][0] = 1
                arith.c.maximum('dp_slots', (1 << (q + r)) + r * (1 << q))
                for subset in range(1, 1 << q):
                    first = subset & -subset
                    block = subset
                    while block:
                        if block & first:
                            v = vectors[block] + [(common[block] >> i) & 1, (common[block] >> j) & 1]
                            previous = F[subset ^ block]
                            for mask, value in enumerate(previous):
                                if value:
                                    for slot, multiplier in enumerate(v):
                                        if multiplier and not (mask >> slot & 1):
                                            F[subset][mask | (1 << slot)] ^= arith.mul(value, multiplier)
                        block = (block - 1) & subset
                    if any(value.bit_length() - 1 > coefficient_caps[mask]
                           for mask, value in enumerate(F[subset])):
                        raise ArithmeticError('component coefficient degree cap')
                for subset in range(1 << q):
                    if constants[subset]:
                        accumulator ^= F[subset][-1]
            matrix[i][j] = matrix[j][i] = accumulator
            arith.c.inc('contraction_entries')
    arith.c.inc('pruned_or_reused_entries', m * m - len(active) * (len(active) - 1) // 2)
    return matrix


class Policy:
    def __init__(self, n, monomials, b, tape, oracle, observer=None):
        if n < 0 or b < 2:
            raise ValueError('invalid n or precision')
        normalized = set()
        for mask in monomials:
            if not isinstance(mask, int) or mask < 0 or mask.bit_length() > n:
                raise ValueError('invalid explicit monomial')
            if mask in normalized:
                normalized.remove(mask)
            else:
                normalized.add(mask)
        self.n, self.b, self.source = n, b, tuple(sorted(normalized))
        self.d = max([mask.bit_count() for mask in self.source] + [0])
        self.tape, self.oracle = tape, oracle
        self.observer = observer
        self.c = Counters()
        self.poly = Poly(self.c)
        self.transcript = []
        self.path = []

    def emit(self, kind, **data):
        if self.observer is not None:
            self.observer(kind, data)

    def source_value(self, x):
        self.c.inc('source_evaluations')
        value = 0
        for mask in self.source:
            value ^= (x & mask) == mask
        return int(value)

    def residual_value(self, a, C, z):
        return self.source_value(a ^ sum(parity(row & z) << i for i, row in enumerate(C)))

    def ask(self, residual_mask, inverse, a, label):
        original_mask = combination(inverse, residual_mask)
        if not original_mask or original_mask.bit_length() > self.n:
            raise ArithmeticError('invalid lifted parity')
        if len(self.transcript) >= self.n:
            raise ArithmeticError('unconditional query cap exceeded')
        answer = self.oracle(original_mask)
        if answer not in (0, 1):
            raise ValueError('oracle is not binary')
        offset = parity(original_mask & a)
        row = {'original_mask': original_mask, 'residual_mask': residual_mask,
               'answer': answer, 'offset': offset, 'corrected': answer ^ offset, 'label': label}
        self.transcript.append(row)
        self.c.inc('query_description_bits', self.n)
        self.emit('query', **row)
        return answer ^ offset

    def leaf(self, a, C, m):
        if m == 0:
            return self.source_value(a)
        constant = self.residual_value(a, C, 0)
        singles = [self.residual_value(a, C, 1 << i) ^ constant for i in range(m)]
        monomials = ([0] if constant else []) + [1 << i for i in range(m) if singles[i]]
        polar_rows = [0] * m
        for i in range(m):
            for j in range(i + 1, m):
                coefficient = self.residual_value(a, C, (1 << i) | (1 << j)) ^ singles[i] ^ singles[j] ^ constant
                if coefficient:
                    monomials.append((1 << i) | (1 << j))
                    polar_rows[i] |= 1 << j
                    polar_rows[j] |= 1 << i

        def form(x, y):
            return parity(combination(polar_rows, x) & y)

        basis = [1 << i for i in range(m)]
        paired = []
        while True:
            found = next(((i, j) for i in range(len(basis)) for j in range(i + 1, len(basis))
                          if form(basis[i], basis[j])), None)
            if found is None:
                break
            i, j = found
            v, w = basis[i], basis[j]
            paired.extend((v, w))
            rest = [x for pos, x in enumerate(basis) if pos not in (i, j)]
            basis = [x ^ (v if form(x, w) else 0) ^ (w if form(x, v) else 0) for x in rest]
        t = len(paired) // 2
        columns = paired + basis
        P_rows = [sum(((col >> i) & 1) << j for j, col in enumerate(columns)) for i in range(m)]
        CP = [combination(P_rows, row) for row in C]
        inverse = left_inverse(CP, m)

        def evaluate_quadratic(z):
            value = 0
            for mask in monomials:
                value ^= (z & mask) == mask
            return int(value)

        linear = sum((evaluate_quadratic(col) ^ constant) << j for j, col in enumerate(columns))
        before = len(self.transcript)
        known = constant
        remaining = linear
        for j in range(t):
            odd = 2 * j
            answer = self.ask(1 << odd, inverse, a, 'leaf_pair')
            if (linear >> odd) & 1:
                known ^= answer
            remaining &= ~(1 << odd)
            if answer:
                remaining ^= 1 << (odd + 1)
        if remaining:
            known ^= self.ask(remaining, inverse, a, 'leaf_affine')
        self.emit('leaf', a=a, C=tuple(C), m=m, quadratic=tuple(sorted(monomials)),
                  polar_rank=2 * t, P_columns=tuple(columns), linear=linear,
                  query_count=len(self.transcript) - before, output=known)
        self.path.append({'kind': 'leaf', 'm': m, 'polar_rank': 2 * t,
                          'queries': len(self.transcript) - before})
        return known

    def run(self):
        a, C, m = 0, [1 << i for i in range(self.n)], self.n
        if self.d <= 2:
            branch = 'low_degree'
            output = self.leaf(a, C, m)
        else:
            H_d = ((1 << (2 * self.d - 1)) - 8) // 3
            if 2 + H_d >= self.n:
                branch = 'read_all'
                known = 0
                for i in range(self.n):
                    known |= self.ask(1 << i, C, 0, 'read_all') << i
                output = self.source_value(known)
            else:
                branch = 'descent'
                k = ceil_log2(8 * self.n * self.d)
                samples = self.b + ceil_log2(2 * self.d)
                if (1 << (2 * self.d)) >= 6 * self.n + 4:
                    raise ArithmeticError('cutoff allocation invariant')
                for r in range(self.d, 2, -1):
                    if m == 0:
                        break
                    self.emit('stage_start', a=a, C=tuple(C), m=m, r=r)
                    prepared, support = prepare_factors(self.source, a, C, m, r)
                    best = None
                    ranks = []
                    for sample in range(samples):
                        anchors = [[self.tape.getrandbits(k) for _ in range(m)] for _ in range(r - 2)]
                        if any(value < 0 or value >= 1 << k for row in anchors for value in row):
                            raise ValueError('coefficient tape exceeded requested width')
                        self.c.inc('random_bits', k * m * (r - 2))
                        N = contraction(prepared, support, anchors, m, r, k, self.poly)
                        rank, rows, cols, _ = rank_minor(N, self.poly)
                        ranks.append(rank)
                        self.emit('sample', a=a, C=tuple(C), m=m, r=r, k=k, sample=sample,
                                  anchors=tuple(tuple(row) for row in anchors),
                                  N=tuple(tuple(row) for row in N), rank=rank,
                                  pivot_rows=tuple(rows), pivot_cols=tuple(cols))
                        if best is None or rank > best[0]:
                            best = rank, rows, cols, N, sample
                    rank, rows, cols, N, selected = best
                    D = (r - 2) * (k - 1)
                    V, detail = kernel_descent(N, rank, rows, cols, D, self.poly)
                    nu = m - rank
                    V_columns = [sum(((V[i] >> j) & 1) << i for i in range(m)) for j in range(nu)]
                    H = nullspace(V_columns, m)
                    if len(H) != rank:
                        raise ArithmeticError('wrong binary codimension')
                    self.emit('batch', a=a, C=tuple(C), m=m, r=r, k=k, rank=rank,
                              N=tuple(tuple(row) for row in N), V=tuple(V), H=tuple(H),
                              selected=selected, sample_ranks=tuple(ranks), **detail)
                    inverse = left_inverse(C, m)
                    answers = sum(self.ask(row, inverse, a, f'degree_{r}') << j for j, row in enumerate(H))
                    z0 = particular(H, answers, m)
                    next_a = a ^ sum(parity(row & z0) << i for i, row in enumerate(C))
                    next_C = [combination(V, row) for row in C]
                    self.emit('update', a=a, C=tuple(C), m=m, r=r, rank=rank, V=tuple(V), H=tuple(H),
                              answers=answers, z0=z0, next_a=next_a, next_C=tuple(next_C), next_m=nu)
                    self.path.append({'kind': 'batch', 'r': r, 'm': m, 'rank': rank,
                                      'queries': rank, 'repairs': detail['repairs'],
                                      'sample_ranks': ranks, 'selected': selected})
                    a, C, m = next_a, next_C, nu
                output = self.leaf(a, C, m)
        if len(self.transcript) > self.n:
            raise ArithmeticError('final query cap')
        return {'output': output, 'branch': branch, 'degree': self.d,
                'queries': len(self.transcript), 'transcript': self.transcript,
                'path': self.path, 'counters': self.c.values}
