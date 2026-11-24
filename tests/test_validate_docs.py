from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_docs.py"
SPEC = importlib.util.spec_from_file_location("validate_docs", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class DocumentationValidatorTests(unittest.TestCase):
    def test_validator_has_no_shadowed_top_level_functions(self) -> None:
        tree = ast.parse(VALIDATOR_PATH.read_text(encoding="utf-8"))
        names = [node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        self.assertEqual(len(names), len(set(names)))

    def test_registry_snapshot_requires_one_full_baseline_sha(self) -> None:
        valid = "**Baseline Commit Inspected:** `a4b54e6f397558d82e6b438f03d9dbfe9944f55e`"
        self.assertEqual(validator.registry_snapshot_baseline(valid), "a4b54e6f397558d82e6b438f03d9dbfe9944f55e")

    def test_registry_snapshot_rejects_missing_or_duplicate_baseline(self) -> None:
        with self.assertRaises(SystemExit):
            validator.registry_snapshot_baseline("No baseline recorded")
        duplicate = (
            "**Baseline Commit Inspected:** `a4b54e6f397558d82e6b438f03d9dbfe9944f55e`\n"
            "**Baseline Commit Inspected:** `a4b54e6f397558d82e6b438f03d9dbfe9944f55e`"
        )
        with self.assertRaises(SystemExit):
            validator.registry_snapshot_baseline(duplicate)

    def test_document_inventory_detects_missing_and_unexpected_files(self) -> None:
        expected = {"docs/a.md", "docs/nested/b.md"}
        listed = {"docs/a.md", "docs/extra.md"}
        missing, unexpected = validator.document_inventory_difference(expected, listed)
        self.assertEqual(missing, {"docs/nested/b.md"})
        self.assertEqual(unexpected, {"docs/extra.md"})

    def test_unicode_repository_tree_parser_preserves_nested_paths(self) -> None:
        tree = """```text
global-economic-news-intelligence/
├── README.md
└── docs/
    ├── README.md
    └── adr/
        └── decisions/
            └── GENI-ADR-020.md
```"""
        self.assertEqual(
            validator.parse_documentation_tree_paths(
                tree, "global-economic-news-intelligence"
            ),
            {"README.md", "docs/README.md", "docs/adr/decisions/GENI-ADR-020.md"},
        )

    def test_ascii_docs_tree_parser_preserves_nested_paths(self) -> None:
        tree = """```text
docs/
|-- README.md
+-- adr/
    |-- README.md
    +-- decisions/
        +-- GENI-ADR-020.md
```"""
        self.assertEqual(
            validator.parse_documentation_tree_paths(tree, "docs"),
            {"README.md", "adr/README.md", "adr/decisions/GENI-ADR-020.md"},
        )

    def test_published_readme_documentation_trees_match_repository(self) -> None:
        validator.validate_readme_documentation_trees()

    def test_root_readme_uses_adr_registry_as_single_inventory(self) -> None:
        validator.validate_root_readme_adr_authority()

    def test_privacy_specification_is_linked_and_complete(self) -> None:
        validator.validate_privacy_specification_contract()

    def test_privacy_architecture_is_aligned_across_documents(self) -> None:
        validator.validate_privacy_specification_contract()
        validator.validate_repository_inventory_alignment()

    def test_document_footer_metadata_matches_header(self) -> None:
        validator.validate_document_footer_metadata()

    def test_first_slice_review_activation_is_gated_consistently(self) -> None:
        validator.validate_review_activation_gates()

    def test_publication_decision_provenance_is_aligned_and_gated(self) -> None:
        validator.validate_publication_decision_provenance_contract()

    def test_first_slice_contract_document_is_registry_controlled(self) -> None:
        self.assertIn("docs/15-first-slice-implementation-contracts.md", validator.CONTROLLED_DOCUMENTS)
        validator.validate_document_versions()
        validator.validate_document_registry_metadata_alignment()

    def test_expected_adr_inventory_includes_adr_020(self) -> None:
        self.assertIn("GENI-ADR-020", validator.EXPECTED_ADR_IDS)
        self.assertEqual(len(validator.EXPECTED_ADR_IDS), 20)


if __name__ == "__main__":
    unittest.main()
