# Polynomial-time parity-query policies for explicit Boolean polynomials

**Daniel Fredriksen | Quantyra Inc. | [ORCID 0009-0002-9123-7435](https://orcid.org/0009-0002-9123-7435)**

[Manuscript PDF](manuscript/main.pdf) | [LaTeX source](manuscript/main.tex) | [Review and scope](REVIEW.md) | [Publication record](publication/README.md)

**Version0.4.0: PUBLISHED AND VERIFIED.** [Version DOI10.5281/zenodo.24095400](https://doi.org/10.5281/zenodo.24095400), [release/PDF](https://github.com/Quantyra/parity-degree-reduction/releases/tag/v0.4.0), [archive receipt](verification/publication-v0.4.0.json). All37archived files match frozen commit9ce510fb278bfc8350f7f841ce9ab36bff354794. This16-page revision removes the extra logarithmic query factor and includes the complete implementation and retained validation. Earlier versions remain immutable under [concept DOI10.5281/zenodo.24092921](https://doi.org/10.5281/zenodo.24092921). The DOI/citation receipt is a post-release record outside the immutable archive.

For every explicit squarefree Boolean ANF p of original degree d>=3, and each fixed hidden input x, the randomized on-demand policy jointly returns p(x) correctly and uses at most min(n,1+[(2^(2d-1)-5)/3]log2 B) queries with probability at least1-2^-b. Here B is the Fourier spectral norm of (-1)^p, used only in analysis. Since B<=sqrt(s), this is min(n,O(1+4^d log s)) queries. Total bit time and live space are polynomial in n, original encoding length and b with fixed exponents independent of d. All random tapes terminate and ask at most n queries. Exact low-degree endpoints and separately charged arbitrary-rational precision parsing remain explicit.

Polynomial anchors in one variable preserve generic rank with bounded failure probability. Exact rational elimination finds an attaining actual-rank minor. A valuation-budgeted repair returns a binary kernel space of codimension equal to the sampled rank, removing the previous k=ceil(log2(8nd)) multiplier. The canonical factor-partition evaluator and the improved cutoff4^d<6n+4 pay all computation. The manuscript explicitly charges the cached implementation's additional storage.

The separate finite-field one-batch theorem and its logarithmic binary-intersection loss remain valid. Structural inputs are [Zhang v1](https://arxiv.org/abs/2611.03452v1) and [Moshkovitz-Zhu v1](https://arxiv.org/abs/2603.11038v1). The recursive policy matches the retained existential query scale under its randomized per-input contract; it does not construct an everywhere-correct sampled deterministic tree. Novelty is unestablished. Unrestricted XOR log-rank and BPP versus BQP remain unresolved.

## Implementation and evidence

The [complete policy and exact checkers](implementation/README.md) are source-preserving exports; [provenance](verification/policy-provenance.json) binds their original identities and raw logs/receipts. The S236 campaign completed21 trajectories, including19 certified good-event successes and two deliberately bad-tape errors, but remains STOP because its final rank-collapse coverage gate failed. A separately preregistered S237 check passed both total and partial rank collapse, all6,523 assertions, and correct3/7-query complete trajectories. The earlier startup import failure and diagnostic history remain visible. No experiment was rerun for this release; the new portable replay launcher was statically checked, not executed.

The [256-fixture component diagnostic](verification/evaluator-diagnostic.json) is also retained unchanged. Finite tests support implementation coverage; the general guarantees follow from the analytic proof and attributed imports. No independent peer review, formal certificate or machine-checked software refinement is claimed.

## Document build

Use Python3.10+, Tectonic0.17.0 and [requirements.txt](requirements.txt):

    python -m pip install -r requirements.txt
    python tools/build.py --tectonic /path/to/tectonic --render
    python tools/check_package.py

Document tools never publish or run the policy experiments. [Build](verification/build.json), [visual](verification/visual.json) and [package](verification/package.json) receipts establish artifact consistency, not mathematical certification. Replay instructions and expected historical failure are separate.

## Citation and ownership

[CITATION.cff](CITATION.cff), [.zenodo.json](.zenodo.json) and [CC BY4.0](LICENSE) retain Daniel Fredriksen, Quantyra Inc. and the confirmed ORCID. OpenAI Codex assisted derivation, source comparison, implementation, drafting and packaging. [REVIEW.md](REVIEW.md) records the internal mathematical/source/claims/artifact review. PaperMill owns publication and queued full-manuscript certification; this revision starts no formal proof job.
