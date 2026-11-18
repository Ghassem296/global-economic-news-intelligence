from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = ROOT / "docs" / "adr" / "decisions"
ADR_REGISTRY = ROOT / "docs" / "adr" / "README.md"
DOC_REGISTRY = ROOT / "docs" / "07-documentation-registry.md"

CONTROLLED_DOCUMENTS = [
    "docs/01-product-and-system-architecture.md",
    "docs/02-component-architecture-and-interfaces.md",
    "docs/03-data-model-and-storage-design.md",
    "docs/04-implementation-plan-and-roadmap.md",
    "docs/05-architecture-decision-records.md",
    "docs/06-documentation-governance-and-change-management.md",
    "docs/07-documentation-registry.md",
    "docs/README.md",
    "docs/adr/README.md",
]
EXPECTED_ADR_IDS = {f"GENI-ADR-{number:03d}" for number in range(1, 20)}
VALID_ADR_STATUSES = {
    "Proposed", "Accepted", "Rejected", "Deprecated", "Superseded", "Withdrawn"
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Cannot read {path.relative_to(ROOT)}: {exc}")


def document_version(path: Path) -> str:
    text = read_text(path)
    match = re.search(
        r"^\*\*Version:\*\*\s*([0-9]+\.[0-9]+)\s*$",
        text,
        re.MULTILINE,
    )
    if not match:
        fail(f"Missing or invalid version metadata: {path.relative_to(ROOT)}")
    return match.group(1)


def version_in_registry(relative_path: str) -> str:
    registry_lines = read_text(DOC_REGISTRY).splitlines()
    matching_rows: list[list[str]] = []
    for line in registry_lines:
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[2] == f"`{relative_path}`":
            matching_rows.append(cells)
    if len(matching_rows) != 1:
        fail(
            f"Expected exactly one table row for {relative_path}; "
            f"found {len(matching_rows)}"
        )
    return matching_rows[0][3]


def validate_document_versions() -> None:
    for relative in CONTROLLED_DOCUMENTS:
        actual = document_version(ROOT / relative)
        recorded = version_in_registry(relative)
        if actual != recorded:
            fail(
                f"Version mismatch for {relative}: "
                f"file={actual}, registry={recorded}"
            )


def validate_adrs() -> None:
    paths = sorted(ADR_DIR.glob("GENI-ADR-*.md"))
    ids: list[str] = []
    for path in paths:
        match = re.match(r"^(GENI-ADR-\d{3})-", path.name)
        if not match:
            fail(f"Invalid ADR filename: {path.name}")
        adr_id = match.group(1)
        ids.append(adr_id)

        text = read_text(path)
        status = re.search(r"^\*\*Status:\*\*\s*([A-Za-z]+)", text, re.MULTILINE)
        if not status:
            fail(f"Missing ADR status: {path.name}")
        if status.group(1) not in VALID_ADR_STATUSES:
            fail(f"Invalid ADR status {status.group(1)} in {path.name}")

        adr_registry_text = read_text(ADR_REGISTRY)
        adr_rows: list[list[str]] = []
        for line in adr_registry_text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and cells[0] == adr_id:
                adr_rows.append(cells)
        if len(adr_rows) != 1 or len(adr_rows[0]) < 5:
            fail(f"Expected exactly one complete ADR registry row for {adr_id}")
        if adr_rows[0][3] != status.group(1):
            fail(
                f"ADR status mismatch for {adr_id}: "
                f"file={status.group(1)}, registry={adr_rows[0][3]}"
            )
        if adr_rows[0][4] != f"`decisions/{path.name}`":
            fail(f"ADR path mismatch for {adr_id}: registry={adr_rows[0][4]}")

        relative = path.relative_to(ROOT).as_posix()
        actual_version = document_version(path)
        recorded_version = version_in_registry(relative)
        if actual_version != recorded_version:
            fail(
                f"ADR version mismatch for {relative}: "
                f"file={actual_version}, registry={recorded_version}"
            )

    if (
        len(paths) != len(EXPECTED_ADR_IDS)
        or set(ids) != EXPECTED_ADR_IDS
        or len(ids) != len(set(ids))
    ):
        fail(
            "Expected exactly one ADR-001 through ADR-019; "
            f"found {len(paths)} files: {sorted(ids)}"
        )

    registry_text = read_text(ADR_REGISTRY)
    priority_section = registry_text.split(
        "## 12. Initial Priority for ADR Development", 1
    )
    if len(priority_section) != 2:
        fail("ADR priority section not found")
    priority_body = priority_section[1].split("## 13.", 1)[0]
    priority_ids = re.findall(r"GENI-ADR-\d{3}", priority_body)
    if (
        len(priority_ids) != len(EXPECTED_ADR_IDS)
        or set(priority_ids) != EXPECTED_ADR_IDS
        or len(priority_ids) != len(set(priority_ids))
    ):
        fail("Every registered ADR must appear exactly once in the priority table")



def validate_markdown_links() -> None:
    """Verify every local inline Markdown link resolves inside the repository."""
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        content = read_text(source)
        for match in link_pattern.finditer(content):
            destination = match.group(1).strip()
            if destination.startswith("<") and ">" in destination:
                destination = destination[1:destination.index(">")]
            else:
                destination = destination.split(maxsplit=1)[0] if destination else ""
            if not destination or destination.startswith("#"):
                continue
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            relative_target = unquote(parsed.path)
            if not relative_target:
                continue
            target = (
                ROOT / relative_target.lstrip("/")
                if relative_target.startswith("/")
                else source.parent / relative_target
            )
            if not target.exists():
                fail(
                    f"Broken Markdown link in {source.relative_to(ROOT)}: "
                    f"{destination}"
                )


def validate_review_contract_alignment() -> None:
    """Keep the six canonical review families represented across key contracts."""
    review_documents = [
        "docs/02-component-architecture-and-interfaces.md",
        "docs/03-data-model-and-storage-design.md",
        "docs/04-implementation-plan-and-roadmap.md",
        "docs/adr/decisions/GENI-ADR-014-human-review-corrections-and-withdrawals.md",
    ]
    families = {
        "ARTICLE_DEDUPLICATION",
        "EVENT_MATCHING",
        "CLAIM_ASSESSMENT",
        "REPORT_VERSION",
        "PUBLICATION_OPERATION",
        "CONTENT_RIGHTS",
    }
    for relative in review_documents:
        content = read_text(ROOT / relative)
        missing = sorted(family for family in families if family not in content)
        if missing:
            fail(f"Review-family contract is incomplete in {relative}: {missing}")
        if "REPORT_VERSION" not in content or "PUBLICATION_OPERATION" not in content:
            fail(f"Publication review families are not distinguished in {relative}")


def validate_event_identity_operation_contract() -> None:
    """Protect operation history, survivor cardinality, and recovery semantics."""
    identity_documents = [
        "docs/02-component-architecture-and-interfaces.md",
        "docs/03-data-model-and-storage-design.md",
        "docs/04-implementation-plan-and-roadmap.md",
        "docs/adr/decisions/GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md",
    ]
    for relative in identity_documents:
        content = read_text(ROOT / relative)
        if "EventIdentityOperationHistory" not in content:
            fail(f"Missing EventIdentityOperationHistory contract in {relative}")
        if "RECONCILIATION_REQUIRED" not in content:
            fail(f"Missing identity-operation reconciliation state in {relative}")
    data_model = read_text(ROOT / "docs/03-data-model-and-storage-design.md")
    for required in (
        "including the selected survivor",
        "exactly one output Event equal to that survivor",
        "The only permitted input/output overlap is the MERGE survivor",
        "EventIdentityOperationHistory",
    ):
        if required not in data_model:
            fail(f"Data-model identity-operation invariant is missing: {required}")


def main() -> None:
    validate_document_versions()
    validate_adrs()
    validate_markdown_links()
    validate_review_contract_alignment()
    validate_event_identity_operation_contract()
    print(
        "Documentation validation passed: controlled document versions, "
        "all 19 ADR files/statuses/paths, ADR registry versions and priorities, "
        "local Markdown links, Human Review family alignment, and event identity-operation invariants."
    )


if __name__ == "__main__":
    main()
