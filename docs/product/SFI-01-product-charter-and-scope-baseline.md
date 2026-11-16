# SFI-01 — Product Charter and Scope Baseline

**Document status:** Baseline draft for product review  
**Work item:** [SFI-01 — Product Charter and Scope Baseline](https://linear.app/getpsi/issue/SFI-1/sfi-01-product-charter-and-scope-baseline)  
**Project:** Software Factory Intelligence (Team SFI)  
**Repository:** [mkrdiop/software-factory-intelligence](https://github.com/mkrdiop/software-factory-intelligence)

## 1. Purpose

Establish the product identity, mission, boundaries, users, outcomes, principles and initial scope of SFI. This is the product baseline for subsequent SFI architecture and implementation work.

## 2. Product thesis

SFI turns the evidence generated throughout software engineering into governed, traceable and reusable intelligence. Its primary strategic asset is a high-quality, versioned **Software Engineering Intelligence Dataset** derived from a provenance-aware **Engineering Evidence History**.

SFI is not merely an AI coding assistant, agent orchestrator, engineering dashboard or generic data lake.

## 3. Problem

Software engineering evidence is fragmented across requirements, discussions, architecture decisions, work trackers, source control, CI, tests, security tools, reviews, releases and incidents. The relationships between intent, decisions, implementation, validation and outcomes are often lost. Consequently, teams cannot reliably reconstruct why software was built a certain way, measure engineering quality end to end, reuse verified solutions, or create trustworthy datasets for evaluation and learning.

## 4. Product mission

Build an interoperable intelligence layer that captures, structures, evaluates and learns from software engineering evidence across the lifecycle, improving the quality, reliability, security and efficiency of production-grade software delivery.

## 5. Primary users and beneficiaries

- Software factory/platform teams that need lifecycle traceability and measurable delivery quality.
- Engineering leaders and architects who need evidence-based insight into decisions, quality and outcomes.
- Developers and AI coding agents whose work should be evaluated against explicit intent and verified evidence.
- QA, security and reliability teams that contribute validation and outcome evidence.
- Dataset/evaluation engineers who curate trustworthy corpora for benchmarking, analytics and model/workflow improvement.
- Enterprise Factory products and compatible third-party engineering systems as integration consumers/producers.

## 6. Product outcomes

1. Reconstruct traceable chains from business intent through decisions, work, code and validation to release/outcome.
2. Preserve a provenance-aware Engineering Evidence History with source, identity, timestamps, versions, ownership and permissions.
3. Produce curated, versioned Software Engineering Intelligence Datasets with explicit quality and usage metadata.
4. Evaluate engineering artifacts and delivery outcomes using reproducible evidence and declared criteria.
5. Discover reusable patterns, failure modes and engineering insights without erasing context or provenance.
6. Enable governed feedback loops that improve agents, workflows, evaluations and, where permitted, specialized models.

## 7. Product scope

### In scope

- Evidence ingestion and connector contracts for engineering systems (initially GitHub, Linear, Notion and AI-agent activity).
- Canonicalization, identity resolution, provenance, temporal/version history and relationship mapping.
- Engineering knowledge graph linking intent, reasoning/decisions, execution, validation, outcomes and learning.
- Evidence quality, completeness, consistency and traceability evaluation.
- Dataset curation, filtering, labeling, deduplication, versioning, lineage and release controls.
- Governance capabilities for ownership, consent/rights, tenant isolation, access control, retention and permitted uses.
- APIs and export/interoperability mechanisms for downstream factory tools, analytics and evaluation workflows.
- Learning and intelligence workflows that consume approved, curated datasets.

### Explicitly out of scope for the initial product baseline

- Replacing GitHub, Linear, Notion, CI/CD, issue trackers or source-of-truth engineering systems.
- Replacing Enterprise Factory Studio, Connect, Runtime or Enterprise Factory Network.
- Defining a competing Enterprise Factory Specification, canonical factory object model, publisher identity model or other ecosystem-wide standards.
- Building a general-purpose autonomous coding agent or IDE.
- Automatically using customer or tenant data to train shared models.
- Treating raw event capture as permission to train, benchmark, publish or cross-share data.
- Guaranteeing correctness solely from model-generated explanations or unverified agent claims.

These exclusions do not prevent later integrations or optional product capabilities; any scope expansion requires an explicit decision and compatibility review.

## 8. Six evidence domains

1. **Intent:** business requirements, user stories, constraints, specifications and acceptance criteria.
2. **Reasoning and decisions:** alternatives, architecture decisions, rationale, approvals and superseded decisions.
3. **Execution:** tasks, agent actions, code changes, commits, pull requests and workflow events.
4. **Validation:** tests, test results, reviews, security findings, conformance and quality measurements.
5. **Outcomes:** accepted releases, deployments, incidents, regressions, operational signals and maintenance.
6. **Learning:** verified patterns, failure analyses, corrections, reusable solutions and evaluation examples.

## 9. Two foundational data assets

- **Engineering Evidence History:** the provenance-aware historical record of observed engineering evidence and its evolution. It preserves source references, event/observation time, versions, actors, relationships, ownership and applicable permissions.
- **Software Engineering Intelligence Dataset:** a curated, versioned and purpose-governed collection derived from evidence history for evaluation, analytics, benchmarking and permitted model/workflow development.

The two assets are related but not interchangeable. Raw evidence is not training-ready by default. Dataset inclusion requires provenance, quality checks, rights/permission checks, tenant-boundary enforcement and declared intended use.

## 10. Product architecture domains

These are conceptual domains, not implementation commitments:

- Knowledge Graph
- Engineering Data Infrastructure
- Evaluation Engine
- Intelligence Engine
- Learning Engine

SFI-02 and SFI-03 will refine boundaries, responsibilities, interfaces and canonical data structures.

## 11. Product principles

1. Dataset-first engineering: every capability considers what evidence it produces and how that evidence may be governed and reused.
2. End-to-end traceability: connect intent to verified outcomes.
3. Evidence over assertions: distinguish observed facts, derived claims and model-generated hypotheses.
4. Provenance and reproducibility: preserve source, lineage, versions and evaluation context.
5. Governance by design: ownership, permissions, tenant isolation, retention and permitted uses are foundational.
6. Interoperability: use vendor-neutral contracts and avoid unnecessary platform lock-in.
7. Separation of concerns: preserve the boundary between immutable/append-only evidence history and curated dataset products.
8. Human accountability: consequential approvals, data-use decisions and policy exceptions remain attributable.
9. Shared-standard alignment: reuse Enterprise Factory authoritative standards; do not fork them.

## 12. Enterprise Factory relationship

SFI is an independently developed project with its own Team SFI Linear project, Notion project home and GitHub repository. It is a complementary intelligence/data layer that may serve and consume capabilities across Factory Studio, Factory Connect, Factory Runtime and Enterprise Factory Network.

Where a shared Enterprise Factory contract or standard exists, SFI must reference and implement that authority. SFI may define SFI-specific extensions only within its own namespace and without changing shared semantics. Changes to shared standards must be proposed and governed in their authoritative Enterprise Factory records.

## 13. Initial success measures

These measures are to be baselined, not assumed achieved:

- **Traceability coverage:** proportion of sampled delivery artifacts connected to an evidence chain from intent to validation/outcome.
- **Evidence completeness:** proportion of required provenance and governance fields populated for captured records.
- **Dataset quality:** measured validity, deduplication, label consistency, lineage completeness and rights/permission compliance.
- **Evaluation reproducibility:** ability to rerun a declared evaluation against a fixed dataset/version and reproduce its result.
- **Connector reliability:** ingestion success, latency, replayability and duplicate handling by source.
- **Operational usefulness:** demonstrated reduction in manual evidence reconstruction and increased reuse of verified patterns.

SFI-02 through SFI-05 should define metric formulas, baselines, target values and measurement procedures. No numerical targets are asserted by this charter.

## 14. Key risks and constraints

- Incomplete or inconsistent source data can create misleading intelligence.
- Tenant leakage or unclear rights can make otherwise useful datasets unusable.
- Connector/API changes can break ingestion and lineage.
- Over-normalization can erase source semantics; under-normalization can prevent cross-source analysis.
- Model-generated labels or summaries can introduce unsupported claims unless separated from verified evidence.
- Scope can expand into an overly broad engineering platform; the initial product must prioritize evidence integrity and dataset quality.

## 15. Initial delivery sequence

- **SFI-01:** Product Charter and Scope Baseline — this document.
- **SFI-02:** System Architecture and Enterprise Factory Integration Boundaries.
- **SFI-03:** Canonical Engineering Evidence and Dataset Model.
- **SFI-04:** Evidence Capture Strategy for GitHub, Linear, Notion and AI Agents.
- **SFI-05:** Dataset Curation, Provenance and Quality Framework.

This sequence is an initial planning baseline and may be refined through explicit Linear decisions.

## 16. SFI-01 acceptance criteria

- [ ] Product mission, thesis, problem and primary users are explicit.
- [ ] In-scope and out-of-scope boundaries are documented.
- [ ] Six evidence domains and the distinction between the two foundational data assets are defined.
- [ ] Product principles and governance constraints are explicit.
- [ ] Enterprise Factory integration and standards-governance boundaries are documented.
- [ ] Initial success measures are defined without inventing unsupported target values.
- [ ] Risks, constraints and next work items are recorded.
- [ ] The charter is saved in the SFI Notion knowledge hub and versioned in the SFI GitHub repository.
- [ ] A corresponding SFI-01 issue tracks review and acceptance in the SFI Linear project.

## 17. Decisions intentionally deferred

Detailed schemas and event semantics; graph technology; storage and retention architecture; connector implementation details; identity resolution mechanics; dataset packaging formats; evaluation algorithms; model choices; deployment topology; pricing and packaging. These belong in subsequent specifications and ADRs.

## 18. Status and change control

This is the baseline draft for product review. Scope changes after acceptance should be recorded as explicit decisions and reflected in the charter version history.