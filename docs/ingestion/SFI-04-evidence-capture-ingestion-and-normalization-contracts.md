# SFI-04 — Evidence Capture, Ingestion and Normalization Contracts

**Status:** Normative proposal for review; not approved  
**Work item:** SFI-04  
**Depends on:** SFI-01 Product Charter; SFI-02 System Architecture; SFI-03 Canonical Engineering Evidence and Dataset Model  
**Contract family:** SFI Connector and Ingestion Contracts v1  
**Schema dialect:** JSON Schema Draft 2020-12  
**Repository:** https://github.com/mkrdiop/software-factory-intelligence

## 1. Purpose

SFI-04 defines the source-neutral contract and operational lifecycle for capturing engineering evidence from external engineering systems and agent workflows, accepting deliveries durably, preserving source fidelity, normalizing observations into SFI-03 Engineering Evidence Records, and safely replaying or reconciling data.

The first source profiles are GitHub, Linear, Notion and explicitly instrumented AI-agent activity. These profiles are adapters to one shared ingestion contract, not four independent data models.

SFI-04 does not implement production connectors, select a queue/database/vendor, or redefine SFI-03. It specifies the contracts those implementations MUST satisfy.

## 2. Normative language and requirement identifiers

MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are normative. Requirements use stable identifiers in the form `SFI04-<area>-<number>`. A schema-valid envelope is only structurally valid; it is not evidence of source authenticity, authorization, semantic correctness or dataset eligibility.

## 3. Contract boundaries

The ingestion pipeline has six separately testable boundaries:

1. **Source adapter:** obtains source events or snapshots under an explicit source installation/connection and least-privilege scope.
2. **Delivery envelope:** transports an authenticated, bounded, versioned delivery with source identity and delivery metadata.
3. **Ingestion gateway:** authenticates the connector, enforces tenant/source binding, applies size/rate limits, deduplicates and durably accepts the envelope.
4. **Raw evidence archive:** preserves an exact permitted source payload or a controlled reference, with digest, retention and access policy.
5. **Normalizer:** applies a versioned source mapping and emits one or more SFI-03 records with field lineage.
6. **Reconciliation worker:** detects missed events, deletion/permission changes, drift and incomplete backfills through source polling or snapshots.

The source system remains authoritative. SFI is a consumer and evidence processor; it MUST NOT write changes back to source engineering records in the initial connector profile.

## 4. Core entities

### 4.1 Source Connection

A Source Connection is a tenant-scoped configured relationship to one source instance. It MUST have an SFI-generated immutable connection ID, tenant ID, workspace ID, source system identifier, source instance identifier, enabled state, granted scopes, credential reference, connector profile/version, configured data scope, retention policy reference and lifecycle timestamps.

A connection MUST bind to exactly one tenant and one workspace. Source instance identity MUST be stable within the source namespace. A connection MUST NOT be moved between tenants by editing its tenant ID; migration requires an explicit audited transfer process and reauthorization.

Secrets MUST be stored in a secrets manager. SFI configuration and delivery envelopes carry secret references or credential version identifiers only, never credential values.

### 4.2 Connector Identity

A connector identity identifies the software adapter, not the source actor or tenant. It includes connector ID, implementation name, semantic version, source profile, mapping profile/version and deployment identity. Connector identity MUST be authenticated at the gateway; caller-supplied connector labels alone are not authentication.

### 4.3 Delivery Envelope

A Delivery Envelope is a transport contract around source payload data. It is not itself an SFI-03 Engineering Evidence Record. It carries the metadata required for authenticated, idempotent, replayable processing and links to the captured source payload.

Required envelope fields:

| Field | Meaning |
|---|---|
| `envelopeVersion` | Delivery contract version, initially `1.0.0`. |
| `deliveryId` | Unique identifier for this transport attempt. |
| `connectionId` | SFI Source Connection identifier. |
| `tenantId`, `workspaceId` | Tenant/workspace asserted by the authenticated connection and checked by the gateway. |
| `source` | SFI-03 source identity tuple and event/revision context. |
| `delivery` | Delivery mode, received time, attempt and source cursor metadata. |
| `payload` | Media type, byte length, digest and inline payload or protected archive reference. |
| `authentication` | Verified authentication method and verification metadata; never raw secrets/signatures. |
| `connector` | Connector ID/version and mapping profile/version. |

