# SFI-03 — Canonical Engineering Evidence and Dataset Model

**Document status:** Normative proposal for review; not approved  
**Work item:** SFI-03 — Canonical Engineering Evidence and Dataset Model  
**Project:** Software Factory Intelligence (Team SFI)  
**Predecessors:** SFI-01 Product Charter; SFI-02 System Architecture and Enterprise Factory Integration Boundaries  
**Specification family:** SFI Data Model v1  
**Schema dialect:** JSON Schema Draft 2020-12  
**Repository:** mkrdiop/software-factory-intelligence

## 1. Purpose and decision scope

SFI-03 defines the canonical data model that allows SFI to ingest, preserve, connect, evaluate and curate software-engineering evidence without making any source system or derived intelligence product the authority for another.

It establishes five interoperable record families:

1. **Engineering Evidence Record** — a normalized, provenance-bearing observation or snapshot of engineering evidence.
2. **Evidence Relationship** — an explicit, attributable assertion connecting evidence records or evidence to an identified external object.
3. **Evaluation Result** — a reproducible assessment of a fixed evidence input set under a versioned evaluator profile.
4. **Dataset Definition** — a governed, versioned specification for selecting and transforming evidence.
5. **Dataset Release** — an immutable, content-addressed output of a particular dataset definition and build.

The model is intentionally separate from source-system schemas, the knowledge-graph storage model, EFS Factory Manifest semantics, and any model-training format. Adapters map source records into this model; downstream systems may project it into graph, analytics, search or training-specific representations.

### 1.1 Normative language

**MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are normative. Each requirement identifier is stable within SFI-03. A schema-valid record is structurally conformant only; it is not thereby truthful, authorized, complete, safe, fit for a dataset, or approved for model training.

### 1.2 Normative vs informative material

Sections 2–13 define normative semantics and acceptance obligations. Examples and fixture descriptions are informative unless explicitly labelled as a conformance requirement. JSON Schemas in `schemas/v1/sfi-03.schema.json` provide structural validation for the five record families; semantic and policy rules remain separate validator stages.

## 2. Canonical modeling principles

- **Source authority:** source systems remain authoritative for their own records. SFI stores attributable observations, snapshots and references.
- **Evidence is not truth:** source-observed, normalized, inferred, model-generated and human-verified claims remain distinguishable.
- **Append-only history:** accepted evidence observations and relationship assertions are not silently overwritten. Corrections, retractions and supersession are new records or explicit lifecycle events.
- **Separate identity domains:** tenant, workspace, source instance, source object, evidence record, actor/principal, publisher, Factory and execution identities MUST NOT be conflated.
- **Temporal clarity:** event time, observation time, ingestion time and effective time are distinct.
- **Explicit lineage:** every derived relationship, evaluation and dataset release MUST identify its inputs and the transformation/evaluator version that produced it.
- **Governance propagation:** rights, purpose restrictions, classification and retention constraints MUST be carried forward or conservatively tightened by derived artifacts.
- **No implicit training permission:** evidence capture or dataset release MUST NOT imply permission for model training or cross-tenant reuse.
- **Interoperability without false equivalence:** source-specific identifiers and semantics are retained; canonical predicates do not erase the original source type.
- **Reproducibility:** an evaluation or dataset build MUST be bound to immutable input snapshots, versioned configuration and content digests.

## 3. Namespace, identifiers and versioning

### 3.1 Schema identifiers

The initial schema bundle uses the provisional, non-dereferencing identifier family `urn:sfi:schema:v1:<record-family>`. These identifiers are stable within this proposal and MUST be treated as opaque schema identifiers. A future schema-registry ADR may introduce resolvable HTTPS distribution URLs without changing the record semantics. No client may dereference a schema identifier merely because it is a URI.

The schema bundle declares JSON Schema Draft 2020-12. Schema version, record schema version, source object version, dataset definition version and dataset release version are separate version dimensions.

### 3.2 Record identifiers

