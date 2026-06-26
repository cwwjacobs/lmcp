---
name: example-skill
description: Minimal example skill used to demonstrate LMCP packaging, manifests, hashes, and generated indexes.
status: example
---

# Example Skill

## Purpose

Demonstrate the minimum shape of a skill packaged inside an LMCP customer pack.

## Inputs

- task description
- selected context packet

## Outputs

- bounded recommendation
- receipt note

## Procedure

1. Read the task.
2. Confirm this skill is relevant.
3. Produce a bounded answer.
4. Do not execute tools or mutate files.

## Claim boundary

This example is packaging scaffolding only. It does not prove MCP compatibility, safety, correctness, or production readiness.
