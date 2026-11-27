-- Isolated qualification PoC only. Not a production schema.
-- FOR SHARE locks are held in the same transaction as protected writes.
-- Revocation updates conflict with those locks and serialize after commit.

CREATE TABLE poc_authorization_grants (
    grant_reference TEXT PRIMARY KEY,
    actor_reference TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_reference TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'REVOKED')),
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    effective_from TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    CHECK (expires_at IS NULL OR expires_at > effective_from)
);

CREATE TABLE poc_content_rights_assessments (
    assessment_reference TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    content_scope_fingerprint TEXT NOT NULL
        CHECK (content_scope_fingerprint ~ '^[0-9a-f]{64}$'),
    operation TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    rights_profile_reference TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('ALLOWED', 'DENIED', 'UNKNOWN', 'EXPIRED', 'REVOKED', 'REQUIRES_REVIEW')
    ),
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    effective_from TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    CHECK (expires_at IS NULL OR expires_at > effective_from)
);

CREATE INDEX poc_authorization_resource_idx
    ON poc_authorization_grants (actor_reference, action, resource_reference);

CREATE INDEX poc_content_rights_scope_idx
    ON poc_content_rights_assessments (source_id, content_scope_fingerprint, operation);