- `evidenceId`, `relationshipId`, `evaluationId` and `releaseId` MUST be globally unique within the SFI deployment and immutable.
- The initial profile uses UUID strings for these identifiers. UUIDs are identifiers, not authorization tokens.
- `tenantId` and `workspaceId` are SFI-scoped identifiers. A workspace belongs to exactly one tenant.
- Source identity is the tuple `(source.system, source.instanceId, source.objectType, source.objectId)`; object version/event identity is additional revision context, not a substitute for that tuple.
- A source URL is a locator for human navigation, not a primary key or proof of authorization.
- IDs MUST NOT embed credentials, secrets, personal data or tenant names.

### 3.3 EFS boundary

SFI MUST NOT reuse `publisher.id`, `factory.id`, Factory Release identifiers or Execution Identity as evidence identifiers, tenant identifiers or source identities. If an evidence record references an Enterprise Factory object, it MUST retain the exact EFS identity values as an external reference and MUST defer EFS syntax, comparison and conformance to the authoritative EFS implementation.

In particular, `publisher.id` remains the exact opaque absolute URI governed by EFS (including its local-only validation/comparison profile). SFI MUST NOT dereference it, normalize it independently, resolve DNS, follow redirects or perform key discovery as part of evidence identity processing.

## 4. Engineering Evidence Record

### 4.1 Semantics

An Engineering Evidence Record is an immutable SFI record representing one observed source event, source-object snapshot, or explicitly declared SFI-derived assertion. It is not necessarily a complete source object and MUST declare its capture/representation mode.

The record is divided into:
- canonical SFI envelope and provenance;
- source identity and source-version context;
- temporal facts;
- payload/content reference and digest;
- normalized content;
- governance metadata;
- optional lineage to earlier evidence.

### 4.2 Required fields

| Field | Requirement | Semantics |
| --- | --- | --- |
| `schemaVersion` | MUST | Version of this record contract, initially `1.0.0`. |
| `recordType` | MUST | Constant `engineering-evidence`. |
| `evidenceId` | MUST | Immutable UUID. |
| `tenantId`, `workspaceId` | MUST | SFI ownership and isolation boundary. |
| `evidenceDomain` | MUST | One of intent, reasoning, execution, validation, outcome, learning. |
| `evidenceType` | MUST | Stable type name within the domain; source-specific original type is retained separately. |
| `captureMode` | MUST | `event`, `snapshot`, `document`, `trace-summary` or `derived-assertion`. |
| `source` | MUST | System, instance, object type, object ID and source version/event context. |
| `temporal` | MUST | `observedAt` and `ingestedAt`; source event time and effective time are optional. |
| `provenance` | MUST | Origin, trust category, connector/mapping versions and actor/producer. |
| `payload` | MUST | Media type and digest; protected archive reference or inline normalized content reference. |
| `content` | MUST | Canonical normalized JSON object; source-specific fields may be preserved under a namespaced extension. |
| `governance` | MUST | Classification, ownership, permitted purposes, rights basis and retention policy. |
| `idempotencyKey` | MUST | Stable connector-scoped key for duplicate delivery detection. |

### 4.3 Source and payload rules

The source object MUST preserve the source system's stable namespace, source instance identity, object type and object identifier. The connector MUST NOT replace source identity with an SFI-generated ID. Source version SHOULD be captured where available. If the source offers no revision identifier, the connector MUST state that it is unavailable rather than fabricate one.

The payload digest MUST be computed over the exact captured payload bytes using the declared algorithm. The archive reference MUST identify a protected SFI-managed object or immutable source artifact. A digest verifies byte integrity only; it does not prove authenticity, correctness, ownership or permission.

The normalized `content` object MUST be reproducible from the captured payload and declared mapping version where the source payload is retained. If normalization involves lossy extraction, redaction or summarization, the transformation MUST be recorded in provenance/lineage and the raw archive retention policy applied.

Secrets, access tokens, private keys and credentials MUST NOT be stored in `content`, payload metadata, source URLs or free-text provenance. Secret detection/redaction MUST occur before broad indexing or dataset export.

### 4.4 Provenance and trust

