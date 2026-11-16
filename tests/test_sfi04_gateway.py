from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from sfi_ingestion import IngestionError, IngestionGateway

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas/v1/sfi-04.schema.json"


def envelope(*, delivery_id="d-1", event_id="evt-1", tenant="tenant-a", cursor="c-1"):
    payload = {"action": "opened", "number": 17}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {
        "envelopeVersion": "1.0.0", "recordType": "delivery-envelope",
        "deliveryId": delivery_id, "connectionId": "conn-a", "tenantId": tenant,
        "workspaceId": "workspace-a",
        "source": {"system": "github", "instanceId": "github.com",
                   "objectType": "pull_request", "objectId": "17", "eventId": event_id},
        "delivery": {"mode": "webhook", "receivedAt": "2026-11-16T09:00:00Z",
                     "attempt": 1, "sourceCursor": cursor, "partition": "repo-1"},
        "payload": {"mediaType": "application/json", "sizeBytes": len(raw),
                    "digest": {"algorithm": "sha-256", "value": hashlib.sha256(raw).hexdigest()},
                    "inline": payload},
        "authentication": {"method": "hmac-signature", "verified": True,
                            "verifiedAt": "2026-11-16T09:00:00Z", "principalRef": "hook-1"},
        "connector": {"connectorId": "github-v1", "connectorVersion": "1.0.0",
                       "profileId": "github", "profileVersion": "1.0.0", "mappingVersion": "1.0.0"}
    }


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.gateway = IngestionGateway(Path(self.tmp.name) / "sfi.db", SCHEMA, max_attempts=2)
        self.gateway.register_connection(connection_id="conn-a", tenant_id="tenant-a",
            workspace_id="workspace-a", source_system="github", source_instance_id="github.com")

    def tearDown(self):
        self.tmp.cleanup()

    def test_accept_is_durable_and_advances_cursor_atomically(self):
        result = self.gateway.accept(envelope(), authenticated_connection_id="conn-a")
        self.assertEqual(result["outcome"], "accepted")
        self.assertEqual(self.gateway.get_delivery("d-1")["status"], "accepted")
        self.assertEqual(self.gateway.get_checkpoint("conn-a", "repo-1"), "c-1")

    def test_redelivery_is_idempotent_and_does_not_advance_cursor(self):
        self.gateway.accept(envelope(), authenticated_connection_id="conn-a")
        duplicate = envelope(delivery_id="d-2", cursor="c-2")
        result = self.gateway.accept(duplicate, authenticated_connection_id="conn-a")
        self.assertEqual(result["outcome"], "duplicate")
        self.assertEqual(result["deliveryId"], "d-1")
        self.assertEqual(self.gateway.get_checkpoint("conn-a", "repo-1"), "c-1")

    def test_tenant_claim_cannot_override_connection_authority(self):
        with self.assertRaisesRegex(IngestionError, "binding-mismatch"):
            self.gateway.accept(envelope(tenant="tenant-victim"), authenticated_connection_id="conn-a")

    def test_connection_identity_is_authenticated_not_caller_label(self):
        with self.assertRaisesRegex(IngestionError, "connection-mismatch"):
            self.gateway.accept(envelope(), authenticated_connection_id="conn-other")

    def test_payload_digest_is_verified_before_acceptance(self):
        bad = envelope()
        bad["payload"]["digest"]["value"] = "0" * 64
        with self.assertRaisesRegex(IngestionError, "digest-mismatch"):
            self.gateway.accept(bad, authenticated_connection_id="conn-a")
        self.assertIsNone(self.gateway.get_delivery("d-1"))
        self.assertIsNone(self.gateway.get_checkpoint("conn-a", "repo-1"))

    def test_schema_invalid_payload_is_rejected(self):
        bad = envelope()
        del bad["tenantId"]
        with self.assertRaisesRegex(IngestionError, "schema-invalid"):
            self.gateway.accept(bad, authenticated_connection_id="conn-a")

    def test_retry_then_quarantine_then_authorized_replay(self):
        self.gateway.accept(envelope(), authenticated_connection_id="conn-a")
        self.assertEqual(self.gateway.mark_failed("d-1", "normalizer-timeout")["status"], "retry")
        self.assertEqual(self.gateway.mark_failed("d-1", "normalizer-timeout")["status"], "quarantined")
        replayed = self.gateway.replay("d-1")
        self.assertEqual(replayed["status"], "retry")
        self.assertEqual(self.gateway.get_delivery("d-1")["status"], "retry")

    def test_unknown_connection_is_rejected(self):
        with self.assertRaisesRegex(IngestionError, "connection-unknown"):
            self.gateway.accept(envelope(), authenticated_connection_id="conn-missing")


if __name__ == "__main__":
    unittest.main()
