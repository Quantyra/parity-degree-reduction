# Polynomial-time parity-query policies for explicit Boolean polynomials

**Daniel Fredriksen · Quantyra Inc. · [ORCID 0009-0002-9123-7435](https://orcid.org/0009-0002-9123-7435)**

[Manuscript PDF](manuscript/main.pdf) · [LaTeX source](manuscript/main.tex) · [Review and scope](REVIEW.md) · [Publication record](publication/README.md)

**Version 0.3.0: published and archive-verified.** [Version DOI10.5281/zenodo.24093687](https://doi.org/10.5281/zenodo.24093687); [release](https://github.com/Quantyra/parity-degree-reduction/releases/tag/v0.3.0). All24archived files match release5f55a6371b0cac793f8784ffabdb1936ea7152be byte for byte; [verification receipt](verification/publication-v0.3.0.json). The earlier [v0.2.0 archive](https://doi.org/10.5281/zenodo.24092922) remains immutable; [concept DOI](https://doi.org/10.5281/zenodo.24092921). Current release/archive status and exact identifiers are in the publication record.

The main theorem gives a uniformly polynomial-time on-demand parity-query policy for an explicit squarefree Boolean ANF p of original degree d and encoding length S. For each fixed hidden x, with probability at least 1-delta, it returns p(x) correctly and asks at most min(n,O(1+4^d log(s) log(nd))) parity queries, where s is Fourier sparsity. Fourier norm and sparsity are analysis quantities, not inputs. Total bit time and working space are poly(n,S,log(1/delta)) with fixed exponents independent of d. An explicit precision input is used; arbitrary rational parsing has a separately charged cost. Every random tape terminates and uses at most n queries.

A factor-partition recurrence groups repeated Boolean variables before exterior-algebra evaluation. A proved norm gap justifies reading all coordinates when the query allowance already permits n; otherwise 4^d<6n+16, making the recurrence's tables and work polynomial. The original ANF and a compact affine map supply all inputs. This strengthens v0.2.0's degree-parameterized computation while preserving its exact query/error guarantee.

The paper retains the separately useful polynomial-time construction of one fixed parity batch, with exact degree reduction on every coset on its success event. The structural inputs are [Zhang v1](https://arxiv.org/abs/2611.03452v1) and [Moshkovitz-Zhu v1](https://arxiv.org/abs/2603.11038v1). The existential query bound is stronger by a logarithmic factor. The recursive guarantee is per input, not a globally correct sampled tree. Novelty remains unestablished; unrestricted XOR log-rank and BPP versus BQP remain unresolved.

## Evidence and build

The argument and costs are analytic. [One retained exact diagnostic](verification/evaluator-diagnostic.json) passed 256 fixtures; its [source](tools/check_evaluator.py) compares the component evaluator against truth-table Boolean reduction and determinant evaluation. It is not an implementation or benchmark of the complete policy and does not prove asymptotic correctness. The original run is preserved, not repeated for publication.

Use Python 3.10+, Tectonic 0.17.0 and [requirements.txt](requirements.txt):

    python -m pip install -r requirements.txt
    python tools/build.py --tectonic /path/to/tectonic --render
    python tools/check_package.py

Build tools never publish. Inspect changed PDF pages before updating [visual evidence](verification/visual.json). [Build](verification/build.json) and [package](verification/package.json) receipts establish document consistency, not mathematical certification.

## Citation and status

[CITATION.cff](CITATION.cff) and [.zenodo.json](.zenodo.json) retain the confirmed author, affiliation, ORCID and preprint metadata. Original package material is licensed under [CC BY 4.0](LICENSE). External papers are cited, not redistributed. OpenAI Codex assisted derivation, source comparison, drafting and package preparation. [REVIEW.md](REVIEW.md) records internal AI-assisted mathematical, source, claims and artifact checks. No independent peer review or Lean certification is claimed. PaperMill retains publication and queued full-manuscript certification ownership.
