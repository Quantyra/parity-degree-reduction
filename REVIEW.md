# Internal manuscript assessment

Date: 2026-11-09. Candidate: working draft 0.1.0. This is an internal AI-assisted review through mathematical, source, claim and artifact lenses. It is not independent peer review, multiple independent reviewers or formal certification.

## Mathematical and computational scope

The theorem concerns every explicitly listed squarefree ANF of actual degree 3<=d<=n and rational 0<delta<=1/4. The algorithm returns a single binary subspace and its equations; all cosets reduce degree on the success event. The original Fourier norm and sparsity occur only in analysis, never as supplied oracles.

Checked in the manuscript:

1. The imported matrix has exactly d-2 homogeneous multilinear anchor blocks. The generic/max-rank factor is 2^(d-2), and quadratic spectral norm gives the separate factor 2^(d-1). Binary expansion costs up to k equations per extension-field row. Parseval supplies the last factor of one half in the logarithm of sparsity.
2. On a pivot chart, the kernel basis has denominator dividing one maximal minor D. Clearing D^(d-1) preserves the strong identity on every rank-preserving specialization. No extra exceptional locus, generic-rank test or symbolic determinant search is used computationally.
3. A fixed nonzero minor has total degree at most n(d-2), so q>=4n(d-2)/delta bounds the rank failure by delta/4. The proof applies over every verified degree-k binary field.
4. The determinant evaluator follows by canceling all subset-expansion terms omitting a direction. Remaining terms are permutations; in characteristic two the permanent is a determinant. Lower-degree monomials contribute zero. This removes the earlier 2^d evaluation factor without changing the subspace, error or codimension analysis.
5. At most t=2k ceil(log_2(2/delta)) monic field trials, with exact irreducibility tests, bound declared field failure by delta/2. Fresh independent anchor bits support the conditional failure calculation. No post-sample retry is assumed.
6. The polynomial time guarantee is in n and explicit encoding length, not merely the binary encoding of n. All field arithmetic, inversion, determinant workspaces, memory access, binary elimination, randomness and output are charged. The number of queries still has exponential dependence on d.
7. The original four exact cubic/quartic controls have attaining minors and independent generic-rank upper bounds. The cubic anchor (1,alpha,0) demonstrates genuine binary dimension loss. Low-rank failures are admitted and probabilistically charged.

These are analytic checks; no implementation, finite benchmark or formal proof checker was run. The new determinant accounting is a refinement of the evaluation step, not a new radical theorem or a solution to recursion.

## Sources and novelty

- [Zhang, arXiv:2611.03452v1](https://arxiv.org/html/2611.03452v1), November 2, 2026: needed top-form/all-coset interface and Theorem 3.12's generic radical identity; Remark 3.17 explicitly leaves efficient construction open. Its descent and full recursive existence theorem are attributed and not reproduced as new results.
- [Moshkovitz-Zhu, arXiv:2603.11038v1](https://arxiv.org/html/2603.11038v1), March 11, 2026: Theorem 1.1's generic/max-rank comparison and Section 5.1's determinant-multiplicity argument. The separate partition-rank inequality and its field-size conditions are not imported.
- [Tsang-Wong-Xie-Zhang, 2013](https://users.cis.fiu.edu/~nxie/papers/TWXZ13.pdf): earlier degree-reduction and parity-query framework. Query efficiency alone does not supply the explicit computation/access contract here.
- [Zhang, Efficient quantum protocols for XOR functions](https://www.cse.cuhk.edu.hk/~syzhang/papers/QbyLogrank.pdf): the stated computational efficiency assumes an efficiently encoded/decoded Fourier spectrum and concerns a quantum communication protocol. That is a different input model and output.

The named transfer question is whether a previous result already supplies the same one-batch ANF-input guarantee and polynomial construction cost with logarithmic descent loss. Bounded searches combined the exact 2611.03452 identifier with algorithm/constructive terms and the degree-reduction, alternating-form and finite-field-kernel operation. They did not identify an inspected primary statement subsuming the exact contract. This does not establish priority. The manuscript therefore presents an attributed algorithmic corollary and makes no first-result or publication-significance claim. No source author was contacted.

## Claims and readiness

The result improves constructive access within its explicit input model. It does not improve the imported existential query bound, construct a full recursive policy or supply an arbitrary quantum amplitude evaluator. The representation of Boolean restrictions over extension fields, degree detection, leaf costs and total error accounting remain separate. No new theorem about the AA conjecture, BPP or BQP is claimed.

The manuscript is a working draft for the user's repository/Zenodo setup. Preparation is authorized; release and DOI creation are pending. The author will enable Zenodo and confirm before the requested PaperMill handoff. Novelty remains unestablished. This is a release-status boundary, not a claim that independent review or full recursion is a prerequisite to preparing the note.

## Artifact checks

Build identity and final log diagnostics are recorded in verification/build.json. Actual visual inspection is recorded in verification/visual.json after rendering; metadata, hashes and local links are checked in verification/package.json. Those checks establish document consistency only. No review is inferred merely from a successful build.

The final six-page PDF was visually inspected on November 9, 2026: equations, theorem/proof continuations, the four-control table, bibliography and author metadata are legible, with no observed clipping or overlap. The final TeX log has no overfull/underfull boxes or unresolved references; all 20 PDF fonts are embedded. A nonfatal local Fontconfig configuration message is retained in the build receipt, with no observed rendering defect. The bibliography occupies a dedicated final page. Exact PDF and render identities are pinned in the receipts.

The public package contains only the manuscript, public references, metadata, licensing and document tooling. It does not bundle private planning history, credentials, machine paths or unrelated research records. Build tooling is adapted under CC BY 4.0 from the same author's aa-noise-influence manuscript archive.
