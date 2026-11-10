"""Portable opt-in replay of unchanged archived case routines; never run by packaging."""
import argparse
import json
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('s236', 's237'), required=True)
    parser.add_argument('--execute', action='store_true',
                        help='Explicitly opt into the bounded mathematical case computations')
    args = parser.parse_args()
    if not args.execute:
        parser.error('Replay requires --execute and an external process/resource limit')
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'implementation'))
    import check_s236_policy as base
    if args.suite == 's236':
        results = [base.run_case(case) for case in base.fixtures()]
        coverage = {key: sum(case['coverage'][key] for case in results)
                    for key in results[0]['coverage']}
        print(json.dumps({'suite': 's236', 'trajectories': len(results),
                          'coverage': coverage}), flush=True)
        base.require(all(coverage[key] > 0 for key in
                         ('nontrivial_kernel', 'nonzero_offsets', 'noncoordinate_queries',
                          'zero_candidate_rejected', 'singular_at_zero', 'repairs', 'off_promise_stages')),
                     'mandatory adversarial coverage (preserved historical STOP)')
        base.require(any(case['good_event_certified'] and case['spectral_bound_below_n']
                         and case['queries'] < case['n'] for case in results), 'genuine query saving')
        base.require(any(case['coverage']['nonzero_batches'] >= 2 and case['good_event_certified']
                         for case in results), 'multiple degree reductions')
        base.require({case['branch'] for case in results} == {'low_degree', 'read_all', 'descent'},
                     'all policy branches')
    else:
        import check_s237_rank_collapse as target
        results = [target.run_case(case) for case in target.fixtures()]
        base.require(len(results) == 2, 'exact preregistered trajectory allocation')
        drops = [(x['rank_over_F2_t'], x['rank_at_zero']) for result in results
                 for x in result['rank_collapse_evidence']]
        base.require(drops == [(2, 0), (4, 2)], 'both total and partial matrix-rank collapse covered')
        base.require(base.TOTAL['sample_matrices'] == 15 and base.TOTAL['cosets'] == 21,
                     'complete samples and all-coset loops')
        print(json.dumps({'suite': 's237', 'status': 'PASS', 'rank_drops': drops,
                          'counts': base.TOTAL, 'results': results}), flush=True)

if __name__ == '__main__':
    main()
