# LMCP KSL Plan

## Ultra Goal

Create a templated local MCP pack shape that lets an operator package curated, hashed, versioned AI-agent skills for customers or internal workflows without making a server, dashboard, or hosted source the authority.

## Kernel

LMCP packages skill bundles as disk truth first:

- skills live in folders
- every skill has a manifest
- pack and skill contents are hashed
- generated indexes expose cheap binding records
- MCP, if used, reads the pack and returns small selected slices
- mutation and execution are not default behavior

## Boundary

### In scope

- canonical folder template
- customer pack manifest
- skill manifest template
- hash ledger
- binding index
- registry index
- tag index
- claim boundary
- receipts
- protected server seam
- local-first read-only MCP adapter later

### Out of scope for V0

- hosted runtime
- remote execution
- automatic equip/apply
- arbitrary command runner
- security/compliance guarantees
- dashboard as source of truth
- LLM runner as authority

## Operational Reality

The operator has many skills across local agents, repos, zip packs, and generated artifacts. The pain is not only skill creation; it is remembering what exists and giving each fresh agent a cheap way to bind the right skill without loading the whole library.

LMCP solves the packaging side:

```text
curated skills
  -> customer pack folder
  -> hashes + manifests
  -> generated indexes
  -> optional local MCP adapter
  -> small selected records in model context
```

## Spine

### Stage 1 — Map and lock shape

Done when:

- root README names the purpose
- claim boundary is explicit
- pack manifest template exists
- skill manifest template exists
- canonical folder layout exists

Receipts:

- README.md
- CLAIM_BOUNDARY.md
- template/PACK_MANIFEST.yaml
- template/skills/example-skill/skill.manifest.yaml

### Stage 2 — Walk implementation

Done when:

- a local script can scan a pack
- skill folder hashes are generated
- cheap binding markers are extracted
- registry and tag index are emitted
- script does not execute skill content

Receipts:

- scripts/build_lmcp_index.py
- template/indexes/hash-ledger.jsonl
- template/indexes/binding-index.jsonl
- template/indexes/registry.jsonl
- template/indexes/tag-index.json

### Stage 3 — Verify pack boundary

Done when:

- generated indexes match pack contents
- duplicate hashes are visible
- missing manifests are review items
- unknown tags are review items
- no network or shell execution exists in the index builder

Receipts:

- PACK_RECEIPT.md
- generated review notes
- smoke-test output when added

## Protected Seams

### Skill content seam

Customers receive skills in `skills/<skill-id>/`. Skill content may be proprietary. The template must not imply those contents are open-source unless the customer pack explicitly says so.

### Manifest seam

`skill.manifest.yaml` is the machine contract. Agents should read manifests before full `SKILL.md` bodies.

### Index seam

Indexes are generated from pack contents. Agents may route from indexes, but indexes do not grant execution authority.

### MCP seam

The MCP adapter is read-only first. It reads generated indexes and selected manifests. Mutation tools are later-only and require explicit approval and receipts.

### Hosted seam

Hosted packs are mirrors or distribution sources. Local verified pack contents are the working authority.

## V0 Success Condition

A fresh CLI agent can inspect a customer LMCP folder and answer:

- What skills are packaged?
- What hashes identify them?
- What tags and binding markers exist?
- Which skill looks relevant to this task?
- Which manifest should be opened?
- What should remain operator-approved?

without asking the operator to remember the whole skill library.

## Completion rule

LMCP completes the loop when a customer pack can be copied, indexed, searched, and exposed through a read-only seam while keeping authority local, bounded, and receipt-backed.
