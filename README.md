# Software Factory Intelligence (SFI)

Software Factory Intelligence (SFI) is an independent engineering project building the intelligence and data infrastructure that learns from software engineering evidence to improve production-grade software delivery.

## Project workspaces

- **Linear:** [Software Factory Intelligence — Team SFI](https://linear.app/getpsi/project/software-factory-intelligence-5bd62a7fb5db)
- **Notion:** [Software Factory Intelligence — Project Home](https://app.notion.com/p/41af741d6511818ea3a5f5af79beef13?pvs=204)
- **GitHub:** [mkrdiop/software-factory-intelligence](https://github.com/mkrdiop/software-factory-intelligence)

## Product baseline

- **SFI-01 — Product Charter and Scope Baseline:** [Notion document](https://app.notion.com/p/41af741d6511810bb463efce5c2bcfa0?pvs=204) · [Markdown source](docs/product/SFI-01-product-charter-and-scope-baseline.md) · [Linear issue](https://linear.app/getpsi/issue/SFI-1/sfi-01-product-charter-and-scope-baseline)

## Architecture baseline

- **SFI-02 — System Architecture and Enterprise Factory Integration Boundaries:** [Notion specification](https://app.notion.com/p/41af741d65118139829de891f58ff7b8?pvs=204) · [Markdown source](docs/architecture/SFI-02-system-architecture-and-enterprise-factory-integration-boundaries.md) · [Linear issue](https://linear.app/getpsi/issue/SFI-2/sfi-02-system-architecture-and-enterprise-factory-integration)

## Canonical data model

- **SFI-03 — Canonical Engineering Evidence and Dataset Model:** [Specification](docs/data-model/SFI-03-canonical-engineering-evidence-and-dataset-model.md) · [Draft 2020-12 schema](schemas/v1/sfi-03.schema.json) · [Conformance fixtures](fixtures/v1/) · [Validator](scripts/validate_sfi03.py) · [Linear issue](https://linear.app/getpsi/issue/SFI-3/sfi-03-canonical-engineering-evidence-and-dataset-model)

## Evidence ingestion contracts

- **SFI-04 — Evidence Capture, Ingestion and Normalization Contracts:** [Specification](docs/ingestion/SFI-04-evidence-capture-ingestion-and-normalization-contracts.md) · [Draft 2020-12 connector/delivery schema](schemas/v1/sfi-04.schema.json) · [Conformance fixtures](fixtures/v1/sfi04/) · [Validator](scripts/validate_sfi04.py) · [CI workflow](.github/workflows/sfi04-contracts.yml) · [Linear issue](https://linear.app/getpsi/issue/SFI-4/sfi-04-evidence-capture-ingestion-and-normalization-contracts)

## Mission

Build an intelligence layer that captures, structures, evaluates and learns from the complete software engineering lifecycle, helping software factories design, implement, validate, document and continuously improve enterprise software.

## Core objectives

1. Build a provenance-aware Software Engineering Evidence Dataset.
2. Transform raw engineering activity into curated, versioned datasets for analytics, evaluation and model development.
3. Develop the engineering knowledge graph, evaluation engine, intelligence engine and learning pipelines.
4. Integrate with GitHub, Linear, Notion and other engineering systems through interoperable connectors.
5. Support the Enterprise Factory ecosystem while preserving its authoritative shared standards.

## Initial evidence domains

- **Intent:** business requirements, user stories, constraints and acceptance criteria.
- **Reasoning and decisions:** architecture alternatives, ADRs, rationale and approvals.
- **Execution:** tasks, agent actions, code changes, commits and pull requests.
- **Validation:** tests, security findings, reviews and conformance results.
- **Outcomes:** accepted releases, incidents, regressions and maintenance.
- **Learning:** verified patterns, failures, corrections and reusable solutions.

## Foundational principles

- Dataset-first engineering.
- End-to-end traceability from intent to verified outcome.
- Evidence over assertions.
- Vendor-neutral interoperability.
- Data ownership, provenance, tenant isolation and governed learning.
- Separation of immutable engineering evidence from curated learning datasets.

## Relationship with Enterprise Factory

SFI has its own repository, Linear project and Notion project home. It is independently developable and deployable, while reusing compatible Enterprise Factory standards and contracts where appropriate. SFI must not create competing definitions for shared concepts such as EFS, the canonical object model or publisher identity.

## Initial architecture domains

- Knowledge Graph
- Engineering Data Infrastructure
- Evaluation Engine
- Intelligence Engine
- Learning Engine

See the [Notion project home](https://app.notion.com/p/41af741d6511818ea3a5f5af79beef13?pvs=204) for the project knowledge hub. Track implementation work in the [SFI Linear project](https://linear.app/getpsi/project/software-factory-intelligence-5bd62a7fb5db).
