# Internal manuscript assessment

Date: 2026-11-09. Candidate: preprint 0.2.0, expanding the unreleased 0.1.0 draft. Decision: **PUBLISH after the exact document/package freeze**, under Dan's explicit expansion and DOI-version instruction. No earlier DOI exists in the inspected release state. This is an internal AI-assisted review across mathematical, source, claims and artifact lenses, not independent peer review, multiple independent reviewers or formal certification.

## Expanded contribution and statement correspondence

The paper retains uniformly polynomial construction of one degree-reducing parity batch, and adds a complete on-demand recursive policy. The latter retains the original explicit squarefree ANF plus one binary affine map. For each fixed hidden x, the joint event of correct output and the stated spectral query bound has probability at least 1-2^(-b). Its universal cap is n queries. The field uses k=ceil(log_2(8nd)), with bounded repetition carrying accuracy. Time is 2^O(d log(d+1))*poly(n,S0,b), and live space is polynomial on all random tapes. S0 excludes any separately encoded rational accuracy input; optional rational parsing is explicitly charged.

The abstract, the two main theorems, proofs, limitations, README and release metadata distinguish uniform polynomial one-batch construction from degree-parameterized recursion; per-input success from a globally correct sampled tree; and an analytic algorithm from implemented or formally certified software. Fourier norm and sparsity are never supplied or computed by the algorithm.

## Recursive mathematical and resource review

1. Under a degree upper bound r, Boolean r-fold differences are base-independent, alternating and multilinear: the extra term in the additivity identity is an (r+1)-fold difference. Scalar extension therefore computes the canonical top form. The zero and repeated-variable collision controls reject direct nonbinary evaluation of an unreduced expression. Actual residual degree need not be detected.
2. The source evaluator uses the original ANF at specified binary points; those calls are charged computation, not hidden-input queries. Only r-2 slots need k-way extension, giving at most k^(r-2)*2^r original evaluations per matrix entry. Streamed loops do not require exponential storage.
3. A left inverse of C lifts every residual parity with its known offset. Updating a,C by a coset solution and nullspace basis preserves exactly the answer-compatible hidden inputs and full column rank. Two arbitrary successful stages compose; the explicit quartic/cubic/quadratic example independently certifies its generic ranks.
4. At most tF=2k(b+1) verified-field trials fail with probability at most 2^(-b-1). Each candidate misses generic rank with probability at most 1/8. A maximum among tA=b+ceil(log_2(2d)) candidates is generic whenever any candidate is; this does not create a generic-rank certificate. Every tape has fixed caps.
5. For each fixed x, condition on the entire successful history. Current maps/functions are fixed, future anchor bits are fresh, and the degree promise follows inductively. The first-failure sum is at most epsilon/2+(d-2)*epsilon/(2d). There is no unsupported all-input or cross-stage independence assertion.
6. Quadratic coefficients are recovered from binary evaluations. Symplectic elimination includes diagonal-to-linear terms through evaluation on the new basis; t odd-coordinate queries leave one affine query. The exact norm is 2^t. Constants, affine functions, zero remaining dimension and s=1 are included. On a bad history the bounded quadratic approximation is still defined.
7. Restriction groups Fourier coefficients, proving norm monotonicity. Summing k*2^(2r-3)*log B gives k*(2^(2d-1)-8)/3*log B. The leaf adds 1+log B. Independent equations telescope the dimension, proving n queries on all tapes. The smaller bound and correctness are jointly probabilistic.
8. Raw bit, field, randomness, input normalization, query-vector and transient-storage costs are displayed. The inequality (2k)^d <= 16nd*[2d/(e ln2)]^d pays the degree power of log n; k is independent of b. Sequential scans/counters incur a conservative W^2 overhead. No free word arithmetic, expanded residual ANF, stored full tree, or arbitrary-accuracy parsing is hidden.

These are analytic checks against the source derivation. No new algorithm implementation, benchmark, numerical experiment or proof checker was run. No unresolved blocking mathematical finding was identified at this internal/imported-theorem boundary; that is not independent acceptance.

## Retained one-batch assessment

The theorem concerns every explicitly listed squarefree ANF of actual degree 3<=d<=n and rational 0<delta<=1/4. The algorithm returns a single binary subspace and its equations; all cosets reduce degree on the success event. The original Fourier norm and sparsity occur only in analysis, never as supplied oracles.

Checked in the manuscript:

