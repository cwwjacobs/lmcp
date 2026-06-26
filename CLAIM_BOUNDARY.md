# LMCP Claim Boundary

LMCP packages local skill bundles and exposes a protected seam for optional MCP access.

## LMCP may claim

- Provides a canonical folder shape for local skill packs.
- Supports hashed and versioned skill packaging.
- Provides machine-readable manifests for skill selection.
- Generates local indexes from pack contents.
- Creates binding records that help agents choose relevant skills without loading the entire pack.
- Provides a seam for a read-only MCP adapter.

## LMCP may not claim

- Proves skill correctness, safety, compliance, or production readiness.
- Guarantees prompt-injection resistance.
- Grants runtime authority to any agent or model.
- Makes hosted or remote skill content trusted.
- Executes, installs, mutates, deletes, or overwrites customer files by default.
- Replaces operator review or customer approval.

## Authority rule

The pack manifest, hashes, and generated indexes are **evidence and routing material**. They do not grant authority.

Execution, equip, install, overwrite, or network behavior must be separately declared, reviewed, and approved.

## Hosted mirror rule

Hosted packs or catalogs are distribution surfaces only. Local verified pack contents are the working authority.

## LLM runner rule

If an LLM is used for ambiguous classification, it is advisory-only. It may suggest labels or stacks; it may not approve, execute, mutate, trust, or grant authority.
