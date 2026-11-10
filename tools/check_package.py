"""Check manuscript metadata, document identity and the public package; never publish."""
import ast
import hashlib
import json
from pathlib import Path
import re

import pymupdf
import yaml

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Polynomial-time parity-query policies for explicit Boolean polynomials"
REPO = "https://github.com/Quantyra/parity-degree-reduction"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    build = json.loads((ROOT / "verification/build.json").read_text(encoding="utf-8"))
    visual = json.loads((ROOT / "verification/visual.json").read_text(encoding="utf-8"))
    preferred = citation["preferred-citation"]
    assert zenodo["title"] == preferred["title"] == TITLE
    assert citation["version"] == zenodo["version"] == "0.4.0"
    assert citation["repository-code"] == REPO
    assert preferred["url"] == REPO + "/blob/main/manuscript/main.pdf"
    assert citation["license"] == zenodo["license"] == "CC-BY-4.0"
    assert preferred["authors"] == citation["authors"]
    author, creator = citation["authors"][0], zenodo["creators"][0]
    assert creator["name"] == f"{author['family-names']}, {author['given-names']}"
    assert creator["affiliation"] == author["affiliation"] == "Quantyra Inc."
    assert author["orcid"] == "https://orcid.org/" + creator["orcid"]
    assert creator["orcid"] == "0009-0002-9123-7435"
    assert zenodo["upload_type"] == "publication"
    assert zenodo["publication_type"] == "preprint"
    assert "doi" not in zenodo and "publication_date" not in zenodo
    publication_path = ROOT / "verification/publication-v0.4.0.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text(encoding="utf-8"))
        assert publication["status"] == "PUBLISHED_AND_VERIFIED"
        assert citation["doi"] == preferred["doi"] == publication["version_doi"]
        assert str(citation["date-released"]) == publication["github_published_at"][:10]
        assert publication["pdf_sha256"] == build["pdf_sha256"]
    else:
        assert "doi" not in preferred and "doi" not in citation and "date-released" not in citation
    assert build["source_sha256"] == sha(ROOT / "manuscript/main.tex")
    assert build["pdf_sha256"] == sha(ROOT / "manuscript/main.pdf")
    assert build["final_log_diagnostics"] == []
    assert visual["pdf_sha256"] == build["pdf_sha256"]
    assert visual["pages_inspected"] == list(range(1, build["pages"] + 1))
    assert visual["verdict"] == "PASS_DOCUMENT_LAYOUT"

    diagnostic = json.loads((ROOT / "verification/evaluator-diagnostic.json").read_text(encoding="utf-8"))
    assert diagnostic["status"] == "PASS" and diagnostic["fixtures"] == 256
    assert diagnostic["runs"] == 1 and diagnostic["timeout_seconds"] == 120
    assert diagnostic["source_sha256"] == sha(ROOT / "tools/check_evaluator.py")

    provenance = json.loads((ROOT / "verification/policy-provenance.json").read_text(encoding="utf-8"))
    assert provenance["source_commit"] == "8ee54bd8520a2be3e37b8bce7b582b8cdcee5150"
    assert len(provenance["files"]) == 8
    for name, item in provenance["files"].items():
        assert item["byte_identical"] and sha(ROOT / name) == item["sha256"], name
    runs = ROOT / "verification/runs"
    early = json.loads((runs / "s236-complete-policy-run1-2026-11-09.json").read_text())
    failed = json.loads((runs / "s236-complete-policy-run2-2026-11-09.json").read_text())
    passed = json.loads((runs / "s237-rank-collapse-run1-2026-11-09.json").read_text())
    assert early["status"] == "STOP" and early["finished_cases"] == []
    assert failed["status"] == "STOP" and failed["exit_code"] == 1
    assert len(failed["finished_cases"]) == 21 and failed["completion"] is None
    assert passed["status"] == "PASS" and passed["exit_code"] == 0
    assert passed["completion"]["counts"]["assertions"] == 6523
    assert passed["completion"]["rank_drops"] == [[2, 0], [4, 2]]
    for receipt, log in [(failed, "s236-complete-policy-run2-2026-11-09.jsonl"),
                         (passed, "s237-rank-collapse-run1-2026-11-09.jsonl")]:
        assert sha(runs / log) == receipt["stdout_sha256"]
        for name, digest in receipt["source_sha256"].items():
            exported = ROOT / "implementation" / name
            if exported.exists():
                assert sha(exported) == digest, name
        events = [json.loads(line) for line in (runs / log).read_text().splitlines()]
        if receipt is passed:
            assert events[-1] == passed["completion"]
    for code in list((ROOT / "implementation").glob("*.py")) + [ROOT / "tools/replay_policy_checks.py"]:
        ast.parse(code.read_text(encoding="utf-8"), filename=code.name)
    # Static validation only: no research module imports or experiment execution.

    pdf = pymupdf.open(ROOT / "manuscript/main.pdf")
    assert len(pdf) == build["pages"] > 0
    assert pdf.metadata["author"] == "Daniel Fredriksen"
    assert pdf.metadata["title"] == TITLE
    fonts = {font[0] for page in pdf for font in page.get_fonts()}
    assert all(xref > 0 and pdf.extract_font(xref)[3] for xref in fonts)
    all_text = "\n".join(page.get_text() for page in pdf)
    assert "Preprint, version 0.4.0" in all_text and "OpenAI Codex" in all_text
    assert "independent peer review" in " ".join(all_text.split())

    required = [
        "README.md", "AGENTS.md", "REVIEW.md", "LICENSE", "LICENSES/CC-BY-4.0.txt",
        "CITATION.cff", ".zenodo.json", ".gitattributes", ".gitignore", "requirements.txt",
        "manuscript/main.tex", "manuscript/main.pdf", "tools/build.py",
        "tools/check_package.py", "verification/build.json", "verification/visual.json",
        "publication/README.md", "publication/RELEASE-NOTES-v0.1.0.md",
        "publication/RELEASE-NOTES-v0.2.0.md", "publication/RELEASE-NOTES-v0.3.0.md",
        "verification/publication-v0.2.0.json", "verification/evaluator-diagnostic.json",
        "tools/check_evaluator.py", "verification/publication-v0.3.0.json",
        "publication/RELEASE-NOTES-v0.4.0.md", "implementation/README.md",
        "tools/replay_policy_checks.py", "verification/policy-provenance.json",
    ]
    required.extend(provenance["files"])
    if publication_path.exists():
        required.append("verification/publication-v0.4.0.json")
    for name in required:
        path = ROOT / name
        assert path.is_file() and path.stat().st_size > 0, name
        if path.suffix in (".md", ".tex", ".json", ".jsonl", ".cff", ".py"):
            data = path.read_text(encoding="utf-8")
            assert not re.search(r"[A-Za-z]:[/\\]Users[/\\]", data), name
            assert not re.search(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", data), name
            if path.suffix == ".md":
                for target in re.findall(r"\]\(([^)]+)\)", data):
                    target = target.strip("<>").split("#", 1)[0]
                    if target and "://" not in target:
                        assert (path.parent / target).exists(), (name, target)
    receipt = {
        "status": "PASS",
        "scope": "Document identities, embedded fonts, metadata, local links, static Python syntax and retained source/log provenance",
        "not_performed": [
            "Zenodo ingestion", "research experiment or replay execution",
            "formal proof verification", "independent peer review",
        ],
        "files": {name: sha(ROOT / name) for name in sorted(required)},
        "pages": len(pdf),
        "embedded_fonts": len(fonts),
        "release_or_doi_created_by_this_check": False,
    }
    (ROOT / "verification/package.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"package": "PASS", "files": len(required), "pages": len(pdf),
                      "embedded_fonts": len(fonts)}))


if __name__ == "__main__":
    main()
