from __future__ import annotations

import re
import sys
import subprocess
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
    "docs/08-security-architecture-and-threat-model.md",
    "docs/09-api-and-integration-contracts.md",
    "docs/10-source-credibility-and-independence.md",
    "docs/11-economic-taxonomy-specification.md",
    "docs/12-testing-and-evaluation-strategy.md",
    "docs/13-deployment-operations-and-observability.md",
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



def markdown_heading_anchors(content: str) -> set[str]:
    """Return GitHub-style heading anchors and explicit HTML anchors."""
    text = markdown_content_without_fences(content)
    anchors: set[str] = set()
    used: dict[str, int] = {}
    for explicit in re.findall(r"""<(?:a|span)\b[^>]*\bid=["']([^"']+)["']""", text, re.IGNORECASE):
        anchors.add(explicit)
    tick = chr(96)
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = match.group(1)
        heading = re.sub(r"!?" + re.escape("[") + r"([^]]+)" + re.escape("]") + re.escape("(") + r"[^)]+" + re.escape(")"), r"\1", heading)
        heading = re.sub(re.escape(tick) + r"([^" + re.escape(tick) + r"]+)" + re.escape(tick), r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", heading)
        heading = re.sub(r"[!*_~]", "", heading)
        heading = heading.lower().strip()
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        slug = re.sub(r"\s+", "-", slug).strip("-")
        count = used.get(slug, 0)
        used[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def validate_markdown_links() -> None:
    """Verify local Markdown file paths and fragment targets."""
    link_pattern = re.compile(r"!?" + re.escape("[") + r"[^]]*" + re.escape("]") + re.escape("(") + r"([^)]+)" + re.escape(")"))
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        content = markdown_content_without_fences(read_text(source))
        for match in link_pattern.finditer(content):
            destination = match.group(1).strip()
            if destination.startswith("<") and ">" in destination:
                destination = destination[1:destination.index(">")]
            else:
                destination = destination.split(maxsplit=1)[0] if destination else ""
            if not destination:
                continue
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                continue
            relative_target = unquote(parsed.path)
            target = source if not relative_target else (
                ROOT / relative_target.lstrip("/")
                if relative_target.startswith("/")
                else source.parent / relative_target
            )
            if not target.exists():
                fail(
                    f"Broken Markdown link in {source.relative_to(ROOT)}: "
                    f"{destination}"
                )
            if parsed.fragment:
                fragment = unquote(parsed.fragment)
                anchors = markdown_heading_anchors(read_text(target))
                if fragment not in anchors:
                    fail(
                        f"Broken Markdown heading anchor in "
                        f"{source.relative_to(ROOT)}: {destination}"
                    )


def validate_markdown_table_structure() -> None:
    """Validate Markdown table header/separator widths and every data-row width."""
    separator_pattern = re.compile(
        r"^[|]\s*:?-{3,}:?\s*(?:[|]\s*:?-{3,}:?\s*)+[|]$"
    )
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        lines = markdown_content_without_fences(read_text(source)).splitlines()
        index = 0
        while index < len(lines) - 1:
            header = lines[index].strip()
            separator = lines[index + 1].strip()
            if not (
                header.startswith("|")
                and header.endswith("|")
                and separator_pattern.match(separator)
            ):
                index += 1
                continue
            expected = len(header[1:-1].split("|"))
            separator_columns = len(separator[1:-1].split("|"))
            if expected != separator_columns:
                fail(
                    f"Markdown table header/separator width mismatch in "
                    f"{source.relative_to(ROOT)} at line {index + 1}: "
                    f"header={expected}, separator={separator_columns}"
                )
            row = index + 2
            while row < len(lines):
                candidate = lines[row].strip()
                if not (candidate.startswith("|") and candidate.endswith("|")):
                    break
                actual = len(candidate[1:-1].split("|"))
                if actual != expected:
                    fail(
                        f"Markdown table row width mismatch in "
                        f"{source.relative_to(ROOT)} at line {row + 1}: "
                        f"expected={expected}, actual={actual}"
                    )
                row += 1
            index = row


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



def markdown_content_without_fences(content: str) -> str:
    """Remove fenced code blocks before treating metadata-like examples as metadata."""
    output: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    tick = chr(96)
    for line in content.splitlines():
        stripped = line.lstrip()
        marker_char = None
        if stripped.startswith("~~~"):
            marker_char = "~"
        elif stripped.startswith(tick * 3):
            marker_char = tick
        if fence_char is None:
            if marker_char is not None:
                fence_char = marker_char
                fence_length = len(stripped) - len(stripped.lstrip(marker_char))
                continue
            output.append(line)
            continue
        if marker_char == fence_char:
            marker_length = len(stripped) - len(stripped.lstrip(marker_char))
            if marker_length >= fence_length:
                fence_char = None
                fence_length = 0
        continue
    return "\n".join(output)


def validate_duplicate_version_metadata() -> None:
    """Header/footer Version metadata must not disagree within a Markdown document."""
    for path in sorted(ROOT.rglob("*.md")):
        text = markdown_content_without_fences(read_text(path))
        versions = re.findall(
            r"^\*\*Version:\*\*\s*([0-9]+\.[0-9]+)\s*$",
            text,
            re.MULTILINE,
        )
        if versions and any(version != versions[0] for version in versions[1:]):
            fail(
                f"Duplicate Version metadata disagrees in {path.relative_to(ROOT)}: "
                f"{versions}"
            )


def metadata_values(text: str, field: str) -> list[str]:
    prefix = f"**{field}:**"
    tick = chr(96)
    values = []
    for line in text.splitlines():
        if line.startswith(prefix):
            values.append(line[len(prefix):].strip().strip(tick).strip())
    return values


def validate_document_footer_metadata() -> None:
    """Check duplicated document footer identity and version fields where defined."""
    checks = {
        "docs/04-implementation-plan-and-roadmap.md": {
            "Document ID": "GENI-PLAN-004",
        },
        "docs/README.md": {
            "Document ID": "GENI-DOC-INDEX-001",
            "Document": "docs/README.md",
        },
    }
    for relative, expected_fields in checks.items():
        text = markdown_content_without_fences(read_text(ROOT / relative))
        for field, expected in expected_fields.items():
            values = metadata_values(text, field)
            minimum = 1 if field == "Document" else 2
            if len(values) < minimum or values[-1] != expected:
                fail(
                    f"Incorrect or missing footer {field} in {relative}: "
                    f"expected {expected!r}, found {values}"
                )
        versions = metadata_values(text, "Version")
        if len(versions) < 2 or versions[-1] != versions[0]:
            fail(f"Footer version does not match header in {relative}: {versions}")


def validate_adr_history_versions() -> None:
    """The latest ADR decision-history row must match current header/footer metadata."""
    tick = chr(96)
    for path in sorted(ADR_DIR.glob("GENI-ADR-*.md")):
        text = markdown_content_without_fences(read_text(path))
        adr_id_match = re.search(
            r"^\*\*ADR ID:\*\*\s*(GENI-ADR-[0-9]{3})",
            text,
            re.MULTILINE,
        )
        header_version = re.search(
            r"^\*\*Version:\*\*\s*([0-9]+\.[0-9]+)",
            text,
            re.MULTILINE,
        )
        header_status = re.search(
            r"^\*\*Status:\*\*\s*([A-Za-z]+)",
            text,
            re.MULTILINE,
        )
        filename_match = re.match(r"^(GENI-ADR-[0-9]{3})-", path.name)
        if not adr_id_match or not header_version or not header_status or not filename_match:
            fail(f"Missing ADR identity/version/status metadata: {path.name}")
        if adr_id_match.group(1) != filename_match.group(1):
            fail(f"ADR ID does not match filename: {path.name}")

        footer_files = metadata_values(text, "File")
        footer_ids = metadata_values(text, "ADR ID")
        footer_versions = metadata_values(text, "Version")
        footer_statuses = metadata_values(text, "Status")
        if footer_files and footer_files[-1] != path.name:
            fail(f"ADR footer filename does not match path: {path.name}")
        if len(footer_ids) > 1 and footer_ids[-1] != filename_match.group(1):
            fail(f"ADR footer ID does not match header: {path.name}")
        if len(footer_versions) > 1 and footer_versions[-1] != header_version.group(1):
            fail(f"ADR footer version does not match header: {path.name}")
        if len(footer_statuses) > 1 and footer_statuses[-1] != header_status.group(1):
            fail(f"ADR footer status does not match header: {path.name}")

        history_section = re.search(
            r"^##\s+[0-9]+\.\s+Decision History\s*$([\s\S]*)$",
            text,
            re.MULTILINE,
        )
        if not history_section:
            fail(f"Missing Decision History section: {path.name}")
        rows = re.findall(
            r"^\|\s*([0-9]+\.[0-9]+)\s*\|\s*[^|]+\|\s*([^|]+)\|",
            history_section.group(1),
            re.MULTILINE,
        )
        if not rows:
            fail(f"Missing versioned Decision History rows: {path.name}")
        latest_version, latest_status = rows[-1]
        if latest_version != header_version.group(1):
            fail(
                f"ADR history/header version mismatch in {path.name}: "
                f"header={header_version.group(1)}, history={latest_version}"
            )
        if latest_status.strip() != header_status.group(1):
            fail(
                f"ADR history/header status mismatch in {path.name}: "
                f"header={header_status.group(1)}, history={latest_status.strip()}"
            )
        numeric_versions = [
            tuple(int(part) for part in version.split("."))
            for version, _ in rows
        ]
        if numeric_versions != sorted(numeric_versions):
            fail(f"ADR Decision History is not monotonic: {path.name}")


def extract_section(content: str, start: str, end: str, label: str) -> str:
    start_index = content.find(start)
    end_index = content.find(end, start_index + len(start)) if start_index >= 0 else -1
    if start_index < 0 or end_index < 0:
        fail(f"Cannot locate {label} section boundaries")
    return content[start_index:end_index]


def repository_names(section: str) -> set[str]:
    """Extract Repository identifiers from exact Markdown code spans."""
    tick = chr(96)
    return set(re.findall(tick + r"([A-Za-z0-9]+Repository)" + tick, section))


def validate_repository_inventory_alignment() -> None:
    """The component repository list, data-model list, and ownership crosswalk must match."""
    component = read_text(ROOT / "docs/02-component-architecture-and-interfaces.md")
    data_model = read_text(ROOT / "docs/03-data-model-and-storage-design.md")
    component_list = extract_section(
        component,
        "## 6. Repository Interfaces",
        "### 6.1 Contract Completeness",
        "Document 02 repository inventory",
    )
    data_list = extract_section(
        data_model,
        "## 23. Repository Contracts",
        "## 24. Migration Strategy",
        "Document 03 repository inventory",
    )
    crosswalk = extract_section(
        component,
        "## 6.3 Repository-to-Aggregate, Writer, and Transaction Crosswalk",
        "## 7. Workflow Contracts",
        "Document 02 repository crosswalk",
    )
    component_names = repository_names(component_list)
    data_names = repository_names(data_list)
    crosswalk_names = repository_names(crosswalk)
    if component_names != data_names:
        fail(
            "Repository inventory mismatch: "
            f"only Document 02={sorted(component_names - data_names)}; "
            f"only Document 03={sorted(data_names - component_names)}"
        )
    if component_names != crosswalk_names:
        fail(
            "Repository ownership crosswalk mismatch: "
            f"unmapped={sorted(component_names - crosswalk_names)}; "
            f"unknown={sorted(crosswalk_names - component_names)}"
        )


def validate_first_slice_review_set() -> None:
    """Keep all six review families and first-slice activation explicit across key documents."""
    documents = [
        "docs/01-product-and-system-architecture.md",
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
    for relative in documents:
        content = read_text(ROOT / relative)
        missing = sorted(family for family in families if family not in content)
        if missing:
            fail(f"Review family vocabulary incomplete in {relative}: {missing}")
        if "first implementation slice" not in content.lower():
            fail(f"First-slice Review activation is not stated in {relative}")


def validate_event_identity_operation_contract() -> None:
    """Protect durable operation history, survivor cardinality, and recovery semantics."""
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
    required = (
        "event_identity_operation_histories",
        "EventIdentityOperationHistoryRepository",
        "expected_event_history_version",
        "exactly one output Event equal to that survivor",
        "The only permitted input/output overlap is the MERGE survivor",
    )
    for term in required:
        if term not in data_model:
            fail(f"Data-model identity-operation invariant is missing: {term}")


def validate_distribution_authorization_contract() -> None:
    """Ensure delivery authorization covers exact payload and every source-derived scope."""
    required_by_document = {
        "docs/01-product-and-system-architecture.md": (
            "content-scope fingerprint",
            "every source-derived content scope",
            "currently effective publication operation",
        ),
        "docs/02-component-architecture-and-interfaces.md": (
            "DistributionAuthorizationRepository",
            "DistributionAuthorizationRightsLink",
            "authorized_content_scope_fingerprint",
            "rights_assessment_set_fingerprint",
            "content_scope_fingerprint",
        ),
        "docs/03-data-model-and-storage-design.md": (
            "event_identity_operation_histories",
            "distribution_authorization_rights_links",
            "DistributionAuthorizationRepository",
            "EventIdentityOperationHistoryRepository",
            "authorized_content_scope_fingerprint",
            "rights_assessment_set_fingerprint",
            "content_scope_fingerprint",
            "CUSTOMER_DISTRIBUTION",
        ),
        "docs/04-implementation-plan-and-roadmap.md": (
            "DistributionAuthorizationRightsLink",
            "rights-assessment-set fingerprint",
            "content-scope fingerprint",
            "CUSTOMER_DISTRIBUTION",
        ),
        "docs/adr/decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md": (
            "every exact source-derived content scope",
            "complete set of exact allowed RightsAssessment references",
            "RFC 8785 JSON Canonicalization Scheme",
            "outbound_payload_sha256",
            "upstream rights dependencies",
            "fail closed",
        ),
    }
    for relative, required_terms in required_by_document.items():
        content = read_text(ROOT / relative)
        for term in required_terms:
            if term not in content:
                fail(f"Distribution authorization contract missing {term!r} in {relative}")



def validate_registry_snapshot_provenance() -> None:
    """Verify that the registry's inspected baseline is a real commit in this checkout's history."""
    registry = read_text(DOC_REGISTRY)
    matches = re.findall(
        r"^\*\*Baseline Commit Inspected:\*\*\s+`([0-9a-f]{40})`\s*$",
        registry,
        re.MULTILINE,
    )
    if len(matches) != 1:
        fail(
            "Documentation registry must contain exactly one full 40-character "
            "Baseline Commit Inspected value"
        )
    baseline = matches[0]
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if exists.returncode != 0:
        fail(f"Registry snapshot commit is not available in Git history: {baseline}")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline, "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if ancestor.returncode != 0:
        fail(
            "Registry snapshot commit is not an ancestor of the checked-out revision: "
            f"{baseline}"
        )


def validate_roadmap_document_inventory() -> None:
    """Ensure the proposed docs tree lists every Markdown document currently in docs/."""
    roadmap = read_text(ROOT / "docs/04-implementation-plan-and-roadmap.md")
    structure = extract_section(
        roadmap,
        "## 5. Project Structure",
        "## 6. Development Stage 0",
        "Roadmap project structure",
    )
    code_block = re.search(r"```text\s*\n([\s\S]*?)\n```", structure)
    if not code_block:
        fail("Roadmap project structure text tree is missing")
    lines = code_block.group(1).splitlines()
    root_line = next(
        (line.strip().rstrip("/") for line in lines
         if line.strip() == "global-economic-news-intelligence/"),
        None,
    )
    if root_line is None:
        fail("Roadmap project structure root is missing")
    directory_stack = [root_line]
    listed_files: set[str] = set()
    for line in lines:
        match = re.match(r"^([│ ]*)(?:├──|└──)\s+(.+?)\s*$", line)
        if not match:
            continue
        depth = len(match.group(1)) // 4
        name = match.group(2).strip()
        is_directory = name.endswith("/")
        name = name.rstrip("/")
        while len(directory_stack) > depth + 1:
            directory_stack.pop()
        parent = directory_stack[: depth + 1]
        full_path = "/".join(parent[1:] + [name])
        if is_directory:
            directory_stack = parent + [name]
        else:
            listed_files.add(full_path)

    expected_files = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs").rglob("*.md")
    }
    missing = sorted(expected_files - listed_files)
    if missing:
        fail(
            "Roadmap project structure omits published Markdown documents: "
            f"{missing}"
        )

    initial_concepts = extract_section(
        roadmap,
        "### Initial Domain Concepts",
        "### Domain Rules",
        "Roadmap Stage 2 initial domain concepts",
    )
    for bullet in (
        "- ProcessingRun and ProcessingStep.",
        "- LLMUsageRecord for model execution and usage records.",
    ):
        count = initial_concepts.splitlines().count(bullet)
        if count != 1:
            fail(
                "Roadmap Stage 2 must list each runtime concept exactly once; "
                f"{bullet!r} occurs {count} times"
            )


def validate_cross_document_contracts() -> None:
    readme = read_text(ROOT / "README.md")
    data_model = read_text(ROOT / "docs/03-data-model-and-storage-design.md")
    components = read_text(ROOT / "docs/02-component-architecture-and-interfaces.md")
    source_spec = read_text(ROOT / "docs/10-source-credibility-and-independence.md")
    adr_008 = read_text(ADR_DIR / "GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md")
    adr_010 = read_text(ADR_DIR / "GENI-ADR-010-phased-text-audio-and-video-delivery.md")
    adr_011 = read_text(ADR_DIR / "GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md")
    adr_016 = read_text(ADR_DIR / "GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md")
    adr_018 = read_text(ADR_DIR / "GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md")
    index = read_text(ROOT / "docs/README.md")

    if "Energy and Natural Resources" in readme:
        fail("README taxonomy label is stale; use the canonical 'Energy and Resources' label")
    for relative in ("docs/01-product-and-system-architecture.md", "docs/11-economic-taxonomy-specification.md"):
        if "Energy and Resources" not in read_text(ROOT / relative):
            fail(f"Canonical Energy and Resources taxonomy label missing from {relative}")

    required_data_terms = (
        "source_id_from", "source_id_to", "valid_from", "valid_until",
        "relationship_version", "### 5.3.1 ArticleOriginRelationship",
        "article_revision_id_from", "### 13.2.1 ExecutionLease", "fencing_token",
        "### 13.2.2 IdempotencyRecord", "operation_scope",
        "execution_leases", "idempotency_records",
    )
    for term in required_data_terms:
        if term not in data_model:
            fail(f"Data-model cross-document contract missing {term!r}")

    required_repositories = (
        "ArticleOriginRelationshipRepository",
        "SourceRelationshipRepository",
        "ExecutionLeaseRepository",
        "IdempotencyRecordRepository",
    )
    for term in required_repositories:
        if term not in components:
            fail(f"Component repository contract missing {term!r}")
        if term not in data_model:
            fail(f"Data-model repository inventory missing {term!r}")

    required_execution_terms = (
        "atomic lease acquisition, renewal, release",
        "current-fencing-token validation",
        "same UnitOfWork boundary",
        "request-fingerprint conflict detection",
    )
    for term in required_execution_terms:
        if term not in components:
            fail(f"Component execution/recovery contract missing {term!r}")

    required_recovery_terms = (
        "stale-worker fencing-token rejection",
        "atomic lease renewal/release",
        "IdempotencyRecord replay",
        "unknown external outcomes",
    )
    for term in required_recovery_terms:
        if term not in data_model:
            fail(f"Data-model recovery verification missing {term!r}")
    for term in ("fencing token", "request fingerprint", "unknown outcome", "reconciled before retry"):
        if term not in adr_016.lower():
            fail(f"ADR-016 persistence/recovery decision missing {term!r}")
    if "ArticleOriginRelationship" not in source_spec:
        fail("Source credibility specification does not define article-origin provenance")
    if "ORIGINAL_REPORTING is an evidence/source role" not in source_spec:
        fail("Source credibility specification must distinguish ORIGINAL_REPORTING from relationship edges")
    if "ORIGINAL_REPORTING" not in adr_008 or "not an edge type" not in adr_008:
        fail("ADR-008 must distinguish source roles from relationship edges")
    if "SourceRightsProfile" not in adr_010 or "ContentRightsProfile" in adr_010:
        fail("ADR-010 rights-profile name must match the canonical SourceRightsProfile model")
    if "ArticleProcessingRecord" not in adr_018 or "- LanguageDetectionRecord" in adr_018 or "not a separate persistent domain entity" not in adr_018:
        fail("ADR-018 language detection must use ArticleProcessingRecord; a standalone LanguageDetectionRecord is not part of the current model")

    deferred = adr_011.split("**Deferred Questions:**", 1)
    if len(deferred) != 2:
        fail("ADR-011 Deferred Questions section not found")
    deferred_body = deferred[1].split("## 8.", 1)[0]
    for obsolete in ("Detailed event lifecycle states and transitions", "Final event relationship taxonomy"):
        if obsolete in deferred_body:
            fail(f"ADR-011 still defers a baseline already defined in Section 6: {obsolete}")

    heading_four = index.find("# 4. Architectural Decision Records")
    section_313 = index.find("## 3.13 Deployment, Operations, and Observability")
    if heading_four < 0 or section_313 < 0 or heading_four < section_313:
        fail("Documentation index Section 4 must follow all Section 3 document entries")



def validate_document_registry_metadata_alignment() -> None:
    """Require every controlled document's ID, version, and lifecycle status to match its registry row."""
    registry_text = read_text(DOC_REGISTRY)
    for relative in CONTROLLED_DOCUMENTS:
        path = ROOT / relative
        content = markdown_content_without_fences(read_text(path))
        values = {
            field: metadata_values(content, field)
            for field in ("Document ID", "Version", "Status")
        }
        for field, found in values.items():
            if len(found) != 1:
                fail(
                    f"Expected exactly one {field} metadata value in {relative}; "
                    f"found {len(found)}"
                )

        matching_rows: list[list[str]] = []
        for line in registry_text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if chr(96) + relative + chr(96) in cells:
                matching_rows.append(cells)

        if len(matching_rows) != 1:
            fail(
                f"Expected exactly one documentation-registry row for {relative}; "
                f"found {len(matching_rows)}"
            )
        row = matching_rows[0]
        if len(row) < 5:
            fail(f"Incomplete documentation-registry row for {relative}: {row}")
        expected = (values["Document ID"][0], values["Version"][0], values["Status"][0])
        actual = (row[0], row[3], row[4])
        if actual != expected:
            fail(
                f"Document metadata/registry mismatch for {relative}: "
                f"file(ID, version, status)={expected}; "
                f"registry(ID, version, status)={actual}"
            )


def validate_documentation_index_adr_authority() -> None:
    """The Documentation Index must link to, not duplicate, the ADR Registry inventory."""
    index = read_text(ROOT / "docs/README.md")
    if "## 4.3 Individual ADR Documents" not in index:
        fail("Documentation Index must retain its Individual ADR Documents guidance section")
    if re.search(r"^\\|\\s*GENI-ADR-\\d{3}\\s*\\|", index, re.MULTILINE):
        fail("Documentation Index duplicates individual ADR inventory rows")
    if "[ADR Registry](adr/README.md)" not in index:
        fail("Documentation Index must link to the authoritative ADR Registry")


def validate_adr_registry_title_alignment() -> None:
    """Keep each ADR title in its file metadata identical to the authoritative registry."""
    registry_text = read_text(ADR_REGISTRY)
    for path in sorted(ADR_DIR.glob("GENI-ADR-*.md")):
        content = markdown_content_without_fences(read_text(path))
        title = re.search(r"^\\*\\*Title:\\*\\*\\s*(.+?)\\s*$", content, re.MULTILINE)
        if not title:
            fail(f"Missing ADR title metadata: {path.name}")
        adr_id_match = re.match(r"^(GENI-ADR-\\d{3})-", path.name)
        if not adr_id_match:
            fail(f"Invalid ADR filename: {path.name}")
        adr_id = adr_id_match.group(1)
        rows = []
        for line in registry_text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells and cells[0] == adr_id:
                rows.append(cells)
        if len(rows) != 1 or len(rows[0]) < 5:
            fail(f"Expected exactly one complete ADR registry row for {adr_id}")
        if rows[0][1] != title.group(1):
            fail(
                f"ADR title mismatch for {adr_id}: "
                f"file={title.group(1)!r}, registry={rows[0][1]!r}"
            )


def main() -> None:
    validate_registry_snapshot_provenance()
    validate_roadmap_document_inventory()
    validate_cross_document_contracts()
    validate_document_versions()
    validate_document_registry_metadata_alignment()
    validate_documentation_index_adr_authority()
    validate_adr_registry_title_alignment()
    validate_adrs()
    validate_duplicate_version_metadata()
    validate_document_footer_metadata()
    validate_adr_history_versions()
    validate_markdown_links()
    validate_markdown_table_structure()
    validate_review_contract_alignment()
    validate_first_slice_review_set()
    validate_repository_inventory_alignment()
    validate_event_identity_operation_contract()
    validate_distribution_authorization_contract()
    print(
        "Documentation validation passed: cross-document taxonomy/source-origin/workflow contracts, controlled versions and document ID/version/status registry parity, ADR title alignment and single-source inventory, duplicate versions, "
        "all 19 ADR files/statuses/paths/history/footer metadata, ADR registry versions and priorities, "
        "local Markdown file paths and heading anchors, Markdown table structure, Review family activation, repository inventory/crosswalk parity, "
        "event identity-operation history/recovery, multi-source distribution authorization, registry snapshot provenance, and roadmap/document inventory parity."
    )


if __name__ == "__main__":
    main()
