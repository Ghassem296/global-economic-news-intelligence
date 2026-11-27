CREATE TABLE backup_payload (
    payload_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payload TEXT NOT NULL
);

CREATE INDEX backup_payload_length_idx
    ON backup_payload ((length(payload)));