1. The imported matrix has exactly d-2 homogeneous multilinear anchor blocks. The generic/max-rank factor is 2^(d-2), and quadratic spectral norm gives the separate factor 2^(d-1). Binary expansion costs up to k equations per extension-field row. Parseval supplies the last factor of one half in the logarithm of sparsity.
2. On a pivot chart, the kernel basis has denominator dividing one maximal minor D. Clearing D^(d-1) preserves the strong identity on every rank-preserving specialization. No extra exceptional locus, generic-rank test or symbolic determinant search is used computationally.
3. A fixed nonzero minor has total degree at most n(d-2), so q>=4n(d-2)/delta bounds the rank failure by delta/4. The proof applies over every verified degree-k binary field.
4. The determinant evaluator follows by canceling all subset-expansion terms omitting a direction. Remaining terms are permutations; in characteristic two the permanent is a determinant. Lower-degree monomials contribute zero. This removes the earlier 2^d evaluation factor without changing the subspace, error or codimension analysis.
5. At most t=2k ceil(log_2(2/delta)) monic field trials, with exact irreducibility tests, bound declared field failure by delta/2. Fresh independent anchor bits support the conditional failure calculation. No post-sample retry is assumed.
6. The polynomial time guarantee is in n and explicit encoding length, not merely the binary encoding of n. All field arithmetic, inversion, determinant workspaces, memory access, binary elimination, randomness and output are charged. The number of queries still has exponential dependence on d.
7. The original four exact cubic/quartic controls have attaining minors and independent generic-rank upper bounds. The cubic anchor (1,alpha,0) demonstrates genuine binary dimension loss. Low-rank failures are admitted and probabilistically charged.

These are analytic checks; no implementation, finite benchmark or formal proof checker was run. The determinant accounting is a refinement of the one-batch evaluator, not a new radical theorem. Its uniform polynomial bound remains distinct from the recursive guarantee.

## Sources and novelty

Reuse the completed, focused source audit for the exact computational contracts; unchanged source evidence is not counted as a new discovery. The November 9 source check reconfirmed the pinned Zhang and Moshkovitz?Zhu versions; a targeted bibliographic check corrected the Hrubes title before release.

- [Zhang, arXiv:2611.03452v1](https://arxiv.org/html/2611.03452v1), November 2, 2026: top forms, all-coset degree drop, affine spectral monotonicity and generic radical identity, especially Theorem 3.12. Remark 3.17 leaves tree-construction time open. Our logarithmic query loss and randomized per-input guarantee do not settle that exact deterministic question.
- [Moshkovitz?Zhu, arXiv:2603.11038v1](https://arxiv.org/html/2603.11038v1), March 11, 2026: Theorem 1.1's generic/max-rank comparison over F2. The separate large-field partition-rank branch is not imported.
- [Tsang?Wong?Xie?Zhang, FOCS 2013](https://users.cis.fiu.edu/~nxie/papers/TWXZ13.pdf): prior parity-tree recursion and degree reduction are attributed, not claimed as new.
- [Zhang, Efficient quantum protocols for XOR functions](https://arxiv.org/abs/1307.6738): computational efficiency assumes efficiently encoded/decoded Fourier spectrum, and the output is a quantum communication protocol. It does not supply the same ANF-input classical path computation.
- [Hrubes, On hardness of multilinearization, and VNP completeness in characteristics two](https://eccc.weizmann.ac.il/report/2015/067/), April 21, 2015, Theorem 7(ii): whole-polynomial arithmetic representation is the obstacle. That conditional hardness does not rule out a degree-parameterized top-form evaluator under a propagated degree promise.

Named transfer question: does a primary result already provide the same explicit-source on-demand policy, query/error contract and paid per-path computation? The retained bounded searches used the Zhang identifier with constructive/recursive terms and parity trees with finite differences and degree-parameterized computation. No inspected statement subsumed the precise contract. This is not proof of novelty or priority. No author was contacted and no broad literature screen was repeated.

## Claims and publication decision

PUBLISH as an attributed algorithmic preprint, with no priority claim and explicit disclosure of internal review and absent formal certification. The complete per-input construction is the expanded reader benefit; the one-step theorem retains its sharper computation bound. Imported structural theorems remain clearly identified. No improvement in existential parity depth, general influence or quantum-simulation bounds is claimed. Unrestricted XOR log-rank and BPP versus BQP remain unresolved.

Formal certification is a separate queued obligation covering the whole revised manuscript, including imported structural results, stochastic/path quantifiers and bit/space bounds. It cannot be claimed from a conditional Lean interface, document check or DOI. The first certification action is a full claim/dependency and reusable-source map; publication does not start inference or compilation.

## Artifact checks

The final build, exact PDF/source hashes, embedded-font count, local-link/package consistency and actual page-inspection identities are recorded in verification/build.json, verification/package.json and verification/visual.json. All 11 final pages were visually inspected on November 9: equations, theorem/proof continuations, controls and bibliography are legible, with no observed clipping or overlap. The final TeX log has no box/reference warnings; the retained Fontconfig message caused no visible defect. A source-title correction and the expanded scope invalidate the old six-page receipt; the new receipt must bind the final PDF. These are document checks, not mathematical certification.

Only manuscript/source, public citations, licensing, metadata and document tools are included. Private planning history, machine paths, credentials and unrelated research archives are excluded. Tooling retains attribution to the same author's aa-noise-influence archive under CC BY 4.0. Post-release DOI/verification updates remain outside the immutable archive they verify.
