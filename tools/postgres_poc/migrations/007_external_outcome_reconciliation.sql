CREATE TABLE external_operations (
    operation_id UUID PRIMARY KEY,
    operation_kind TEXT NOT NULL CHECK (operation_kind IN ('PUBLICATION', 'DELIVERY')),
    status TEXT NOT NULL CHECK (
        status IN (
            'PENDING',
            'IN_PROGRESS',
            'RECONCILIATION_REQUIRED',
            'SUCCEEDED',
            'FAILED',
            'CANCELLED'
        )
    ),
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE external_attempts (
    attempt_id UUID PRIMARY KEY,
    operation_id UUID NOT NULL REFERENCES external_operations(operation_id),
    attempt_number INTEGER NOT NULL CHECK (attempt_number > 0),
    attempt_type TEXT NOT NULL CHECK (attempt_type IN ('EXECUTE', 'RECONCILE')),
    outcome TEXT NOT NULL CHECK (
        outcome IN (
            'CONFIRMED_SUCCESS',
            'CONFIRMED_FAILURE',
            'OUTCOME_UNKNOWN',
            'RECONCILED_SUCCESS',
            'RECONCILED_NOT_APPLIED'
        )
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (operation_id, attempt_number)
);

CREATE FUNCTION guard_external_attempt_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    current_status TEXT;
BEGIN
    SELECT status
    INTO current_status
    FROM external_operations
    WHERE operation_id = NEW.operation_id
    FOR UPDATE;

    IF current_status IS NULL THEN
        RAISE EXCEPTION 'External operation does not exist'
            USING ERRCODE = '23503';
    END IF;

    IF NEW.attempt_type = 'EXECUTE' AND current_status <> 'IN_PROGRESS' THEN
        RAISE EXCEPTION 'Side-effecting execution is blocked until operation is IN_PROGRESS'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.attempt_type = 'RECONCILE' AND current_status <> 'RECONCILIATION_REQUIRED' THEN
        RAISE EXCEPTION 'Reconciliation is allowed only for unknown outcomes'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER external_attempt_state_guard
BEFORE INSERT ON external_attempts
FOR EACH ROW
EXECUTE FUNCTION guard_external_attempt_state();
