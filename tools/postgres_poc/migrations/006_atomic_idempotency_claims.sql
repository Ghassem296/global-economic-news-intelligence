ALTER TABLE idempotency_records
    ALTER COLUMN result_id DROP NOT NULL;

ALTER TABLE idempotency_records
    ADD COLUMN state TEXT NOT NULL DEFAULT 'COMPLETED',
    ADD COLUMN completed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp();

ALTER TABLE idempotency_records
    ALTER COLUMN completed_at DROP NOT NULL;

ALTER TABLE idempotency_records
    ADD CONSTRAINT idempotency_records_state_check
    CHECK (
        (state = 'CLAIMED' AND result_id IS NULL AND completed_at IS NULL)
        OR
        (state = 'COMPLETED' AND result_id IS NOT NULL AND completed_at IS NOT NULL)
    );