The gateway MUST derive tenant/workspace/connection authority from authenticated server-side connection state. It MUST compare envelope claims to that state and reject mismatches. The envelope MUST NOT be trusted to choose its own tenant.

### 4.4 Cursor and Checkpoint

A cursor is opaque source-adapter state scoped to a connection, source endpoint/resource, and sync partition. It MUST be stored server-side, encrypted where it contains sensitive material, versioned by connector profile, and advanced only after all events represented by the checkpoint have been durably accepted.

A cursor is not a timestamp unless the source explicitly defines it as such. Connectors MUST NOT assume cursor ordering, arithmetic or portability between installations. Cursor advancement MUST be atomic with durable acceptance or recoverable through replay.

### 4.5 Normalization Result

A Normalization Result records the outcome of mapping one accepted delivery into zero, one or multiple SFI-03 evidence records. It MUST identify delivery ID, source object/event identity, connector version, mapping version, output evidence IDs, field-level lineage where feasible, warnings, omissions, redactions, and terminal result.

Result states: `normalized`, `partially-normalized`, `quarantined`, `rejected`, `retryable-failure`, `permanent-failure`. A no-op/duplicate outcome is represented separately as `duplicate`.

## 5. Delivery and acknowledgement semantics

### 5.1 Delivery modes

The contract supports:

- **Webhook/event push:** source sends a notification or event to a registered endpoint.
- **Polling/incremental sync:** connector fetches changes using source cursors or modified-since semantics.
- **Snapshot/backfill:** connector enumerates a bounded source scope and captures current state or historical ranges.
- **Agent instrumentation:** an authorized SDK/runtime emits explicitly declared action, tool, artifact and result events.

A source webhook may contain only a notification that a resource changed. In that case the adapter SHOULD fetch the authoritative current object under the connection's granted scope, preserving the notification and fetched snapshot as distinct provenance inputs.

### 5.2 At-least-once and idempotency

SFI guarantees at-least-once delivery processing, not exactly-once transport. The gateway MUST make durable acceptance idempotent.

The deduplication key MUST be derived from the authenticated connection, source instance, source event ID or stable source object revision, and delivery semantic type. Delivery ID alone is insufficient because retries may create new delivery IDs for the same source event.

Where a source has no stable event/revision ID, the connector MUST declare a deterministic fingerprint profile and its collision limitations. A changed source revision MUST NOT be suppressed as a duplicate. A repeated delivery of the same logical event MUST resolve to the original accepted delivery outcome.

### 5.3 Acknowledgement

A webhook endpoint MUST acknowledge only after the envelope is durably recorded or placed in a durable intake queue. It MUST NOT acknowledge merely because a request entered process memory.

Recommended response classes:
- accepted/deduplicated: successful 2xx acknowledgement;
- malformed or unauthenticated: 4xx rejection;
- rate limited: 429 with retry guidance where supported;
- transient internal unavailability before durable acceptance: 5xx so the source may retry.

The gateway MUST NOT return detailed tenant existence, credential state, internal topology or payload validation internals to unauthenticated callers.

### 5.4 Retry and dead-letter behavior

Transient failures MUST use bounded exponential backoff with jitter and an explicit retry budget. Permanent schema, authorization or policy failures MUST be quarantined or rejected with a stable machine-readable error code. Exhausted transient deliveries MUST enter a durable dead-letter/quarantine state with operator-visible diagnostics and replay capability.

Replay MUST preserve original source event time, observed time and payload digest. Replay time MUST be recorded separately. Reprocessing under a new connector or mapping version MUST create a new normalization run and lineage record; it MUST NOT silently overwrite previous outputs.

## 6. Capture and normalization pipeline

The required sequence is:

