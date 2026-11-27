CREATE TABLE decision_cases (
    case_id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

INSERT INTO decision_cases (case_id)
SELECT DISTINCT case_id FROM decision_records
ON CONFLICT (case_id) DO NOTHING;

ALTER TABLE decision_records
    ADD CONSTRAINT decision_records_case_fk
    FOREIGN KEY (case_id) REFERENCES decision_cases(case_id);

ALTER TABLE decision_records
    ADD CONSTRAINT decision_records_outcome_check
    CHECK (outcome IN ('OPEN', 'MATCH', 'NO_MATCH'));

ALTER TABLE article_revisions
    ADD CONSTRAINT article_revisions_article_revision_unique
    UNIQUE (article_id, revision_id);

ALTER TABLE articles
    ADD COLUMN current_revision_id UUID;

ALTER TABLE articles
    ADD CONSTRAINT articles_current_revision_fk
    FOREIGN KEY (article_id, current_revision_id)
    REFERENCES article_revisions (article_id, revision_id)
    DEFERRABLE INITIALLY DEFERRED;

-- The UNIQUE constraint above already provides this lookup index.
-- Drop the duplicate standalone index created by the initial PoC schema.
DROP INDEX IF EXISTS articles_source_identity_idx;
