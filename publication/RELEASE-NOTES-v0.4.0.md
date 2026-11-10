# Version0.4.0: parity policy without the extra query logarithm

The main recursive theorem now uses at most min(n,1+[(2^(2d-1)-5)/3]log2 B) queries jointly with correctness at probability at least1-2^-b for each fixed input. The former k=ceil(log2(8nd)) multiplier is removed; total bit time/live space remain polynomial, every tape terminates and at most n queries are asked. This matches the retained existential query scale under a randomized visited-path contract.

The revised proof adds one-variable polynomial anchors, exact rank/minor discovery, a fixed-minor valuation bound for kernel repair and an improved read-all cutoff. All coefficient/rational degrees, adaptive failure costs and implementation caches are charged. The separate finite-field one-batch theorem remains.

The archive contains a complete implementation, exact reference checkers and retained receipts/logs. The initial full-policy campaign remains STOP because of missing matrix-rank-collapse coverage, despite19 good-event successes and two allowed bad-tape errors. A separate check passed total/partial rank collapse and all6,523 assertions. No research experiment was rerun for publication; a portable opt-in replay launcher is supplied with its unexecuted status disclosed.

Internal AI-assisted mathematical/source/claims/artifact review is recorded. No independent peer review, formal certification, novelty claim, improved existential depth or BPP/BQP result is asserted. PaperMill certification must cover the full revised scope.

This is a new version of the existing paper under concept DOI10.5281/zenodo.24092921. Prior version DOIs and tags remain immutable. Author, affiliation, ORCID and CC BY4.0 are unchanged; the version DOI is recorded after verified ingestion.
