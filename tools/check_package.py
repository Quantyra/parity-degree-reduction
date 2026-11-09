"""Check manuscript metadata, document identity and the public package; never publish."""
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
    assert citation["version"] == zenodo["version"] == "0.3.0"
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
    publication_path = ROOT / "verification/publication-v0.3.0.json"
    if publication_path.exists():
        publication = json.loads(publication_path.read_text(encoding="utf-8"))
        assert publication["status"] == "PUBLISHED_AND_VERIFIED"
        assert citation["doi"] == preferred["doi"] == publication["version_doi"]
        assert str(citation["date-released"]) == "2026-11-09"
        assert publication["pdf_sha256"] == build["pdf_sha256"]
    else:
        assert "doi" not in preferred and "date-released" not in citation
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

    pdf = pymupdf.open(ROOT / "manuscript/main.pdf")
    assert len(pdf) == build["pages"] > 0
    assert pdf.metadata["author"] == "Daniel Fredriksen"
    assert pdf.metadata["title"] == TITLE
    fonts = {font[0] for page in pdf for font in page.get_fonts()}
    assert all(xref > 0 and pdf.extract_font(xref)[3] for xref in fonts)
    all_text = "\n".join(page.get_text() for page in pdf)
    assert "Preprint, version 0.3.0" in all_text and "OpenAI Codex" in all_text
    assert "independent peer review" in " ".join(all_text.split())

    required = [
        "README.md", "AGENTS.md", "REVIEW.md", "LICENSE", "LICENSES/CC-BY-4.0.txt",
        "CITATION.cff", ".zenodo.json", ".gitattributes", ".gitignore", "requirements.txt",
        "manuscript/main.tex", "manuscript/main.pdf", "tools/build.py",
        "tools/check_package.py", "verification/build.json", "verification/visual.json",
        "publication/README.md", "publication/RELEASE-NOTES-v0.1.0.md",
        "publication/RELEASE-NOTES-v0.2.0.md", "publication/RELEASE-NOTES-v0.3.0.md",
        "verification/publication-v0.2.0.json", "verification/evaluator-diagnostic.json",
        "tools/check_evaluator.py",
    ]
    if publication_path.exists():
        required.append("verification/publication-v0.3.0.json")
    for name in required:
        path = ROOT / name
        assert path.is_file() and path.stat().st_size > 0, name
        if path.suffix in (".md", ".tex", ".json", ".cff", ".py"):
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
        "scope": "Document identities, embedded fonts, metadata, local links and package files",
        "not_performed": [
            "Zenodo ingestion", "algorithm implementation or benchmark",
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
