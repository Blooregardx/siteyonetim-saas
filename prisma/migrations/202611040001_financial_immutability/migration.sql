-- SPDX-License-Identifier: AGPL-3.0-only
-- Charge identity and successful bulk idempotency history are append-only.
-- Row locks still work with UPDATE(id) grants; no existing rows are changed.
CREATE TRIGGER charge_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "Charge"
FOR EACH STATEMENT EXECUTE FUNCTION reject_financial_mutation();
CREATE TRIGGER bulk_charge_operation_immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON "BulkChargeOperation"
FOR EACH STATEMENT EXECUTE FUNCTION reject_financial_mutation();
