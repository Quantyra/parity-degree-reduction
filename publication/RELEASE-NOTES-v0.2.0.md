# Degree reduction and recursive parity queries ? v0.2.0

First archived preprint, expanding the unreleased v0.1.0 working draft. Includes the PDF, LaTeX source, metadata, licensing and document-check receipts.

Retains polynomial-time construction of one degree-reducing parity batch and adds a complete on-demand recursive policy from the original explicit Boolean ANF. For each fixed hidden input, correctness and min(n,O(1+4^d log(s) log(nd))) parity queries hold jointly with probability at least 1-delta. Bit time is 2^O(d log(d+1))*poly(n,S,log(1/delta)), with explicit precision encoding and polynomial working space. The unconditional query cap is n.

The proof computes Boolean finite differences before scalar extension, retains a compact affine map, separates field size from error amplification, and supplies exact quadratic leaves and full resource accounting. It is an attributed algorithmic consequence of Zhang and Moshkovitz?Zhu. It does not improve the stronger existential query bound, yield an all-input correct sampled tree, or resolve unrestricted XOR log-rank or BPP versus BQP.

Internal AI-assisted mathematical/source/claims/artifact review only; no implementation, independent peer review or Lean certification. Novelty and publication significance remain unestablished. Daniel Fredriksen, Quantyra Inc., ORCID 0009-0002-9123-7435. CC BY 4.0.