1. Authenticate connection and delivery origin.
2. Resolve server-side connection configuration and tenant/workspace binding.
3. Enforce source scope, request limits, payload size and media-type allowlist.
4. Verify webhook signature/token or connector API authentication where applicable.
5. Validate envelope structure and source instance identity.
6. Compute/verify payload digest over exact captured bytes.
7. Apply idempotency check and durably accept.
8. Archive payload or protected reference under the applicable retention and rights policy.
9. Normalize using an immutable, versioned mapping profile.
10. Validate emitted SFI-03 records structurally.
11. Run semantic and governance checks as separate stages.
12. Persist normalization result, provenance and lineage.
13. Advance source cursor/checkpoint only after durable acceptance and recoverable processing state.
14. Publish an internal evidence-accepted event for downstream projections.

The connector MUST NOT bypass the ingestion gateway to write directly into evidence history, graph storage, datasets or evaluation stores.

### 6.1 Field mapping and lineage

Every mapping profile MUST declare:
- source system and supported object/event types;
- profile identifier and semantic version;
- source API/webhook version assumptions;
- source field path to canonical field mapping;
- transformation type and deterministic behavior;
- null, missing, empty and deleted-field semantics;
- timestamp parsing and timezone policy;
- identity mapping rules;
- redaction and exclusion rules;
- fields preserved only in the raw payload;
- fields intentionally omitted and the reason;
- compatibility and migration notes.

A mapping MUST NOT invent source values. If a value is absent, unknown or unavailable due to scope, it remains absent/unknown and a warning may be recorded. Derived values MUST be marked as derived and identify the transformation. Lossy transformations MUST be disclosed in lineage.

Where practical, normalized fields SHOULD carry source JSON pointer/path and source revision provenance. A field-level lineage map is recommended for identity, timestamps, status, actor, content, labels and relationships.

### 6.2 Source-native semantics

Canonicalization MUST preserve source-native type, status, labels, actor identity, timestamps and source identifiers in a namespaced source metadata area or protected raw payload. Canonical evidence types are cross-source classifications; they MUST NOT replace source-native semantics.

Unknown source fields SHOULD be retained in the raw payload and MUST NOT be promoted to trusted canonical fields without a mapping rule. Unsupported event types MUST be safely ignored, archived or quarantined according to profile policy, with explicit metrics; they MUST NOT be silently misrepresented as a supported type.

### 6.3 Payload capture, redaction and archive

The archive MUST store only content permitted by source scope, contract, policy and applicable rights. Raw payload retention and normalized evidence retention may differ. SFI MUST define a maximum payload size and an explicit overflow policy per connector; silent truncation is prohibited.

If redaction is required, SFI MUST preserve the original digest and record whether the archived payload is raw, redacted or unavailable. If raw content cannot lawfully or contractually be retained, SFI MAY store only an allowed redacted snapshot or source reference, and MUST record the limitation. A digest alone is not a recoverable payload.

Credentials, webhook secrets, private keys, session cookies and access tokens MUST be removed before archive and normalization. Sensitive data discovered in payloads MUST trigger configured redaction/quarantine controls before downstream indexing or dataset use.

## 7. Initial source adapter profiles

All profiles below are read-only with respect to source records. Each connector MUST be independently enableable, scope-configurable, observable and revocable.

### 7.1 GitHub

**Initial evidence:** repository metadata, issues, issue comments, pull requests, review comments/reviews, commits, branches/tags/releases, workflow runs, check suites and check runs. CI logs/artifacts are optional and require separate explicit scopes and retention controls.

**Acquisition:** webhooks for supported event families plus periodic reconciliation polling. Webhook delivery IDs are retained for deduplication. Notifications that lack full object state trigger a source API fetch. Backfill uses bounded repository and date ranges with explicit rate-limit handling.

**Identity:** source system `github`; source instance identifies GitHub.com or a particular GitHub Enterprise installation; object type and object ID retain the source's stable IDs. Repository full name and URLs are descriptive locators, not sole identifiers. Installation/account scope is recorded.

**Mapping:** issues/PRs usually contribute intent and execution evidence; commits and release references contribute execution/outcome; reviews, checks and workflow results contribute validation. Classification is contextual and profile-versioned, not inferred solely from an event name.