`provenance.origin` distinguishes:
- `source-observed`: captured directly from an identified source;
- `source-derived`: computed by the source system and observed by SFI;
- `sfi-normalized`: mapped or transformed by a declared SFI connector/normalizer;
- `sfi-derived`: generated by an SFI deterministic process;
- `model-generated`: generated by an AI/model process;
- `human-authored`: entered by an identified human actor outside a source-system capture.

`provenance.trust` is an independent epistemic classification:
- `unverified`;
- `source-authenticated`;
- `human-reviewed`;
- `independently-verified`;
- `disputed`.

Origin MUST NOT be treated as a trust score. A source-authenticated record can still be wrong; a model-generated hypothesis can later be independently verified. Trust changes MUST be represented by a new review/verification evidence record or explicit auditable state event, not by rewriting the original observation.

### 4.5 Temporal semantics

- `occurredAt`: when the source event is said to have occurred.
- `observedAt`: when the connector or actor observed the source evidence.
- `ingestedAt`: when SFI durably accepted the evidence.
- `effectiveAt`: when the fact is asserted to apply in the modeled domain.
- `sourceUpdatedAt`: source-reported update time, when available.

All timestamps MUST be RFC 3339 date-time values with an explicit UTC offset. SFI MUST NOT infer `occurredAt` from `ingestedAt`. Late-arriving and out-of-order evidence MUST be preserved; ordering and current-state projections are derived views.

### 4.6 Corrections, revisions and deletion

A new source revision MUST create a new evidence observation. The newer record MAY identify `supersedesEvidenceIds`. Supersession means a later record replaces an earlier record for a defined source-object interpretation; it does not erase the earlier observation.

Retraction MUST be an explicit, attributable lifecycle event referencing the affected evidence ID and reason category. Legal deletion or erasure requirements may require removal of payload bytes and derived copies; the append-only principle does not override applicable law or contractual obligations. Where retention of a tombstone is lawful, it SHOULD retain only the minimum non-content metadata needed to prevent accidental re-ingestion and explain the deletion.

## 5. Evidence Relationship

### 5.1 Semantics

An Evidence Relationship is a first-class, independently attributable assertion connecting a subject to a target. The target may be another SFI evidence record or a source/external object. Relationships are not silently inferred from graph proximity.

### 5.2 Canonical predicates

The initial controlled predicate vocabulary is:
`supports`, `implements`, `validates`, `contradicts`, `supersedes`, `derived-from`, `references`, `blocks`, `caused-by`, `belongs-to`, `produced-by`, `reviewed-by`.

The vocabulary is intentionally small. Unknown source relations MUST be retained in source metadata and mapped to a canonical predicate only when the mapping is justified. Extensions MUST use a namespaced predicate and MUST NOT redefine a core predicate.

### 5.3 Assertion status and evidence basis

Status is one of `candidate`, `asserted`, `verified`, `rejected` or `superseded`. A candidate is a possible match; asserted means an identified producer has made the claim; verified means a declared verification process or authorized reviewer confirmed it; rejected means the assertion was explicitly rejected. A model-produced relationship MUST NOT be marked verified solely because a model produced it.

Every relationship MUST identify:
- subject and target;
- predicate;
- status;
- assertion method (`source-native`, `deterministic-rule`, `human`, `model`);
- asserted time and asserting actor/process;
- evidence basis (one or more evidence IDs or an explicit external source reference);
- confidence when estimated, with its interpretation documented by the producing method.

Confidence is not truth probability unless the method explicitly calibrates it. A missing confidence is preferable to a fabricated numeric value. Verification/rejection and supersession history MUST be auditable.

## 6. Evaluation Result

An Evaluation Result records the outcome of applying a named, versioned evaluator profile to a fixed input snapshot.

Required properties include:
- immutable evaluation ID and schema version;
- tenant/workspace;
- evaluator ID, evaluator version and profile version;
- evaluation start/completion timestamps and terminal status;
- explicit input evidence IDs and, where used, relationship IDs;
- input snapshot digest and configuration digest;
- criteria-level outcomes with stable criterion IDs, result state, measured values and evidence references;
- summary outcome and reproducibility metadata.

Evaluator status is `completed`, `failed`, `cancelled` or `incomplete`. Criterion outcome is `pass`, `fail`, `warning`, `not-applicable` or `indeterminate`. An overall score MUST NOT conceal criterion-level failures or indeterminate results.

