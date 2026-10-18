"""Keep Home Assistant manifest requirements in sync with UV dependencies."""

import json
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_requirements_are_in_uv_dev_dependencies() -> None:
    """Every integration requirement must match a declared UV dependency."""
    manifest_path = ROOT / "custom_components/fernsehserien/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    manifest_requirements = {
        canonicalize_name(requirement.name): requirement
        for requirement in map(Requirement, manifest.get("requirements", []))
    }
    uv_dependencies = {
        canonicalize_name(requirement.name): requirement
        for requirement in map(
            Requirement, project["dependency-groups"]["dev"]
        )
    }

    missing = set(manifest_requirements) - set(uv_dependencies)
    assert not missing, (
        "Manifest requirements missing from [dependency-groups].dev: "
        + ", ".join(sorted(missing))
    )

    for name, manifest_requirement in manifest_requirements.items():
        uv_requirement = uv_dependencies[name]
        assert manifest_requirement.specifier == uv_requirement.specifier, (
            f"Version mismatch for {name}: manifest requires "
            f"'{manifest_requirement}', but pyproject.toml declares "
            f"'{uv_requirement}'"
        )