**Constraints:** installation permissions are least-privilege; private repository access is tenant-authorized. Forks, transfers, renames, deleted resources, force pushes and webhook redelivery MUST be handled explicitly. Do not collect secrets from logs or artifacts. A commit SHA is a source revision identifier, not proof of review or deployment.

### 7.2 Linear

**Initial evidence:** teams/projects, initiatives, cycles, issues, comments, labels, relations, attachments metadata, status changes, assignee changes and project updates where permitted.

**Acquisition:** webhooks where available plus cursor/pagination-based reconciliation. Webhook payload and subsequent API-fetched object are separate provenance inputs. Backfill is bounded by workspace/team/project and explicit date ranges.

**Identity:** source system `linear`; source instance identifies the Linear workspace/tenant context. Preserve immutable issue/object IDs and identifiers such as `SFI-123` as source-native keys; identifiers may change or be reused under source rules and MUST NOT alone be treated as globally unique.

**Mapping:** projects/initiatives and issue descriptions can represent intent; issue status, cycle and assignment changes represent execution events; comments and project updates are contextual reasoning evidence, not automatically verified decisions. Links/relations remain source-native relationship evidence until mapped to an explicit SFI predicate.

**Constraints:** use workspace-authorized credentials and scopes. Do not infer completion quality from a status alone. Preserve issue history events when available; a current-state snapshot is not a complete event history.

### 7.3 Notion

**Initial evidence:** selected pages and database rows explicitly authorized for capture, including page metadata, content blocks, properties, comments/discussions when explicitly enabled, and revision/update metadata available through the API.

**Acquisition:** event notification/webhook where supported by the deployed Notion API profile plus periodic page/database reconciliation. Fetch page content and relevant block children under the configured scope. Notion page hierarchy and parent references MUST be retained.

**Identity:** source system `notion`; source instance identifies the connected workspace; page/block/database/data-source IDs are preserved exactly. Titles and page URLs are locators/descriptive values, not canonical identifiers.

**Mapping:** specifications, requirements, ADRs, design notes and decision records may map to intent or reasoning. Page type alone MUST NOT determine trust or approval. A page marked draft or unverified remains so; approval evidence must be explicit.

**Constraints:** capture is opt-in by workspace/page/database scope. Respect page permissions and content access. Do not assume that access to a parent implies permission to export every child or linked resource. Preserve block hierarchy and order. Comments/discussions and meeting transcripts require explicit policy/scope. Synced content and external embeds must retain origin references and must not be represented as locally authored. Uploaded files are separate artifacts with their own access and retention rules.

### 7.4 AI-agent instrumentation

**Initial evidence:** declared task/session metadata, user/agent identity, authorized prompt/task reference, tool invocation metadata, input/output artifact references, code diff/commit/PR references, test command/result summaries, environment metadata, agent model/provider/version where available, policy decisions, human approvals and final declared outcomes.

**Acquisition:** explicit SDK hooks, runtime instrumentation or signed agent event delivery. Each event MUST identify agent/session/run, tool, action type, time, execution environment, correlation/parent event, artifact references and declared result. Instrumentation MUST be configurable per tenant and task.

**Constraints:** private model chain-of-thought, hidden reasoning traces, private scratchpads and internal deliberation MUST NOT be captured. Capture only declared task context, authorized inputs, tool/action events, output artifacts and concise externally visible summaries. Secrets and unrelated user content MUST be excluded. Agent assertions are model/agent-generated evidence with appropriate origin and trust; they are not independent proof of execution or success. Tool results and test outputs should be separately captured as source/tool-observed evidence.

## 8. Source profile registry and compatibility

Each connector profile MUST declare a profile ID, version, source system, supported API versions, event/object types, required scopes, optional scopes, webhook verification method, polling strategy, cursor semantics, idempotency strategy, payload size limits, mapping version, known gaps, retention defaults and conformance fixture set.

Connector implementation version and mapping profile version are independent. A connector patch that does not change mapping semantics MAY keep the mapping version; any change to canonical meaning, field mapping, redaction or timestamp behavior MUST increment mapping version.

