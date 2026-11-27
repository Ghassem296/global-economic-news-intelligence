-- ArticleRevisionService appends a revision before saving the new Article projection.
-- Defer the owner FK so both writes can remain in one UnitOfWork and are validated
-- together at commit; a transaction that omits the Article row still fails.
ALTER TABLE article_revisions
    ALTER CONSTRAINT article_revisions_article_id_fkey
    DEFERRABLE INITIALLY DEFERRED;
