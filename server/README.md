# LMCP Server Seam

This folder is reserved for the optional local MCP adapter.

## V0 rule

Do not start with the server as the source of truth.

The source of truth is the customer pack folder:

```text
PACK_MANIFEST.yaml
skills/
indexes/
receipts/
```

The server should read generated indexes and selected manifests only.

## Recommended v0.1 MCP surface

Read-only tools:

```text
lmcp_list_skills
lmcp_search_skills
lmcp_get_record
lmcp_get_manifest
lmcp_get_pack_boundary
lmcp_build_context_packet
```

Resources:

```text
lmcp://pack/manifest
lmcp://index/registry
lmcp://index/tags
lmcp://skill/<skill-id>/manifest
```

## Blocked by default

Do not implement these in the first server version:

```text
lmcp_execute_skill
lmcp_install_skill
lmcp_delete_skill
lmcp_overwrite_skill
lmcp_trust_remote_pack
lmcp_run_any_command
```

## Transport

Prefer stdio for local agent hosts.

HTTP, hosted, or remote transports are later seams and must add authentication, host/origin controls, body limits, and explicit deployment receipts.

## Authority boundary

The MCP server exposes selected pack records. It does not make skills trusted, safe, correct, executable, or approved.