A connector MUST advertise supported profile versions and fail closed when a required source API contract is incompatible. Unknown fields may be retained but not interpreted as known semantics. Deprecation requires a migration window and compatibility notice.

## 9. Security, authorization and tenant isolation

- Connection authorization MUST be evaluated at setup, acquisition, delivery, normalization, query and export boundaries.
- Credentials are isolated by tenant and connection; operators and connector workers receive only required access.
- Webhook authentication MUST use source-supported signatures/tokens with replay protection and constant-time secret comparison where applicable. Secrets are rotated and revocable.
- The gateway MUST bind tenant/workspace identity from authenticated connection configuration, never from an untrusted envelope.
- Cross-tenant references, cursor reuse, payload archive references and idempotency collisions MUST be rejected.
- Source content is untrusted data. Instructions embedded in issues, documents, comments, code or logs MUST never alter connector configuration, policies, tool permissions or processing instructions.
- Rate limits, payload size, decompression ratio, archive quota and parsing time MUST be bounded.
- Audit logs record connection creation, scope changes, credential rotation, access, replay, redaction, quarantine, deletion and revocation without copying secrets or unnecessary content.

## 10. Privacy, rights, retention and revocation

Capture scope MUST be explicit and revocable. Source access is not equivalent to ownership or a grant for all SFI purposes. Every accepted SFI-03 record MUST carry the applicable governance envelope. Unknown or ambiguous rights MUST be represented as unknown/restricted, not assumed cleared.

Disconnecting a source prevents new acquisition but does not automatically erase already captured evidence. Erasure, retention expiry, access revocation and legal hold are separate lifecycle actions with explicit propagation to raw payloads, normalized evidence, graph projections, indexes, evaluations, datasets and exports.

A source deletion event MUST be interpreted according to source semantics and configured policy: it may mean source object deleted, access revoked, object unavailable, or event omitted. SFI MUST NOT infer legal erasure solely from an API 404. The connector records the observation and invokes the applicable governance workflow.

## 11. Observability and operational controls

Per connection and source profile, SFI MUST measure:
- last successful event and reconciliation;
- delivery rate, accepted, duplicate, rejected, quarantined and failed counts;
- webhook verification failures and retry distribution;
- source API latency, rate-limit responses and pagination progress;
- cursor age/lag and checkpoint position (without exposing sensitive cursor contents);
- normalization success, partial mapping, unknown event types and mapping warnings;
- payload sizes, redaction counts and archive failures;
- time from source event to durable acceptance and normalized evidence;
- replay/dead-letter backlog and reconciliation drift;
- policy denials, scope violations and cross-tenant rejection attempts.

Metrics SHOULD avoid high-cardinality labels containing user IDs, repository names, issue titles or document content. Logs SHOULD use stable opaque IDs and redacted diagnostics.

## 12. Failure handling and recovery

| Failure | Required behavior |
|---|---|
| Invalid webhook signature | Reject; audit; do not archive as trusted source evidence. |
| Tenant/connection mismatch | Reject; security event; no cursor advancement. |
| Duplicate delivery | Return original durable outcome; do not create duplicate evidence. |
| Rate limit / transient API failure | Backoff; preserve cursor; retry within budget. |
| Source permission revoked | Pause affected scope; mark connection degraded; do not broaden access. |
| Unknown event type | Preserve raw metadata if permitted; quarantine or ignore by explicit profile policy; emit metric. |
| Mapping error | Quarantine delivery with versioned diagnostics; do not fabricate partial facts. |
| Archive failure | Do not acknowledge durable acceptance unless another durable protected capture exists. |
| Normalizer outage | Keep durable intake; process later; do not lose cursor/event lineage. |
| Partial source outage | Continue unaffected partitions; expose degraded state. |
| Source deletion / 404 | Record source observation; distinguish unavailable/deleted/access denied; invoke policy workflow. |
| Connector version incompatibility | Fail closed for affected profile; preserve backlog for replay after upgrade. |

Recovery MUST be deterministic from durable delivery records and declared connector/mapping versions. Manual replay requires authorization and an audit entry. Reconciliation SHOULD periodically compare source scope snapshots with SFI-observed objects to identify missed events and drift.

