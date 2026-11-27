CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE sources (
    source_id TEXT PRIMARY KEY
);

CREATE TABLE articles (
    article_id UUID PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    external_identity TEXT NOT NULL,
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (source_id, external_identity)
);

CREATE TABLE article_revisions (
    revision_id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(article_id),
    revision_number INTEGER NOT NULL CHECK (revision_number > 0),
    fingerprint TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (article_id, revision_number)
);

CREATE INDEX article_revisions_fingerprint_idx
    ON article_revisions (article_id, fingerprint);

CREATE TABLE idempotency_records (
    operation_scope TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    request_fingerprint TEXT NOT NULL,
    result_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (operation_scope, idempotency_key)
);

CREATE TABLE events (
    event_id UUID PRIMARY KEY
);

CREATE TABLE decision_records (
    decision_id UUID PRIMARY KEY,
    case_id UUID NOT NULL,
    predecessor_decision_id UUID UNIQUE REFERENCES decision_records(decision_id),
    outcome TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE article_event_links (
    link_id UUID PRIMARY KEY,
    decision_id UUID NOT NULL REFERENCES decision_records(decision_id),
    article_id UUID NOT NULL REFERENCES articles(article_id),
    event_id UUID NOT NULL REFERENCES events(event_id),
    UNIQUE (decision_id, article_id, event_id)
);

CREATE TABLE evidence_locations (
    location_id UUID PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    uri TEXT NOT NULL
);

CREATE TABLE analyses (
    analysis_id UUID PRIMARY KEY
);

CREATE TABLE analysis_inputs (
    analysis_id UUID NOT NULL REFERENCES analyses(analysis_id),
    input_id UUID NOT NULL,
    PRIMARY KEY (analysis_id, input_id)
);

CREATE TABLE analysis_evidence_links (
    analysis_id UUID NOT NULL,
    input_id UUID NOT NULL,
    evidence_location_id UUID NOT NULL REFERENCES evidence_locations(location_id),
    PRIMARY KEY (analysis_id, input_id, evidence_location_id),
    FOREIGN KEY (analysis_id, input_id)
        REFERENCES analysis_inputs(analysis_id, input_id)
);

CREATE TABLE reports (
    report_id UUID PRIMARY KEY
);

CREATE TABLE report_provenance_links (
    report_id UUID NOT NULL REFERENCES reports(report_id),
    evidence_location_id UUID NOT NULL REFERENCES evidence_locations(location_id),
    PRIMARY KEY (report_id, evidence_location_id)
);

CREATE TABLE execution_leases (
    resource_id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    fencing_token BIGINT NOT NULL CHECK (fencing_token > 0),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE protected_state (
    resource_id TEXT PRIMARY KEY,
    fencing_token BIGINT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE counters (
    counter_name TEXT PRIMARY KEY,
    value BIGINT NOT NULL CHECK (value >= 0)
);

CREATE INDEX articles_source_identity_idx
    ON articles (source_id, external_identity);
