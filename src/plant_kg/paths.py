"""Keep bundled inputs separate from writable analysis outputs."""

from pathlib import Path


def resource_root(package_dir: Path | None = None) -> Path:
    """Resolve resources in an installed wheel or a source checkout."""
    package_dir = package_dir or Path(__file__).resolve().parent
    bundled = package_dir / "resources"
    if (bundled / "config/sources.toml").is_file():
        return bundled
    checkout = package_dir.parents[1]
    if (checkout / "config/sources.toml").is_file():
        return checkout
    raise FileNotFoundError("Missing plant-kg resources; reinstall the package.")


RESOURCE_ROOT = resource_root()


def workspace_root() -> Path:
    """Use the checkout for editable installs, otherwise the working directory."""
    if (RESOURCE_ROOT / "pyproject.toml").is_file():
        return RESOURCE_ROOT
    return Path.cwd()