## 13. API and event contract requirements

The implementation MUST expose versioned operations equivalent to:
- register/update/revoke a source connection;
- inspect connection health and granted scopes;
- accept a delivery envelope;
- inspect delivery status and normalization result;
- replay/quarantine resolution under authorization;
- trigger bounded backfill/reconciliation;
- inspect cursor/checkpoint metadata;
- inspect connector profile and mapping versions.

Internal events SHOULD distinguish `delivery.accepted`, `delivery.rejected`, `delivery.quarantined`, `normalization.completed`, `normalization.failed`, `source.reconciliation.detected-drift`, and `connection.revoked`. Event transport technology is deferred; event names and semantics are not.

## 14. Conformance and testing

A connector is conformant only when it passes:
1. Envelope structural schema validation.
2. Authentication and tenant-binding tests.
3. Idempotency/retry/replay tests.
4. Cursor checkpoint and pagination tests.
5. Payload digest/archive and redaction tests.
6. Mapping determinism and source-field lineage tests.
7. Permission/scope and revocation tests.
8. Tenant isolation and hostile payload tests.
9. Source deletion, rename/transfer and API drift tests where applicable.
10. SFI-03 record schema and semantic validation.
11. Operational metrics and failure recovery tests.

The initial fixture corpus MUST include valid webhook, poll, snapshot/backfill and agent events; invalid authentication/tenant mismatch; duplicate delivery; missing source revision; unsupported event; redaction; source deletion/permission loss; and partial normalization.

Synthetic fixtures MUST contain no live tokens, real customer data or private source content. Each negative fixture MUST declare expected failure stage and stable error code.

## 15. Acceptance criteria

- [ ] Source Connection, Connector Identity, Delivery Envelope, Cursor and Normalization Result are defined.
- [ ] Webhook, polling, snapshot/backfill and agent instrumentation modes are specified.
- [ ] At-least-once delivery, idempotency, acknowledgement, retry, quarantine and replay semantics are explicit.
- [ ] Gateway derives tenant/workspace authority from authenticated connection state.
- [ ] Payload integrity, raw archive, redaction and retention behavior are explicit.
- [ ] Mapping profiles are versioned and preserve source-native semantics and lineage.
- [ ] GitHub, Linear, Notion and agent adapter profiles are documented with scope and limitations.
- [ ] No hidden model chain-of-thought capture is permitted.
- [ ] Source connectors are read-only in the initial profile.
- [ ] Rights, deletion, revocation and tenant isolation are operational requirements.
- [ ] Failure handling, reconciliation and operational metrics are defined.
- [ ] Connector conformance and fixture taxonomy are actionable.
- [ ] SFI-03 canonical record semantics are reused without forking.
- [ ] Notion, GitHub and Linear resources are cross-linked.

## 16. Decisions deferred

Queue/broker technology; database and raw archive vendor; credential/secrets manager; concrete webhook cryptographic profile per source/API version; exact payload limits; cursor persistence implementation; universal event bus; canonical digest algorithm/profile; connector deployment topology; full OAuth app registration details; per-jurisdiction retention schedules; and source-specific exhaustive field maps. These require implementation ADRs or source-profile revisions.

## 17. Follow-on implementation sequence

1. **SFI-04a:** Connector Profile and Delivery Envelope schemas, fixtures and structural validator.
2. **SFI-04b:** Ingestion gateway, durable intake, idempotency ledger, retry/quarantine and replay.
3. **SFI-04c:** GitHub connector and mapping profile.
4. **SFI-04d:** Linear connector and mapping profile.
5. **SFI-04e:** Notion connector and mapping profile.
6. **SFI-04f:** Agent instrumentation SDK/event profile.
7. **SFI-04g:** Reconciliation, conformance harness and operational dashboards.

## 18. Change control

This specification is a normative proposal pending review. No connector profile, mapping or governance rule becomes an approved baseline until explicitly accepted. Contract changes MUST update the Notion specification, Git schemas, fixtures, validator tests and Linear acceptance criteria together.
