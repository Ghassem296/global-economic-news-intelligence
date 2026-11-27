CREATE FUNCTION advance_external_operation_state()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.attempt_type = 'EXECUTE' THEN
        CASE NEW.outcome
            WHEN 'CONFIRMED_SUCCESS' THEN
                UPDATE external_operations
                SET status = 'SUCCEEDED', version = version + 1
                WHERE operation_id = NEW.operation_id AND status = 'IN_PROGRESS';
            WHEN 'CONFIRMED_FAILURE' THEN
                UPDATE external_operations
                SET status = 'FAILED', version = version + 1
                WHERE operation_id = NEW.operation_id AND status = 'IN_PROGRESS';
            WHEN 'OUTCOME_UNKNOWN' THEN
                UPDATE external_operations
                SET status = 'RECONCILIATION_REQUIRED', version = version + 1
                WHERE operation_id = NEW.operation_id AND status = 'IN_PROGRESS';
        END CASE;
    ELSIF NEW.attempt_type = 'RECONCILE' THEN
        CASE NEW.outcome
            WHEN 'RECONCILED_SUCCESS' THEN
                UPDATE external_operations
                SET status = 'SUCCEEDED', version = version + 1
                WHERE operation_id = NEW.operation_id
                  AND status = 'RECONCILIATION_REQUIRED';
            WHEN 'RECONCILED_NOT_APPLIED' THEN
                UPDATE external_operations
                SET status = 'PENDING', version = version + 1
                WHERE operation_id = NEW.operation_id
                  AND status = 'RECONCILIATION_REQUIRED';
        END CASE;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER external_attempt_advance_operation_state
AFTER INSERT ON external_attempts
FOR EACH ROW
EXECUTE FUNCTION advance_external_operation_state();