The record MUST distinguish structural validation, semantic validation, policy evaluation, trust verification and runtime execution outcomes. An evaluation MUST NOT imply that an artifact is safe, compliant or fit for production unless the evaluator profile explicitly defines that claim and its evidence basis.

Reproducibility metadata MUST identify evaluator artifact/version, configuration digest, input snapshot digest, execution environment/profile and deterministic flag. If the evaluator is stochastic, its seed and model/version metadata SHOULD be recorded when available. Private model chain-of-thought MUST NOT be captured; only authorized input/output summaries, tool events, declared rationale artifacts and evaluation evidence may be retained.

## 7. Dataset Definition

A Dataset Definition is a mutable, versioned specification of how a dataset is selected, transformed, labeled, quality-checked and governed. It is not the dataset itself and does not freeze membership.

It MUST identify:
- dataset ID and definition version;
- name and purpose/description;
- selection rules (tenant/workspace scope, evidence domains/types, time window, explicit include/exclude criteria);
- transformation pipeline and immutable version identifiers;
- label schema/version, where applicable;
- target use(s), including analytics, evaluation, benchmarking, retrieval, or model development/training;
- quality gates and minimum required evidence/provenance;
- governance policy: permitted purposes, sharing scope, retention and approval requirements.

A definition MUST NOT broaden the rights of its input evidence. A definition that selects evidence from multiple tenants MUST be rejected unless an explicit lawful/contractual sharing grant covers each included item and the cross-tenant operation is authorized.

Dataset definitions are versioned. A change to selection, transformation, labeling, quality gates or permitted purpose MUST create a new definition version. Existing releases remain bound to the exact definition version used to build them.

## 8. Dataset Release

A Dataset Release is an immutable, reproducible artifact generated from one Dataset Definition version and a fixed evidence snapshot.

It MUST include:
- immutable release ID and dataset ID;
- exact definition version and builder version;
- creation timestamp and terminal build status;
- item count and stable item manifest;
- evidence and relationship input snapshot references/digests;
- transformation and labeling lineage;
- evaluation/quality-gate results;
- content digest and digest algorithm/profile;
- rights/governance summary and approval record where required.

The release manifest MUST identify every included evidence item or an immutable partition/index whose contents are themselves digest-bound. It MUST NOT rely solely on a mutable query to reconstruct membership. Dataset release artifacts MUST NOT contain raw source payloads by default; payload inclusion requires explicit policy and rights checks.

Release status is `building`, `validated`, `approved`, `published`, `withdrawn` or `failed`. A published release is immutable. Corrections produce a new release; withdrawal blocks future distribution/use according to policy but does not silently mutate the historical manifest. A release digest proves integrity of the defined release payload, not the legality or quality of its contents.

## 9. Governance, rights and permitted use

### 9.1 Mandatory governance envelope

Every evidence record and dataset release MUST carry:
- tenant ownership and workspace scope;
- data classification;
- rights basis or explicit unknown/restricted status;
- permitted-purpose list;
- sharing scope;
- retention policy reference and applicable expiry;
- restriction/consent reference where required.

Permitted purposes are drawn from a controlled vocabulary: `engineering-operations`, `analytics`, `evaluation`, `benchmarking`, `retrieval`, `model-development`, `model-training`, `product-improvement`, `security-investigation`. A tenant policy may further restrict this vocabulary. `model-training` MUST NOT be inferred from `model-development`, `analytics` or generic consent.

### 9.2 Conservative inheritance

A derived relationship, evaluation or dataset item MUST inherit the most restrictive applicable classification, sharing and purpose restrictions of its inputs unless an authorized policy decision explicitly permits a narrower exception. If rights are unknown, the item is not eligible for cross-tenant sharing, public benchmarking or model training.

A dataset release is eligible for a target use only if every included item and every transformation step is permitted for that use. The builder MUST produce an auditable eligibility report and exclude or quarantine items that fail the policy gate.

### 9.3 Retention and deletion propagation

