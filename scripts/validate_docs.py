from __future__ import annotations

import re
import sys
from pathlib import Path

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
        r"^\\*\\*Version:\\*\\*\\s*([0-9]+\\.[0-9]+)\\s*$",
        text,
        re.MULTILINE,
    )
    if not match:
        fail(f"Missing or invalid version metadata: {path.relative_to(ROOT)}")
    return match.group(1)


def version_in_registry(relative_path: str) -> str:
    registry_lines = read_text(DOC_REGISTRY).splitlines()
    matching_rows = [line for line in registry_lines if f"`{relative_path}`" in line]
    if len(matching_rows) != 1:
        fail(
            f"Expected exactly one registry row for {relative_path}; "
            f"found {len(matching_rows)}"
        )
    cells = [cell.strip() for cell in matching_rows[0].strip().strip("|").split("|")]
    if len(cells) < 4:
        fail(f"Malformed registry row for {relative_path}")
    return cells[3]


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
        match = re.match(r"^(GENI-ADR-\\d{3})-", path.name)
        if not match:
            fail(f"Invalid ADR filename: {path.name}")
        adr_id = match.group(1)
        ids.append(adr_id)

        text = read_text(path)
        status = re.search(r"^\\*\\*Status:\\*\\*\\s*([A-Za-z]+)", text, re.MULTILINE)
        if not status:
            fail(f"Missing ADR status: {path.name}")
        if status.group(1) not in VALID_ADR_STATUSES:
            fail(f"Invalid ADR status {status.group(1)} in {path.name}")

        if path.name not in read_text(ADR_REGISTRY):
            fail(f"ADR missing from ADR registry: {path.name}")

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
    priority_ids = re.findall(r"GENI-ADR-\\d{3}", priority_body)
    if (
        len(priority_ids) != len(EXPECTED_ADR_IDS)
        or set(priority_ids) != EXPECTED_ADR_IDS
        or len(priority_ids) != len(set(priority_ids))
    ):
        fail("Every registered ADR must appear exactly once in the priority table")


def main() -> None:
    validate_document_versions()
    validate_adrs()
    print(
        "Documentation validation passed: controlled document versions, "
        "all 19 ADR files/statuses, ADR registry versions, and priority coverage."
    )


if __name__ == "__main__":
    main()
