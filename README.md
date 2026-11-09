# Constructing a degree-reducing parity batch from explicit Boolean polynomials

**Daniel Fredriksen · Quantyra Inc. · [ORCID 0009-0002-9123-7435](https://orcid.org/0009-0002-9123-7435)**

[Manuscript PDF](manuscript/main.pdf) · [LaTeX source](manuscript/main.tex) · [Review and scope](REVIEW.md) · [Zenodo setup](publication/README.md)

**Working draft, version 0.1.0.** The repository and manuscript are prepared for review. No GitHub release, Zenodo archive or DOI has been created. The author will connect this repository to Zenodo; the subsequent PaperMill handoff and release decision remain pending.

Given an explicit squarefree Boolean polynomial of degree d>=3, the note gives a randomized algorithm constructing a fixed batch of parity queries that lowers the degree on every branch. For f=(-1)^p, B=||fhat||_1 and error allowance delta, the codimension is at most

    min(n, k * 2^(2d-3) * log_2 B),
    k = ceil(log_2(4n(d-2)/delta)).

Success probability is at least 1-delta, and degree reduction is exact on success. Construction time and space are polynomial in the ambient dimension, explicit ANF encoding length and log(1/delta). The degree-dependent query bound remains exponential. Determinant evaluation in characteristic two removes the subset-enumeration cost of the initial derivation.

This is an algorithmic corollary of the generic radical identity in [Zhang v1](https://arxiv.org/abs/2611.03452v1) and the rank comparison of [Moshkovitz-Zhu v1](https://arxiv.org/abs/2603.11038v1), using standard specialization and linear algebra. It introduces a logarithmic codimension loss relative to the structural existence result. Novelty and publication significance are not established. The note supplies a proved algorithm and pseudocode, not a software implementation or benchmark. Efficient full recursion, unrestricted XOR log-rank and BPP versus BQP remain unresolved.

## Build and check

Use Python 3.10+, Tectonic 0.17.0 and the pinned packages in [requirements.txt](requirements.txt).

    python -m pip install -r requirements.txt
    python tools/build.py --tectonic /path/to/tectonic --render
    python tools/check_package.py

The optional render step produces page images for visual inspection. Tectonic may download its standard typesetting bundle if uncached. These tools only typeset and check documents; they do not publish or run the mathematical algorithm. Build and package receipts are in [verification](verification/). Rebuilding changed source requires renewed visual inspection before updating the visual receipt. The build helper was adapted from the same author's [aa-noise-influence archive](https://github.com/Quantyra/aa-noise-influence), under CC BY 4.0.

## Citation and archiving

[CITATION.cff](CITATION.cff) describes this working draft. Root [.zenodo.json](.zenodo.json) requests a publication/preprint archive and takes precedence over CFF metadata in Zenodo's GitHub ingestion. It contains no invented DOI or release date. The PDF is tracked in the repository, so it will be present in a future repository archive.

Follow [the setup instructions](publication/README.md) to enable **Quantyra/parity-degree-reduction** in Zenodo. No publishing workflow or credential is included. Enabling the connection prepares future release archiving; a later published GitHub release is a separate action.

All original package material is licensed under [CC BY 4.0](LICENSE). External papers are linked, not redistributed. OpenAI Codex assisted with derivation, source comparison, drafting and package preparation. Internal analytic and document checks are documented in [REVIEW.md](REVIEW.md); no independent peer review or formal certification is claimed.