Retention expiry, erasure, withdrawal and legal hold MUST propagate to raw payloads, normalized records, graph projections, search indexes, evaluation artifacts, dataset builds and exported copies under SFI control. SFI MUST maintain a deletion/withdrawal ledger sufficient to prevent re-ingestion or accidental reuse where lawful. Immutable release storage does not override erasure obligations; the system may need to revoke access, rebuild a release without affected data, or destroy the affected artifact.

## 10. Idempotency, ordering and consistency

- Connector delivery is at-least-once; durable effects MUST be idempotent.
- Idempotency scope MUST include tenant, source instance, connector identity and connector-defined event/object revision key.
- Repeated delivery of the same source event MUST not create duplicate logical observations.
- A changed source version MUST create a distinct observation, even if the source object ID is unchanged.
- Missing source revisions require a connector-specific stable content/event fingerprint; the connector MUST document collision limitations.
- SFI MUST preserve original event/observation/ingestion timestamps and MUST tolerate late/out-of-order arrival.
- Graph projections, search indexes and analytics tables are rebuildable derived views; they MUST retain the evidence IDs and source snapshot from which they were derived.

## 11. Schema and semantic conformance

### 11.1 Structural validation

The initial JSON Schema bundle defines a discriminated union for all five record families using Draft 2020-12. It validates required fields, primitive types, controlled enumerations, timestamp formats, UUID syntax, numeric ranges and record discriminators.

### 11.2 Semantic validation

A semantic validator MUST additionally check:
1. tenant/workspace ownership consistency and authorization;
2. referenced evidence/relationship existence and tenant compatibility;
3. idempotency-key uniqueness within its defined scope;
4. temporal ordering sanity without rewriting source timestamps;
5. source revision and supersession consistency;
6. relationship endpoint and evidence-basis resolution;
7. confidence presence/range and method-specific rules;
8. evaluation input snapshot digest consistency;
9. dataset definition version and build lineage resolution;
10. dataset release membership/count/digest consistency;
11. rights/purpose inheritance and target-use eligibility;
12. retention, legal hold, withdrawal and deletion propagation;
13. secret/PII handling and permitted export controls;
14. EFS identity references delegated to authoritative EFS validation.

Schema validation MUST be a distinct result from semantic validation and policy authorization.

### 11.3 Fixture taxonomy

The initial conformance corpus SHOULD include:
- **valid-minimal:** smallest valid example of each record family;
- **valid-full:** populated example with optional metadata and lineage;
- **invalid-structure:** missing required property, wrong type, invalid enum, malformed timestamp/UUID, invalid confidence;
- **invalid-semantics:** cross-tenant reference, missing relationship endpoint, impossible supersession, digest mismatch, unauthorized purpose;
- **governance:** unknown rights, restricted purpose, retention expiry, legal hold, deletion propagation;
- **temporal:** late arrival, source clock skew, out-of-order revisions;
- **provenance:** source-observed, source-derived, model-generated, human-verified;
- **interoperability:** GitHub/Linear/Notion/CI/agent mapping and EFS external references;
- **replay/idempotency:** duplicate delivery, changed source revision and replay after connector restart.

Fixtures MUST be deterministic, synthetic and free of real secrets or personal data. Every negative fixture MUST state the expected validator stage and stable error code.

## 12. Security and privacy constraints

- Tenant isolation MUST be enforced before query, graph traversal, evaluation, dataset build and export.
- Source credentials MUST be held in a secrets manager or equivalent protected facility; schemas carry references only.
- Content MUST be treated as untrusted data, including instructions embedded in issue descriptions, documents, code, logs or model-generated summaries.
- Dataset export MUST apply authorization, redaction, rights and retention checks at build time and again at distribution time.
- Access to raw payloads MUST be more restrictive than access to sanitized metadata where appropriate.
- Audit records MUST capture actor, action, target, policy decision and timestamp without unnecessarily duplicating sensitive content.
- Agent evidence capture MUST be configured and disclosed; hidden model reasoning/private chain-of-thought is out of scope.

## 13. Compatibility and evolution

