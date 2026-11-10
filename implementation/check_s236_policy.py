"""Frozen exact reference for 21 complete S235 trajectories; never imported by policy."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import time

# The pinned embedded Windows Python uses an isolated ._pth search path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from s236_policy import Policy


TOTAL = {'assertions': 0, 'sample_matrices': 0, 'cosets': 0, 'strong_derivatives': 0,
         'negative_transcripts': 0, 'max_reference_terms': 0, 'max_truth_table': 0}


def require(condition, message):
    TOTAL['assertions'] += 1
    if not condition:
        raise AssertionError(message)


def indices(mask):
    return [j for j in range(mask.bit_length()) if (mask >> j) & 1]


def rsum(values):
    out = 0
    for value in values:
        out ^= value
    return out


def pmul(a, b):
    return rsum(b << j for j in indices(a))


def pdet(matrix):
    n = len(matrix)
    require(n <= 4, 'reference determinant allocation')
    value = 0
    for permutation in itertools.permutations(range(n)):
        term = 1
        for i, j in enumerate(permutation):
            term = pmul(term, matrix[i][j])
            if not term:
                break
        value ^= term
    return value


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = vector
                break
            vector ^= pivots[bit]
    return len(pivots)


def bxor_insert(target, value):
    if value in target:
        target.remove(value)
    else:
        target.add(value)


def normalize(monomials):
    out = set()
    for mask in monomials:
        bxor_insert(out, mask)
    return out


def beval(monomials, point):
    return sum((point & mask) == mask for mask in monomials) & 1


def compose(monomials, offset, rows):
    """Independent Boolean substitution: multiply factors by mask union, then XOR."""
    output = set()
    for mask in monomials:
        product = {0}
        for variable in indices(mask):
            factor = ([0] if (offset >> variable) & 1 else []) + [1 << j for j in indices(rows[variable])]
            new_product = set()
            for term in product:
                for value in factor:
                    bxor_insert(new_product, term | value)
            product = new_product
        output.symmetric_difference_update(product)
        require(len(output) <= 8192, 'reference ANF allocation')
    TOTAL['max_reference_terms'] = max(TOTAL['max_reference_terms'], len(output))
    return output


def degree(monomials):
    return max([mask.bit_count() for mask in monomials] + [0])


def spectrum_norm(monomials):
    active = sorted(set(j for mask in monomials for j in indices(mask)))
    require(len(active) <= 13, 'truth-table support cap')
    reduced = {sum(((mask >> j) & 1) << k for k, j in enumerate(active)) for mask in monomials}
    table = [1 - 2 * beval(reduced, x) for x in range(1 << len(active))]
    TOTAL['max_truth_table'] = max(TOTAL['max_truth_table'], len(table))
    step = 1
    while step < len(table):
        for start in range(0, len(table), 2 * step):
            for j in range(start, start + step):
                a, b = table[j], table[j + step]
                table[j], table[j + step] = a + b, a - b
        step *= 2
    return Fraction(sum(abs(x) for x in table), len(table))


def transcript_valid(transcript, x, n):
    rows = []
    for entry in transcript:
        mask = entry['original_mask']
        if not (0 < mask < (1 << n)) or entry['answer'] != ((mask & x).bit_count() & 1):
            return False
        if entry['corrected'] != (entry['answer'] ^ entry['offset']):
            return False
        rows.append(mask)
    return len(rows) <= n and binary_rank(rows) == len(rows)


def reference_matrix(top, anchors, m, r):
    # Cofactors of the final two binary basis directions reduce determinant size to r-2.
    out = [[0] * m for _ in range(m)]
    for monomial in top:
        positions = indices(monomial)
        for i, j in itertools.combinations(positions, 2):
            rest = [k for k in positions if k not in (i, j)]
            value = pdet([[h[k] for k in rest] for h in anchors])
            out[i][j] ^= value
            out[j][i] ^= value
    return tuple(tuple(row) for row in out)


def kernel_product(matrix, basis):
    nu = len(basis[0]) if basis else 0
    for row in matrix:
        support = [(i, x) for i, x in enumerate(row) if x]
        if support:
            for j in range(nu):
                require(rsum(pmul(x, basis[i][j]) for i, x in support) == 0,
                        'polynomial kernel certificate')


def certify_actual_rank(matrix, rank, selected_rows, selected_cols):
    m = len(matrix)
    P = [[matrix[i][j] for j in selected_cols] for i in selected_rows]
    delta = pdet(P)
    require(delta != 0, 'attaining rank minor')
    free = [j for j in range(m) if j not in selected_cols]
    G = [[0] * len(free) for _ in range(m)]
    for j, free_col in enumerate(free):
        column = [matrix[i][free_col] for i in selected_rows]
        if any(column):
            for i, pivot_col in enumerate(selected_cols):
                replaced = [row[:] for row in P]
                for l in range(rank):
                    replaced[l][i] = column[l]
                G[pivot_col][j] = pdet(replaced)
        G[free_col][j] = delta
    # Bottom minor is delta^nu by explicit construction, so NG=0 proves rank<=rank.
    kernel_product(matrix, G)
    return delta


def coset_representatives(H, m):
    rho = len(H)
    selected = []
    column_vectors = []
    for i in range(m):
        column = sum(((row >> i) & 1) << j for j, row in enumerate(H))
        if binary_rank(column_vectors + [column]) > len(column_vectors):
            column_vectors.append(column)
            selected.append(i)
        if len(selected) == rho:
            break
    require(len(selected) == rho and rho <= 4, 'reference coset dimension')
    output = {}
    for assignment in range(1 << rho):
        point = sum(((assignment >> j) & 1) << i for j, i in enumerate(selected))
        label = sum(((row & point).bit_count() & 1) << j for j, row in enumerate(H))
        output[label] = point
    require(len(output) == 1 << rho, 'surjective batch reference')
    return output


class Tape:
    def __init__(self, seed=None, coefficients=None, zero=False):
        self.rng = random.Random(seed)
        self.coefficients = coefficients
        self.zero = zero
        self.position = 0
        self.bits_used = 0

    def getrandbits(self, k):
        self.bits_used += k
        if self.zero:
            value = 0
        elif self.coefficients is not None:
            if self.position >= len(self.coefficients):
                raise AssertionError('scripted tape exhausted: unexpected trajectory')
            value = self.coefficients[self.position]
        else:
            value = self.rng.getrandbits(k)
        self.position += 1
        return value


def script(n, d, stages):
    repetitions = 2 + (2 * d - 1).bit_length()
    values = []
    for r, m, patterns, all_zero in stages:
        require(len(patterns) == r - 2, 'script anchor count')
        for sample in range(repetitions):
            for pattern in patterns:
                values.extend(0 if all_zero or sample == 0 else pattern.get(j, 0) for j in range(m))
    return Tape(coefficients=values)


def fixtures():
    grouped = [(1 << i) | (1 << j) | (1 << k)
               for i in range(4) for j in range(4, 8) for k in range(8, 13)]
    cases = []

    def add(name, n, raw, x, kind='endpoint', seed=236, stages=None, zero=False):
        d = degree(normalize(raw))
        tape = script(n, d, stages) if stages else Tape(seed=seed, zero=zero)
        cases.append({'name': name, 'n': n, 'raw': raw, 'x': x, 'kind': kind,
                      'tape': tape, 'seed': seed if stages is None and not zero else None,
                      'scripted': stages is not None, 'zero_tape': zero})

    add('zero_dimension', 0, [], 0)
    add('constant_one', 5, [0], 17)
    add('affine', 7, [1, 4, 32, 0], 45)
    add('quadratic_nonzero', 8, [3, 5, 24, 1, 128, 0], 173)
    add('quadratic_zero', 8, [3, 5, 24, 1, 128, 0], 0)
    add('duplicate_normalization', 4, [7, 7, 3, 1, 0, 0], 15)
    add('read_all_cubic', 3, [7], 7)
    add('read_all_boundary', 10, [7], 7)
    add('read_all_high_degree', 8, [63, 128], 63)
    for n in (11, 13):
        add(f'cubic_polynomial_{n}', n, [7], 7, 'cubic', stages=[(3, n, [{0: 1, 1: 2}], False)])
    add('cubic_deliberately_bad', 13, [7], 7, 'cubic', zero=True)
    add('full_support_scripted', 13, grouped, 273, 'grouped', stages=[(3, 13, [{0: 1, 4: 1}], False)])
    add('full_support_seed236', 13, grouped, 273, 'grouped')
    add('offset_scripted', 32, [7, 9, 2, 0], 13, 'cubic', stages=[(3, 32, [{0: 1, 1: 1}], False)])
    add('mixed_seed237', 32, [7, 9, 2, 0], 5, 'cubic', seed=237)
    add('two_stage_polynomial', 128, [15, 112], 127, 'quartic_volume', stages=[
        (4, 128, [{0: 1, 1: 2}, {2: 1, 3: 2}], False),
        (3, 126, [{2: 1, 3: 1}], False)])
    add('two_stage_seed238', 128, [15, 112], 127, 'quartic_volume', seed=238)
    add('bad_first_stage', 128, [15, 112], 15, 'quartic_volume', stages=[
        (4, 128, [{}, {}], True), (3, 128, [{4: 1, 5: 1}], False)])
    add('rank_four_scripted', 192, [15, 51, 448], 479, 'quartic_rank4', stages=[
        (4, 192, [{0: 1}, {1: 1}], False), (3, 188, [{2: 1, 3: 1}], False)])
    add('rank_four_seed239', 192, [15, 51, 448], 479, 'quartic_rank4', seed=239)
    require(len(cases) == 21, 'frozen trajectory count')
    return cases


class Audit:
    def __init__(self, fixture):
        self.f = fixture
        self.source = normalize(fixture['raw'])
        self.good = True
        self.current = None
        self.current_state = None
        self.query_rows = []
        self.stages = []
        self.leaves = []
        self.coverage = {'nontrivial_kernel': 0, 'nonzero_offsets': 0, 'noncoordinate_queries': 0,
                         'zero_candidate_rejected': 0, 'singular_at_zero': 0,
                         'repairs': 0, 'nonzero_batches': 0, 'off_promise_stages': 0}

    def generic_rank(self, current, C, r):
        top = {mask for mask in current if mask.bit_count() == r}
        if not top:
            return 0
        if r == 4:
            require(self.f['kind'] in ('quartic_volume', 'quartic_rank4'), 'unsupported generic quartic')
            require(C == tuple(1 << i for i in range(self.f['n'])), 'quartic generic-rank source state')
            expected = {15} if self.f['kind'] == 'quartic_volume' else {15, 51}
            require(top == expected, 'quartic source form')
            return 2 if self.f['kind'] == 'quartic_volume' else 4
        require(r == 3, 'unsupported generic order')
        if self.f['kind'] == 'grouped':
            groups = [range(4), range(4, 8), range(8, 13)]
        elif self.f['kind'] == 'quartic_volume':
            groups = [[4], [5], [6]]
        elif self.f['kind'] == 'quartic_rank4':
            groups = [[6], [7], [8]]
        else:
            groups = [[0], [1], [2]]
        forms = [rsum(C[j] for j in group) for group in groups]
        expected = {mask for mask in compose({7}, 0, forms) if mask.bit_count() == 3}
        require(top == expected and binary_rank(forms) == 3, 'decomposable cubic rank certificate')
        return 2

    def check_state(self, a, C, m):
        require(len(C) == self.f['n'] and all(row.bit_length() <= m for row in C), 'affine dimensions')
        require(binary_rank(C) == m, 'injective affine map')
        augmented = [row | ((((self.f['x'] ^ a) >> i) & 1) << m) for i, row in enumerate(C)]
        require(binary_rank(augmented) == m, 'hidden input belongs to affine state')

    def __call__(self, kind, event):
        if kind == 'query':
            require(event['answer'] == ((event['original_mask'] & self.f['x']).bit_count() & 1), 'oracle answer')
            self.query_rows.append(dict(event))
            self.coverage['noncoordinate_queries'] += event['original_mask'].bit_count() > 1
            self.coverage['nonzero_offsets'] += event['offset'] != 0
            if event['label'].startswith('degree_'):
                a, C, m = self.current_state
                require(rsum(C[i] for i in indices(event['original_mask'])) == event['residual_mask'], 'batch query lift')
                require(event['offset'] == ((event['original_mask'] & a).bit_count() & 1), 'batch affine offset')
        elif kind == 'stage_start':
            a, C, m, r = (event[key] for key in ('a', 'C', 'm', 'r'))
            self.check_state(a, C, m)
            self.current = compose(self.source, a, C)
            self.current_state = a, C, m
            if self.good:
                require(degree(self.current) <= r, 'propagated degree promise')
            else:
                self.coverage['off_promise_stages'] += degree(self.current) > r
            self.R = self.generic_rank(self.current, C, r)
            self.sample_ranks = []
        elif kind == 'sample':
            m, r = event['m'], event['r']
            top = {mask for mask in self.current if mask.bit_count() == r}
            reference = reference_matrix(top, event['anchors'], m, r)
            require(event['N'] == reference, 'canonical contraction matrix mismatch')
            require(all(value.bit_length() - 1 <= (r - 2) * (event['k'] - 1)
                        for row in reference for value in row), 'matrix coefficient degree cap')
            certify_actual_rank(reference, event['rank'], event['pivot_rows'], event['pivot_cols'])
            require(event['rank'] <= self.R, 'sample exceeds independently proved generic rank')
            self.sample_ranks.append(event['rank'])
            TOTAL['sample_matrices'] += 1
        elif kind == 'batch':
            m, r, rank, V, H = (event[key] for key in ('m', 'r', 'rank', 'V', 'H'))
            nu = m - rank
            require(tuple(self.sample_ranks) == event['sample_ranks'], 'sample trajectory')
            require(rank == max(self.sample_ranks) and event['selected'] == self.sample_ranks.index(rank), 'maximum-rank selection')
            kernel_product(event['N'], event['initial'])
            kernel_product(event['N'], event['final'])
            require(binary_rank(V) == nu and len(V) == m, 'repaired specialization dimension')
            require(len(H) == rank and binary_rank(H) == rank, 'batch codimension')
            for row in H:
                require(rsum(V[i] for i in indices(row)) == 0, 'H annihilates V')
            require(all(value.bit_length() - 1 <= rank * (r - 2) * (event['k'] - 1)
                        for row in event['final'] for value in row), 'basis degree cap')
            require(event['repairs'] <= nu * rank * (r - 2) * (event['k'] - 1), 'repair count cap')
            matrix_zero = [sum((value & 1) << j for j, value in enumerate(row)) for row in event['N']]
            self.coverage['singular_at_zero'] += binary_rank(matrix_zero) < rank
            self.coverage['repairs'] += event['repairs']
            self.coverage['zero_candidate_rejected'] += min(self.sample_ranks) == 0 < rank
            self.coverage['nonzero_batches'] += rank > 0
            full_rank = rank == self.R
            top = {mask for mask in self.current if mask.bit_count() == r}
            if full_rank:
                if nu >= r - 1 and top:
                    self.coverage['nontrivial_kernel'] += 1
                active = set(i for mask in top for i in indices(mask))
                for i in active:
                    derivative = {mask ^ (1 << i) for mask in top if mask >> i & 1}
                    restricted = compose(derivative, 0, V)
                    require(degree(restricted) <= r - 2, 'nonvacuous strong vanishing identity')
                    TOTAL['strong_derivatives'] += 1
            self.good = self.good and full_rank
            if self.good:
                for representative in coset_representatives(H, m).values():
                    restricted = compose(self.current, representative, V)
                    require(degree(restricted) <= r - 1, 'degree drop on every batch-answer coset')
                    TOTAL['cosets'] += 1
            self.stages.append({'r': r, 'm': m, 'actual_degree': degree(self.current),
                                'generic_component_rank': self.R, 'selected_rank': rank,
                                'good_history_after': self.good, 'sample_ranks': self.sample_ranks[:],
                                'repairs': event['repairs'], 'kernel_dimension': nu})
        elif kind == 'update':
            require(event['next_m'] == event['m'] - event['rank'], 'dimension telescoping')
            answers = sum(((row & event['z0']).bit_count() & 1) << j for j, row in enumerate(event['H']))
            require(answers == event['answers'], 'particular solution')
            expected_a = event['a'] ^ sum(((row & event['z0']).bit_count() & 1) << i for i, row in enumerate(event['C']))
            expected_C = tuple(rsum(event['V'][j] for j in indices(row)) for row in event['C'])
            require(event['next_a'] == expected_a and event['next_C'] == expected_C, 'affine update')
            self.check_state(event['next_a'], event['next_C'], event['next_m'])
            after = compose(self.source, event['next_a'], event['next_C'])
            require(after == compose(self.current, event['z0'], event['V']), 'source invariant after restriction')
            if self.good:
                require(degree(after) <= event['r'] - 1, 'visited residual degree')
        elif kind == 'leaf':
            a, C, m = event['a'], event['C'], event['m']
            self.check_state(a, C, m)
            actual = compose(self.source, a, C)
            extracted = {mask for mask in actual if mask.bit_count() <= 2}
            require(set(event['quadratic']) == extracted, 'leaf coefficient extraction even off promise')
            if self.good:
                require(actual == extracted, 'exact leaf on good history')
            columns = event['P_columns']
            require(binary_rank(columns) == m, 'symplectic change of basis invertible')
            P_rows = [sum(((col >> i) & 1) << j for j, col in enumerate(columns)) for i in range(m)]
            transformed = compose(extracted, 0, P_rows)
            expected = ({0} if 0 in extracted else set()) | {1 << j for j in indices(event['linear'])}
            t = event['polar_rank'] // 2
            expected |= {(1 << (2 * j)) | (1 << (2 * j + 1)) for j in range(t)}
            require(transformed == expected, 'quadratic normal form including square-to-linear terms')
            CP = tuple(rsum(P_rows[j] for j in indices(row)) for row in C)
            for query in self.query_rows[-event['query_count']:] if event['query_count'] else []:
                require(rsum(CP[i] for i in indices(query['original_mask'])) == query['residual_mask'], 'leaf query lift')
                require(query['offset'] == ((query['original_mask'] & a).bit_count() & 1), 'leaf offset')
            require(event['query_count'] <= min(m, t + 1), 'exact leaf query cap')
            self.leaves.append({'m': m, 'actual_degree': degree(actual), 'polar_rank': 2 * t,
                                'queries': event['query_count'], 'good_history': self.good})
        else:
            raise AssertionError('unknown observer event')


def run_case(fixture):
    started = time.perf_counter()
    audit = Audit(fixture)
    calls = []

    def oracle(mask):
        require(mask.bit_length() <= fixture['n'] and mask != 0, 'original-input query domain')
        answer = (mask & fixture['x']).bit_count() & 1
        calls.append((mask, answer))
        require(len(calls) <= fixture['n'], 'oracle n cap')
        return answer

    policy = Policy(fixture['n'], fixture['raw'], 2, fixture['tape'], oracle, audit)
    result = policy.run()
    require(tuple(sorted(audit.source)) == policy.source, 'normalization reference')
    require(result['queries'] == len(calls), 'query accounting')
    require(transcript_valid(result['transcript'], fixture['x'], fixture['n']), 'original transcript validity/independence')
    require(result['counters'].get('random_bits', 0) == fixture['tape'].bits_used, 'random bit accounting')
    d, n = result['degree'], fixture['n']
    if d >= 3:
        k, t_A = (8 * n * d - 1).bit_length(), 2 + (2 * d - 1).bit_length()
        require(fixture['tape'].bits_used <= t_A * k * n * (d - 2) * (d - 1) // 2, 'whole-path random cap')
    if fixture['tape'].coefficients is not None:
        require(fixture['tape'].position == len(fixture['tape'].coefficients), 'exact scripted tape consumption')
    correct = result['output'] == beval(audit.source, fixture['x'])
    B = spectrum_norm(audit.source)
    coefficient = ((1 << (2 * d - 1)) - 5) // 3 if d >= 3 else 1
    spectral_cap_holds = result['queries'] <= 1 or Fraction(1 << (result['queries'] - 1)) <= B ** coefficient
    informative = n >= 1 and B ** coefficient < (1 << (n - 1))
    if audit.good:
        require(correct, 'wrong output on independently certified good event')
        require(spectral_cap_holds, 'excess spectral query count on good event')
    if result['branch'] == 'read_all':
        require(correct and result['queries'] == n and result['counters'].get('dp_slots', 0) == 0,
                'read-all exact allocation branch')
        require(B ** coefficient >= (1 << (n - 1)), 'read-all respects spectral contract')
    if fixture['name'] == 'offset_scripted':
        require(audit.coverage['nonzero_offsets'] > 0, 'analytically guaranteed nonzero offset missing')
    if fixture['name'] == 'full_support_scripted':
        require(B == Fraction(5, 2) and informative and result['queries'] < n, 'full-support genuine savings')
    if fixture['name'] in ('two_stage_polynomial', 'rank_four_scripted'):
        require(informative and audit.good and audit.coverage['nonzero_batches'] == 2, 'genuine two-stage reconstruction')
    if fixture['name'] in ('cubic_deliberately_bad', 'bad_first_stage'):
        require(not audit.good and not correct, 'bad-tape negative control did not expose allowed error')
    if fixture['name'] == 'full_support_scripted':
        corrupted = [dict(row) for row in result['transcript']]
        corrupted[0]['answer'] ^= 1
        require(not transcript_valid(corrupted, fixture['x'], n), 'corrupted transcript verifier negative control')
        TOTAL['negative_transcripts'] += 1
    result.update({'name': fixture['name'], 'n': n, 'input_monomials': len(fixture['raw']),
                   'normalized_monomials': len(audit.source), 'input_masks': fixture['raw'],
                   'hidden_input': fixture['x'], 'seed': fixture['seed'], 'scripted': fixture['scripted'],
                   'zero_tape': fixture['zero_tape'], 'good_event_certified': audit.good,
                   'correct': correct, 'B_exact': str(B), 'spectral_cap_holds': spectral_cap_holds,
                   'spectral_bound_below_n': informative, 'stages': audit.stages,
                   'leaves': audit.leaves, 'coverage': audit.coverage,
                   'elapsed_seconds': time.perf_counter() - started})
    return result


def main():
    start = time.perf_counter()
    results = []
    for case in fixtures():
        print(json.dumps({'event': 'start', 'name': case['name']}), flush=True)
        result = run_case(case)
        results.append(result)
        print(json.dumps({'event': 'case', 'result': result}), flush=True)
    coverage = {key: sum(case['coverage'][key] for case in results) for key in results[0]['coverage']}
    require(all(coverage[key] > 0 for key in ('nontrivial_kernel', 'nonzero_offsets', 'noncoordinate_queries',
                                            'zero_candidate_rejected', 'singular_at_zero', 'repairs', 'off_promise_stages')),
            'mandatory adversarial coverage')
    require(any(case['good_event_certified'] and case['spectral_bound_below_n'] and case['queries'] < case['n']
                for case in results), 'genuine query saving')
    require(any(case['coverage']['nonzero_batches'] >= 2 and case['good_event_certified'] for case in results),
            'multiple degree reductions')
    require({case['branch'] for case in results} == {'low_degree', 'read_all', 'descent'}, 'all policy branches')
    sources = {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
               for name in ('s236_policy.py', 'check_s236_policy.py', 'run_s236_bounded.py')}
    print(json.dumps({'event': 'complete', 'status': 'PASS', 'trajectories': len(results),
                      'counts': TOTAL, 'coverage': coverage, 'source_sha256': sources,
                      'good_event_trajectories': sum(case['good_event_certified'] for case in results),
                      'deliberately_incorrect_bad_tapes': sum(not case['correct'] for case in results),
                      'elapsed_seconds': time.perf_counter() - start,
                      'scope': 'Bounded complete-policy validation with a separate exact reference; not an empirical failure-probability estimate, asymptotic proof, independent researcher review or formal certificate.'}), flush=True)


if __name__ == '__main__':
    main()
