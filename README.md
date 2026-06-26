# LMCP — Local MCP Pack Template

LMCP is a **templated local MCP pack** for shipping curated, hashed, versioned AI-agent skills to a customer or operator.

It is designed for paid or private workflow bundles where a customer receives:

- a bounded local MCP shape
- a curated skill folder
- manifests for each skill
- hashes and version records
- generated indexes
- receipts
- a protected seam for optional MCP exposure

## Core doctrine

Disk truth first. Server second.

- The **pack folder** is the source of truth.
- Hashes prevent duplicate work.
- Manifests give machines stable binding spots.
- Indexes let agents select skills without loading the whole pack.
- MCP is an adapter over the pack, not the authority.
- Hosted copies are mirrors, not trusted runtime authority.

## What this is for

Use LMCP to package a bounded skill bundle such as:

- Curation Stack
- Proprietary Workflow Pack
- Repo Audit Pack
- SourceBoundary Pack
- Agent Boundary Pack
- Customer-specific workflow pack

The customer gets the MCP-ready folder and the skills in it. The pack remains bounded by its `PACK_MANIFEST.yaml`, claim boundary, hashes, and receipts.

## V0 canonical shape

```text
lmcp/
  README.md
  CLAIM_BOUNDARY.md
  docs/
    KSL.md
  template/
    PACK_MANIFEST.yaml
    README_CUSTOMER.md
    skills/
      example-skill/
        SKILL.md
        skill.manifest.yaml
    indexes/
      README.md
    receipts/
      README.md
  scripts/
    build_lmcp_index.py
  server/
    README.md
```

## Pack shape for customers

```text
<customer-pack>/
  PACK_MANIFEST.yaml
  README_CUSTOMER.md
  CLAIM_BOUNDARY.md
  skills/
    <skill-id>/
      SKILL.md
      skill.manifest.yaml
      examples/             # optional
      scripts/              # optional, disabled unless declared
      receipts/             # optional
  indexes/
    hash-ledger.jsonl
    binding-index.jsonl
    registry.jsonl
    tag-index.json
  receipts/
    PACK_RECEIPT.md
```

## First command

Build local indexes from the template pack:

```bash
python3 scripts/build_lmcp_index.py --pack template --out template/indexes
```

The script is local-only and standard-library-only. It hashes skill folders, extracts cheap binding markers, writes a registry, and does not execute skills.

## MCP boundary

The MCP server seam should be read-only first:

- list available skills
- search by tag / capability class
- get one registry record
- get one selected manifest
- return a dry-run equip or usage recommendation

It should not initially:

- execute skill scripts
- install packages
- mutate customer folders
- trust hosted content
- expose secrets
- grant authority

## Licensing note

This repository is a template scaffold. A sold customer pack should carry its own commercial license or terms. Do not accidentally mark proprietary skill contents as OSS unless that is intentional.