- The initial contract version is `1.0.0` for the SFI-03 proposal; schema version and record version MUST be explicit.
- Additive optional fields MAY be introduced in a compatible minor revision when existing validators can safely ignore them under the declared profile.
- Changes to required fields, enum meaning, identity semantics, timestamp semantics, governance obligations or digest coverage are breaking and require a new major contract version or explicit migration profile.
- Unknown fields MUST be preserved by ingestion where safe and MUST NOT be interpreted as trusted SFI core semantics.
- Core fields MUST NOT be repurposed by extensions.
- Schema changes require updated examples, fixtures, semantic validator rules, compatibility notes and migration guidance in the same change set.

## 14. Initial schema bundle and implementation layout

The first implementation baseline is:

- `schemas/v1/sfi-03.schema.json` — Draft 2020-12 union schema and shared definitions.
- `fixtures/v1/valid/evidence-source-observed.json`
- `fixtures/v1/valid/evidence-model-generated.json`
- `fixtures/v1/valid/relationship-asserted.json`
- `fixtures/v1/valid/evaluation-completed.json`
- `fixtures/v1/valid/dataset-definition.json`
- `fixtures/v1/valid/dataset-release.json`
- `fixtures/v1/invalid/evidence-missing-provenance.json`
- `fixtures/v1/invalid/relationship-invalid-confidence.json`

The union schema is a structural baseline, not the complete conformance implementation. Semantic validator and governance-policy tests are follow-on implementation work and MUST be tracked separately.

## 15. Acceptance criteria

SFI-03 is ready for review when:

- [ ] Five canonical record families and their boundaries are defined.
- [ ] Evidence identity, source identity, tenant/workspace scope and EFS boundary are explicit.
- [ ] Provenance, trust and temporal semantics are independent and unambiguous.
- [ ] Evidence corrections, supersession, retraction and deletion are defined.
- [ ] Relationship predicates, status, basis and assertion method are specified.
- [ ] Evaluation inputs, criteria, results and reproducibility metadata are defined.
- [ ] Dataset definition and immutable dataset release are separate models.
- [ ] Governance, permitted purposes, rights inheritance and deletion propagation are specified.
- [ ] Draft 2020-12 schema bundle validates all five record families.
- [ ] Positive and negative fixtures exercise the initial schema.
- [ ] Semantic validation requirements and fixture taxonomy are actionable.
- [ ] EFS shared identity/manifest/release semantics are not redefined.
- [ ] Notion, GitHub and Linear references are cross-linked and verified.

## 16. Decisions deliberately deferred

The following are not silently decided by SFI-03:
- physical storage format and immutable archive technology;
- event transport, queueing and delivery protocol;
- canonical JSON/digest profile for SFI evidence and dataset releases;
- graph database and relationship-resolution algorithm;
- universal connector protocol and source-specific mapping governance;
- exact PII taxonomy, jurisdictional retention schedules and legal-basis catalog;
- dataset artifact packaging format and registry implementation;
- semantic version compatibility policy beyond the initial schema-evolution rules;
- model-evaluation framework, benchmark scoring and calibrated confidence;
- EFS event envelope or runtime state-machine semantics.

These require focused ADRs or follow-on specifications. EFS-owned concepts remain governed by the Enterprise Factory standards and their own change process.

## 17. Follow-on engineering work

1. **SFI-04 — Evidence Ingestion, Provenance and Normalization Contracts:** connector envelope, idempotency, mapping manifests, raw archive references and replay.
2. **SFI-05 — Evidence Graph and Relationship Resolution:** graph projection, candidate matching, verification workflow and temporal edges.
3. **SFI-06 — Evaluation Contract and Conformance Validator:** semantic validation engine, error taxonomy and deterministic conformance runner.
4. **SFI-07 — Dataset Curation, Build and Release Pipeline:** immutable build manifests, policy gates, lineage and artifact registry.
5. **SFI-ADR series:** persistence, digest profile, tenant isolation, graph projection, artifact packaging and model/agent evidence safety.

## 18. Change control

This document is a normative proposal pending review. No requirement in this document becomes an approved product baseline until explicitly accepted. Changes to normative semantics MUST be reflected in the Notion specification, Git schema bundle, fixtures, validator tests and Linear acceptance criteria in one traceable update.
