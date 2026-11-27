ALTER TABLE articles
    ADD COLUMN source_last_seen_at TIMESTAMPTZ;

CREATE INDEX articles_source_last_seen_idx
    ON articles (source_id, source_last_seen_at);
