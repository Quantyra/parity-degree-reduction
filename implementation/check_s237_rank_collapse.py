"""Two preregistered S237 full-policy trajectories; S236 sources stay unchanged."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_s236_policy as ref
from s236_policy import Policy


class CollapseAudit(ref.Audit):
    def __init__(self, fixture):
        super().__init__(fixture)
        self.collapse = []

    def generic_rank(self, current, C, r):
        if r == 4:
            ref.require(self.f['kind'] == 'two_disjoint_volumes', 'admitted direct-sum certificate')
            ref.require(C == tuple(1 << j for j in range(128)), 'initial quartic coordinates')
            ref.require({mask for mask in current if mask.bit_count() == 4} == {15, 240},
                        'two independent four-volume source forms')
            # Each four-dimensional volume contraction has rank<=2. The disjoint
            # sum has rank<=4, attained by the displayed block matrix below.
            return 4
        return super().generic_rank(current, C, r)

    def __call__(self, kind, event):
        old_cosets = ref.TOTAL['cosets']
        super().__call__(kind, event)
        if kind != 'batch' or event['rank'] == 0:
            return
        m, rank, N, V = (event[key] for key in ('m', 'rank', 'N', 'V'))
        ref.require(len(self.collapse) == 0, 'exactly one nonzero batch per fixture')
        ref.require(m == self.f['n'], 'collapse occurs in original full state')
        expected = [[0] * m for _ in range(m)]
        if self.f['kind'] == 'grouped':
            for i in range(8):
                for j in range(8, 13):
                    expected[i][j] = expected[j][i] = 2
            expected_rank, rank_zero, pivots = 2, 0, [0, 8]
            excluded = set()
            ref.require(ref.rsum(V[:8]) == 0 and ref.rsum(V[8:]) == 0,
                        'cubic repaired space equals ker(L1+L2,L3)')
        else:
            expected[2][3] = expected[3][2] = 1
            expected[6][7] = expected[7][6] = 2
            expected_rank, rank_zero, pivots = 4, 2, [2, 3, 6, 7]
            excluded = {2, 3}
            ref.require(all(V[j] == 0 for j in (2, 3, 6, 7)),
                        'quartic repaired space fixes both block pairs')
        ref.require(N == tuple(tuple(row) for row in expected), 'analytic selected matrix identity')
        ref.require(rank == expected_rank == self.R, 'selected matrix independently generic')
        fixed_minor = ref.pdet([[N[i][j] for j in pivots] for i in pivots])
        ref.require(fixed_minor == 4, 'explicit attaining determinant is t^2')
        at_zero = [sum((value & 1) << j for j, value in enumerate(row)) for row in N]
        observed_zero_rank = ref.binary_rank(at_zero)
        ref.require(observed_zero_rank == rank_zero < rank, 'actual selected matrix loses rank at zero')
        initial_zero = [sum((value & 1) << j for j, value in enumerate(row))
                        for row in event['initial']]
        initial_zero_rank = ref.binary_rank(initial_zero)
        final_zero_rank = ref.binary_rank(V)
        ref.require(initial_zero_rank == 0 < m - rank == final_zero_rank,
                    'unrepaired dimension fails; repaired dimension succeeds')
        ref.require(event['repairs'] > 0, 'repair branch was actually used')
        ref.require(all(value in (0, 1) for row in event['final'] for value in row),
                    'repaired kernel constant on these analytic fixtures')
        ref.require(all(a == (b << 2) for ar, br in zip(event['initial'], event['final'])
                        for a, b in zip(ar, br)), 'removed common t^2 from basis, not assumed from N(0)')
        ref.require(event['repairs'] == 2 * (m - rank), 'two divisions per independent basis column')
        # Independent full kernel of N(0), known explicitly from the displayed matrix.
        free = [j for j in range(m) if j not in excluded]
        index = {j: k for k, j in enumerate(free)}
        naive = [1 << index[j] if j in index else 0 for j in range(m)]
        naive_dimension = ref.binary_rank(naive)
        ref.require(naive_dimension == m - rank_zero > final_zero_rank,
                    'repaired space strictly smaller than full zero-specialized kernel')
        ref.require(all(ref.rsum(naive[j] for j in ref.indices(row)) == 0 for row in at_zero),
                    'naive matrix really spans ker N(0)')
        naive_degree = ref.degree(ref.compose(self.current, 0, naive))
        ref.require(naive_degree == event['r'], 'naive full-kernel specialization fails degree drop')
        ref.require(self.good and ref.TOTAL['cosets'] - old_cosets == 1 << rank,
                    'every answer coset passed the retained exact checker')
        self.collapse.append({
            'r': event['r'], 'm': m, 'selected_sample': event['selected'],
            'rank_over_F2_t': rank, 'rank_at_zero': observed_zero_rank,
            'attaining_minor_indices': pivots, 'attaining_minor_polynomial_mask': fixed_minor,
            'matrix_nonzero_entries': [[i, j, value] for i, row in enumerate(N)
                                       for j, value in enumerate(row) if value],
            'initial_basis_rank_at_zero': initial_zero_rank,
            'repaired_basis_rank_at_zero': final_zero_rank,
            'full_kernel_dimension_at_zero': naive_dimension, 'repairs': event['repairs'],
            'cosets_verified': ref.TOTAL['cosets'] - old_cosets,
            'naive_kernel_restriction_degree': naive_degree,
            'negative_controls': {'unrepaired_basis_rejected': True, 'full_kernel_at_zero_rejected': True},
            'parity_equations': list(event['H']), 'specialized_basis_rows': list(V)})


def fixtures():
    grouped = [(1 << i) | (1 << j) | (1 << k)
               for i in range(4) for j in range(4, 8) for k in range(8, 13)]
    return [
        {'name': 'total_rank_collapse', 'n': 13, 'raw': grouped, 'x': 273, 'kind': 'grouped',
         'tape': ref.script(13, 3, [(3, 13, [{0: 2, 4: 2}], False)]),
         'expected_B': Fraction(5, 2), 'expected_output': 1, 'query_limit': 3},
        {'name': 'partial_rank_collapse', 'n': 128, 'raw': [15, 240], 'x': 255,
         'kind': 'two_disjoint_volumes',
         'tape': ref.script(128, 4, [(4, 128, [{0: 1, 4: 1}, {1: 1, 5: 2}], False),
                                    (3, 124, [{}], True)]),
         'expected_B': Fraction(121, 16), 'expected_output': 0, 'query_limit': 7}]


def run_case(fixture):
    audit = CollapseAudit(fixture)
    calls = []

    def oracle(mask):
        ref.require(0 < mask < (1 << fixture['n']), 'original parity domain')
        answer = (mask & fixture['x']).bit_count() & 1
        calls.append((mask, answer))
        ref.require(len(calls) <= fixture['n'], 'unconditional query cap')
        return answer

    policy = Policy(fixture['n'], fixture['raw'], 2, fixture['tape'], oracle, audit)
    result = policy.run()
    ref.require(result['branch'] == 'descent', 'construction not bypassed by cutoff')
    ref.require(audit.good and len(audit.collapse) == 1, 'certified good rank-collapse trajectory')
    ref.require(audit.coverage['singular_at_zero'] == 1, 'original missing coverage predicate now true')
    ref.require(result['output'] == ref.beval(audit.source, fixture['x']) == fixture['expected_output'],
                'exact complete-policy output')
    ref.require(result['queries'] == len(calls) <= fixture['query_limit'], 'complete trajectory query cap')
    ref.require(ref.transcript_valid(result['transcript'], fixture['x'], fixture['n']), 'original transcript')
    ref.require(result['counters']['random_bits'] == fixture['tape'].bits_used, 'random bit accounting')
    ref.require(fixture['tape'].position == len(fixture['tape'].coefficients), 'exact frozen tape consumption')
    B = ref.spectrum_norm(audit.source)
    ref.require(B == fixture['expected_B'], 'independent original spectral norm')
    coefficient = ((1 << (2 * result['degree'] - 1)) - 5) // 3
    ref.require(Fraction(1 << (result['queries'] - 1)) <= B ** coefficient < (1 << (fixture['n'] - 1)),
                'exact spectral cap and genuine query-saving regime')
    result.update({'name': fixture['name'], 'n': fixture['n'], 'input_masks': fixture['raw'],
                   'hidden_input': fixture['x'], 'B_exact': str(B), 'good_event_certified': audit.good,
                   'correct': True, 'spectral_cap_holds': True, 'spectral_bound_below_n': True,
                   'stages': audit.stages, 'leaves': audit.leaves,
                   'coverage': audit.coverage, 'rank_collapse_evidence': audit.collapse})
    return result


def main():
    start = time.perf_counter()
    results = []
    for fixture in fixtures():
        print(json.dumps({'event': 'start', 'name': fixture['name']}), flush=True)
        result = run_case(fixture)
        results.append(result)
        print(json.dumps({'event': 'case', 'result': result}), flush=True)
    ref.require(len(results) == 2, 'exact preregistered trajectory allocation')
    drops = [(x['rank_over_F2_t'], x['rank_at_zero'])
             for result in results for x in result['rank_collapse_evidence']]
    ref.require(drops == [(2, 0), (4, 2)], 'both total and partial matrix-rank collapse covered')
    ref.require(ref.TOTAL['sample_matrices'] == 15 and ref.TOTAL['cosets'] == 21,
                'complete samples and all-coset loops')
    sources = {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
               for name in ('s236_policy.py', 'check_s236_policy.py',
                            'check_s237_rank_collapse.py', 'run_s237_bounded.py')}
    print(json.dumps({'event': 'complete', 'status': 'PASS', 'trajectories': 2,
                      'rank_drops': drops, 'counts': ref.TOTAL, 'source_sha256': sources,
                      'repairs': sum(r['coverage']['repairs'] for r in results),
                      'negative_control_rejections': 4, 'elapsed_seconds': time.perf_counter() - start,
                      'scope': 'Separate S237 rank-collapse coverage; S236 campaign remains STOP. '
                               'No general-bound improvement, empirical probability estimate, '
                               'independent researcher review or formal certificate.'}), flush=True)


if __name__ == '__main__':
    main()
