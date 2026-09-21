"""Read-only catalog for the vendored Everything Claude Code assets.

ECC assets are Markdown instructions. They are indexed for discovery and can
be injected into an agent task explicitly; they are never imported as Python
or executed as commands by this module.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent / "ecc"
_KINDS = ("agents", "skills", "commands")


@dataclass(frozen=True)
class EccAsset:
    kind: str
    name: str
    path: str
    title: str
    description: str
    content: str

    def as_dict(self, include_content: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {
            "kind": self.kind,
            "name": self.name,
            "path": self.path,
            "title": self.title,
            "description": self.description,
        }
        if include_content:
            result["content"] = self.content
        return result


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip().lower()] = value.strip().strip("'\"")
    return metadata, text[end + 4:].lstrip("\n")


def _title_and_description(name: str, content: str, metadata: dict[str, str]) -> tuple[str, str]:
    heading = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
    title = metadata.get("name") or (heading.group(1).strip() if heading else name.replace("-", " ").title())
    description = metadata.get("description", "")
    if not description:
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                description = line[:240]
                break
    return title, description


@lru_cache(maxsize=1)
def _load_assets() -> tuple[EccAsset, ...]:
    assets: list[EccAsset] = []
    if not ROOT.exists():
        return ()
    for kind in _KINDS:
        directory = ROOT / kind
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            raw = path.read_text(encoding="utf-8")
            metadata, content = _parse_front_matter(raw)
            relative = path.relative_to(ROOT).as_posix()
            name = path.stem
            title, description = _title_and_description(name, content, metadata)
            assets.append(EccAsset(kind, name, relative, title, description, content))
    return tuple(assets)


def assets(kind: str = "") -> list[EccAsset]:
    """Return imported assets, optionally restricted to agents/skills/commands."""
    normalized = kind.strip().lower()
    if normalized and normalized not in _KINDS:
        return []
    return [asset for asset in _load_assets() if not normalized or asset.kind == normalized]


def search(query: str, kind: str = "", limit: int = 20) -> list[dict[str, Any]]:
    """Find assets by name, title, description, or body text."""
    terms = [term for term in query.lower().split() if term]
    matches = []
    for asset in assets(kind):
        haystack = f"{asset.name} {asset.title} {asset.description} {asset.content}".lower()
        if not terms or all(term in haystack for term in terms):
            matches.append(asset.as_dict())
        if len(matches) >= max(1, min(limit, 100)):
            break
    return matches


def get_asset(name: str, kind: str = "") -> EccAsset | None:
    """Get one asset by its relative path, name, or title."""
    needle = name.strip().lower()
    for asset in assets(kind):
        if needle in {asset.path.lower(), asset.name.lower(), asset.title.lower()}:
            return asset
    return None


def summary() -> dict[str, int]:
    return {kind: len(assets(kind)) for kind in _KINDS}


async def tool_ecc_catalog(kind: str = "") -> str:
    """List the imported ECC catalog and counts."""
    selected = assets(kind)
    counts = summary()
    lines = [f"ECC catalog: {counts['agents']} agents, {counts['skills']} skills, {counts['commands']} commands"]
    for asset in selected:
        lines.append(f"- [{asset.kind}] {asset.name}: {asset.title}")
    return "\n".join(lines)


async def tool_ecc_search(query: str = "", kind: str = "", limit: int = 20) -> str:
    results = search(query, kind, limit)
    if not results:
        return "No ECC assets matched that query."
    lines = [f"ECC matches ({len(results)}):"]
    lines.extend(f"- [{item['kind']}] {item['path']}: {item['title']} - {item['description']}" for item in results)
    return "\n".join(lines)


async def tool_ecc_get(name: str, kind: str = "") -> str:
    asset = get_asset(name, kind)
    if not asset:
        return f"ECC asset '{name}' was not found."
    return f"# ECC {asset.kind}: {asset.title}\nPath: {asset.path}\n\n{asset.content}"