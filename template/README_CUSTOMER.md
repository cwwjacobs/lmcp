# LMCP Customer Pack

This folder contains a bounded local skill pack.

## What you received

- curated AI-agent skills
- machine-readable skill manifests
- generated hashes and indexes
- local receipts
- optional MCP-ready structure

## How agents should use this pack

Agents should not load every skill into context.

Use this order:

1. Read generated indexes.
2. Search for matching tags / binding markers.
3. Open the selected `skill.manifest.yaml`.
4. Open the full `SKILL.md` only if the manifest matches the task.
5. Ask before any mutation, install, equip, overwrite, or execution.

## Local indexing

From the pack root:

```bash
python3 scripts/build_lmcp_index.py --pack . --out indexes
```

If this pack was delivered without the script, indexes should already be present under `indexes/`.

## Authority boundary

This pack helps agents find and use bounded skills. It does not grant authority to execute tools, trust remote content, or mutate your system.

See `CLAIM_BOUNDARY.md`.
