# Degree reduction and recursive parity queries for explicit Boolean polynomials

**Daniel Fredriksen ? Quantyra Inc. ? [ORCID 0009-0002-9123-7435](https://orcid.org/0009-0002-9123-7435)**

[Manuscript PDF](manuscript/main.pdf) ? [LaTeX source](manuscript/main.tex) ? [Review and scope](REVIEW.md) ? [Publication record](publication/README.md)

**Preprint candidate, version 0.2.0.** This expands the unreleased 0.1.0 working draft. The first GitHub release and Zenodo archive are authorized and pending exact-package checks; no prior DOI is assumed.

The paper gives two attributed algorithmic corollaries for an explicit squarefree Boolean polynomial p of degree d. For f=(-1)^p, let B be its Fourier spectral norm and s its Fourier sparsity; neither is an algorithm input.

- One fixed parity batch lowers degree on every coset, with probability at least 1-delta, codimension at most min(n,k*2^(2d-3)*log_2 B), and k=ceil(log_2(4n(d-2)/delta)). Determinant evaluation gives construction time polynomial in ambient n, explicit input length and log(1/delta).
- A complete on-demand recursive policy, for each fixed hidden input, jointly returns p(x) correctly and asks min(n,O(1+4^d log(s) log(nd))) parity queries with probability at least 1-delta. Its bit time is 2^O(d log(d+1))*poly(n,S,log(1/delta)), with polynomial working space. The cap n holds on every tape. An explicit accuracy integer is used; arbitrary rational parsing has a separately charged input cost.

Recursion retains the original ANF plus a compact binary affine map. Boolean finite differences precede scalar extension; fixed-budget maximum-rank sampling, lifted queries and exact quadratic leaves complete the proof. The one-batch theorem retains a stronger uniform polynomial runtime for its narrower output. The paper supplies algorithms and proofs, not an implementation or benchmark.

The structural inputs are [Zhang v1](https://arxiv.org/abs/2611.03452v1) and [Moshkovitz?Zhu v1](https://arxiv.org/abs/2603.11038v1). The imported existential depth bound is stronger by a logarithmic factor. Our randomized per-input policy is not a globally correct sampled deterministic tree. Novelty and publication significance remain unestablished; unrestricted XOR log-rank and BPP versus BQP remain unresolved.

## Build and check

Use Python 3.10+, Tectonic 0.17.0 and [requirements.txt](requirements.txt).

    python -m pip install -r requirements.txt
    python tools/build.py --tectonic /path/to/tectonic --render
    python tools/check_package.py

These tools only typeset and check documents. Inspect changed pages before updating [visual evidence](verification/visual.json); [build](verification/build.json) and [package](verification/package.json) receipts establish document consistency, not theorem verification. Tooling is adapted under CC BY 4.0 from the same author's [aa-noise-influence archive](https://github.com/Quantyra/aa-noise-influence).

## Citation and archiving

[CITATION.cff](CITATION.cff) and [.zenodo.json](.zenodo.json) contain the confirmed author and preprint metadata. The PDF is tracked in Git and included in the repository archive. See [publication details](publication/README.md) for release status and verified identifiers; enabling Zenodo alone does not mint a DOI.

All original package material is licensed under [CC BY 4.0](LICENSE). External papers are linked, not redistributed. OpenAI Codex assisted derivation, source comparison, drafting and package preparation. [REVIEW.md](REVIEW.md) records internal AI-assisted mathematical, source, claims and artifact checks. No independent peer review or Lean certification is claimed.
