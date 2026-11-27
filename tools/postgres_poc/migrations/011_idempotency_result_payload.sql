-- Isolated ArticleRevisionService PoC extension only.
-- Keep result_id for compatibility with existing SQL-only experiments while
-- storing the complete typed service result for exact idempotent replay.
ALTER TABLE idempotency_records
    ADD COLUMN result_payload JSONB;

ALTER TABLE idempotency_records
    ADD CONSTRAINT idempotency_result_payload_object_check
    CHECK (result_payload IS NULL OR jsonb_typeof(result_payload) = 'object');
