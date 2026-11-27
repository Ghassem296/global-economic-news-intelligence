-- Isolated ArticleRevisionService integration PoC schema extension only.
-- The complete typed revision payload is retained as JSONB; nullable columns
-- preserve compatibility with earlier SQL-only PoC fixtures and legacy rows.
ALTER TABLE articles
    ADD COLUMN canonical_source_identifier TEXT,
    ADD COLUMN identity_normalization_version TEXT,
    ADD COLUMN canonical_url TEXT,
    ADD COLUMN original_url TEXT,
    ADD COLUMN external_id TEXT,
    ADD COLUMN title TEXT,
    ADD COLUMN content_availability TEXT,
    ADD COLUMN content_reference TEXT,
    ADD COLUMN content_hash TEXT,
    ADD COLUMN content_normalization_version TEXT,
    ADD COLUMN summary TEXT,
    ADD COLUMN author TEXT,
    ADD COLUMN language TEXT,
    ADD COLUMN published_at TIMESTAMPTZ,
    ADD COLUMN article_metadata JSONB,
    ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp();

ALTER TABLE articles
    DROP CONSTRAINT articles_source_id_external_identity_key;

ALTER TABLE articles
    ADD CONSTRAINT articles_source_identity_v2_unique
    UNIQUE (source_id, canonical_source_identifier, identity_normalization_version);

ALTER TABLE articles
    ADD CONSTRAINT articles_source_identity_v2_pair_check
    CHECK (
        (canonical_source_identifier IS NULL AND identity_normalization_version IS NULL)
        OR
        (canonical_source_identifier IS NOT NULL
         AND identity_normalization_version IS NOT NULL)
    );

ALTER TABLE articles
    ADD CONSTRAINT articles_metadata_object_check
    CHECK (article_metadata IS NULL OR jsonb_typeof(article_metadata) = 'object');

ALTER TABLE articles
    ADD CONSTRAINT articles_content_availability_check
    CHECK (
        content_availability IS NULL
        OR content_availability IN ('available', 'partial', 'metadata-only', 'unavailable')
    );

ALTER TABLE article_revisions
    ADD COLUMN revision_payload JSONB,
    ADD COLUMN revision_fingerprint_schema_version TEXT;

ALTER TABLE article_revisions
    ADD CONSTRAINT article_revisions_payload_object_check
    CHECK (revision_payload IS NULL OR jsonb_typeof(revision_payload) = 'object');

ALTER TABLE article_revisions
    ADD CONSTRAINT article_revisions_payload_fingerprint_version_check
    CHECK (
        (revision_payload IS NULL AND revision_fingerprint_schema_version IS NULL)
        OR
        (revision_payload IS NOT NULL
         AND revision_fingerprint_schema_version IS NOT NULL
         AND length(revision_fingerprint_schema_version) > 0)
    );
