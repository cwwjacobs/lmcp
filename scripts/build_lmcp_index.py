#!/usr/bin/env python3
"""
Build LMCP pack indexes.

Local-only, standard-library-only, read-only scanner.
It hashes skill folders and emits:
- hash-ledger.jsonl
- binding-index.jsonl
- registry.jsonl
- tag-index.json
- index-build receipt

It does not execute skill scripts, install packages, call the network, or mutate skill contents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TEXT_EXTS = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".ts", ".js", ".sh", ".toml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "indexes", "receipts"}

MARKER_RULES: list[tuple[str, list[str]]] = [
    ("repo-audit", ["repo", "repository", "audit"]),
    ("dependency-map", ["dependency", "import", "mermaid"]),
    ("claim-boundary", ["claim boundary", "bounded claim", "overclaim"]),
    ("prompt-injection", ["prompt injection", "untrusted", "authority"]),
    ("mcp", ["mcp", "model context protocol"]),
    ("workflow", ["workflow", "skillchain", "card/tool/blocked"]),
    ("context-handoff", ["context", "handoff", "compression"]),
    ("receipt", ["receipt", "hash", "sha256"]),
    ("read-only", ["read-only", "no network", "no shell"]),
    ("packaging", ["pack", "package", "manifest"]),
]

TYPE_RULES: list[tuple[str, list[str]]] = [
    ("audit.dependency_map", ["dependency-map"]),
    ("audit.claim_boundary", ["claim-boundary"]),
    ("boundary.prompt_injection", ["prompt-injection"]),
    ("tooling.mcp", ["mcp"]),
    ("workflow.skillchain", ["workflow"]),
    ("ops.context_handoff", ["context-handoff"]),
    ("packaging.skill_pack", ["packaging"]),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_skill_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            path = Path(root) / name
            if path.is_file():
                files.append(path)
    return sorted(files)


def sha256_tree(skill_dir: Path) -> str:
    h = hashlib.sha256()
    for path in iter_skill_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(sha256_file(path).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def read_text(path: Path, max_bytes: int = 200_000) -> str:
    try:
        raw = path.read_bytes()[:max_bytes]
        return raw.decode("utf-8", errors="replace")
    except OSError:
        return ""


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    m = pattern.search(block)
    if not m:
        return None
    return m.group(1).strip().strip('"\'')


def yamlish_value(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return None
    return m.group(1).strip().strip('"\'')


def collect_text_for_markers(skill_dir: Path) -> str:
    chunks: list[str] = []
    for path in iter_skill_files(skill_dir):
        if path.suffix.lower() in TEXT_EXTS:
            chunks.append(read_text(path, max_bytes=50_000))
    return "\n".join(chunks).lower()


def infer_markers(skill_dir: Path) -> tuple[list[str], list[str]]:
    markers: set[str] = set()
    tags: set[str] = set()

    if (skill_dir / "SKILL.md").exists():
        markers.add("has_skill_md")
    if (skill_dir / "README.md").exists():
        markers.add("has_readme")
    if (skill_dir / "LICENSE").exists() or (skill_dir / "LICENSE.md").exists():
        markers.add("has_license")
    if (skill_dir / "skill.manifest.yaml").exists() or (skill_dir / "skill.manifest.yml").exists():
        markers.add("has_manifest")
    if (skill_dir / "examples").exists():
        markers.add("has_examples")
    if (skill_dir / "scripts").exists():
        markers.add("has_scripts")

    text = collect_text_for_markers(skill_dir)
    for tag, needles in MARKER_RULES:
        if any(n in text for n in needles):
            tags.add(tag)
            markers.add(f"mentions_{tag.replace('-', '_')}")

    if re.search(r"\b(curl|wget|requests\.|fetch\(|http://|https://)\b", text):
        markers.add("authority_network_surface_candidate")
        tags.add("network-surface")
    if re.search(r"\b(rm\s+-rf|unlink\(|shutil\.rmtree|delete_file|os\.remove)\b", text):
        markers.add("authority_file_delete_surface_candidate")
        tags.add("file-delete-surface")
    if re.search(r"\b(os\.environ|process\.env|api[_-]?key|token|secret)\b", text):
        markers.add("authority_env_or_secret_surface_candidate")
        tags.add("env-token-surface")

    return sorted(markers), sorted(tags)


def infer_type(tags: list[str]) -> str:
    tag_set = set(tags)
    for type_hint, required_tags in TYPE_RULES:
        if all(t in tag_set for t in required_tags):
            return type_hint
    return "unknown.needs_review"


def parse_skill(skill_dir: Path, pack_root: Path) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    manifest = skill_dir / "skill.manifest.yaml"
    manifest_alt = skill_dir / "skill.manifest.yml"
    manifest_path = manifest if manifest.exists() else manifest_alt if manifest_alt.exists() else None

    skill_text = read_text(skill_md) if skill_md.exists() else ""
    manifest_text = read_text(manifest_path) if manifest_path else ""

    folder_id = skill_dir.name
    manifest_id = yamlish_value(manifest_text, "id") if manifest_text else None
    fm_name = frontmatter_value(skill_text, "name") if skill_text else None
    manifest_name = yamlish_value(manifest_text, "name") if manifest_text else None
    description = frontmatter_value(skill_text, "description") if skill_text else None

    markers, tags = infer_markers(skill_dir)
    content_hash = sha256_tree(skill_dir)
    rel_path = skill_dir.relative_to(pack_root).as_posix()
    stable_id = manifest_id or fm_name or folder_id
    type_hint = infer_type(tags)

    return {
        "record_type": "lmcp_skill_record",
        "id": stable_id,
        "name": manifest_name or fm_name or folder_id,
        "description": description or "",
        "path": rel_path,
        "content_hash": f"sha256:{content_hash}",
        "binding_markers": markers,
        "tags": tags,
        "type_hint": type_hint,
        "has_skill_md": skill_md.exists(),
        "has_manifest": manifest_path is not None,
        "manifest_path": manifest_path.relative_to(pack_root).as_posix() if manifest_path else None,
        "duplicate_of": None,
        "review_items": [],
    }


def find_skill_dirs(pack_root: Path) -> list[Path]:
    skills_root = pack_root / "skills"
    if not skills_root.exists():
        return []
    dirs = []
    for child in sorted(skills_root.iterdir()):
        if child.is_dir() and child.name not in SKIP_DIRS:
            if (child / "SKILL.md").exists() or (child / "skill.manifest.yaml").exists() or (child / "README.md").exists():
                dirs.append(child)
    return dirs


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")


def build_tag_index(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    idx: dict[str, set[str]] = {}
    for rec in records:
        for tag in rec.get("tags", []):
            idx.setdefault(tag, set()).add(rec["id"])
        for marker in rec.get("binding_markers", []):
            idx.setdefault(marker, set()).add(rec["id"])
    return {k: sorted(v) for k, v in sorted(idx.items())}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build LMCP pack indexes")
    parser.add_argument("--pack", required=True, help="Pack root containing skills/")
    parser.add_argument("--out", required=True, help="Output directory for indexes")
    args = parser.parse_args()

    pack_root = Path(args.pack).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    records = [parse_skill(d, pack_root) for d in find_skill_dirs(pack_root)]

    seen_hashes: dict[str, str] = {}
    for rec in records:
        h = rec["content_hash"]
        if h in seen_hashes:
            rec["duplicate_of"] = seen_hashes[h]
            rec["review_items"].append("duplicate_hash_instance")
        else:
            seen_hashes[h] = rec["id"]
        if not rec["has_manifest"]:
            rec["review_items"].append("missing_skill_manifest")
        if rec["type_hint"] == "unknown.needs_review":
            rec["review_items"].append("unknown_type_hint")

    hash_ledger = [
        {
            "id": rec["id"],
            "path": rec["path"],
            "content_hash": rec["content_hash"],
            "duplicate_of": rec["duplicate_of"],
        }
        for rec in records
    ]

    binding_index = [
        {
            "id": rec["id"],
            "path": rec["path"],
            "content_hash": rec["content_hash"],
            "binding_markers": rec["binding_markers"],
            "tags": rec["tags"],
            "type_hint": rec["type_hint"],
            "review_items": rec["review_items"],
        }
        for rec in records
    ]

    write_jsonl(out_dir / "hash-ledger.jsonl", hash_ledger)
    write_jsonl(out_dir / "binding-index.jsonl", binding_index)
    write_jsonl(out_dir / "registry.jsonl", records)

    tag_index = build_tag_index(records)
    (out_dir / "tag-index.json").write_text(json.dumps(tag_index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "record_type": "lmcp_index_build_receipt",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pack_root": str(pack_root),
        "out_dir": str(out_dir),
        "skill_count": len(records),
        "duplicate_instances": sum(1 for r in records if r["duplicate_of"]),
        "missing_manifests": sum(1 for r in records if not r["has_manifest"]),
        "unknown_type_hints": sum(1 for r in records if r["type_hint"] == "unknown.needs_review"),
        "claim_boundary": "Index build is a local read-only scan. It does not prove safety or authorize execution.",
    }
    receipts_dir = pack_root / "receipts"
    receipts_dir.mkdir(exist_ok=True)
    stamp = receipt["timestamp"].replace(":", "").replace("+", "Z")
    (receipts_dir / f"index-build-{stamp}.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
