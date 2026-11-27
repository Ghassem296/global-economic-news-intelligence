from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = ROOT / "src/global_economic_news_intelligence/domain"
DOMAIN_PACKAGE = "global_economic_news_intelligence.domain"


def test_domain_layer_imports_only_standard_library_or_domain_modules() -> None:
    violations: list[str] = []
    for path in DOMAIN_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue

            for module in modules:
                if not module:
                    continue
                root_module = module.split(".", maxsplit=1)[0]
                if (
                    root_module not in sys.stdlib_module_names
                    and not module.startswith(DOMAIN_PACKAGE)
                ):
                    violations.append(f"{path.relative_to(ROOT)} imports {module}")

    assert not violations, "\n".join(violations)
