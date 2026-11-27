from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.application.article_revision_commands import (
    PersistArticleRevisionCommand,
    PersistArticleRevisionResult,
)
from global_economic_news_intelligence.application.article_revision_service import (
    ArticleProjection,
    ArticleRevisionService,
)
from global_economic_news_intelligence.domain.article_revision_contracts import (
    ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
    ArticleRevisionRecord,
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import (
    CommandMetadata,
    CommitResult,
)
from global_economic_news_intelligence.exceptions import ErrorCode, GeniError

NOW = datetime(2026, 11, 27, 8, 0, tzinfo=UTC)
IDENTITY = SourceArticleIdentity("publisher:123", "source-id-v1")


def make_revision(title: str = "Central bank holds rates") -> PersistArticleRevision:
    return PersistArticleRevision(
        source_id="source-1",
        source_article_identity=IDENTITY,
        original_url="https://example.com/article/123",
        external_id="123",
        normalized_title=title,
        content_availability=ContentAvailability.METADATA_ONLY,
        content_reference=None,
        content_hash=None,
        content_normalization_version=None,
        summary="Policy decision summary",
        author="A. Writer",
        language="en",
        published_at=None,
        observed_at=NOW,
        change_reason="INITIAL_COLLECTION",
        rights_assessment_references=("metadata-assessment-1",),
    )


def make_metadata(expected_version: str | None = None) -> CommandMetadata:
    return CommandMetadata(
        command_id="command-1",
        schema_version="1",
        actor_reference="service:collector",
        authorization_reference="authorization-1",
        correlation_id="correlation-1",
        idempotency_scope="article.revision.persist",
        idempotency_key="request-1",
        expected_aggregate_version=expected_version,
    )


class FakeClock:
    def now(self) -> datetime:
        return datetime(2026, 11, 27, 9, 0, tzinfo=UTC)


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    def commit(self) -> CommitResult:
        self.committed = True
        return CommitResult()

    def rollback(self) -> None:
        self.rolled_back = True


class FakeUnitOfWorkFactory:
    def __init__(self) -> None:
        self.items: list[FakeUnitOfWork] = []

    def begin(self) -> FakeUnitOfWork:
        item = FakeUnitOfWork()
        self.items.append(item)
        return item


class FakeArticleIds:
    def __init__(self) -> None:
        self.calls = 0

    def new_article_id(self) -> str:
        self.calls += 1
        return f"article-{self.calls}"


class FakeAuthorization:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls: list[tuple[CommandMetadata, str, str]] = []

    def is_authorized(
        self,
        metadata: CommandMetadata,
        *,
        action: str,
        resource_reference: str,
    ) -> bool:
        self.calls.append((metadata, action, resource_reference))
        return self.allowed


class FakeContentRights:
    def __init__(
        self,
        allowed: bool = True,
        metadata_allowed: bool = True,
    ) -> None:
        self.allowed = allowed
        self.metadata_allowed = metadata_allowed
        self.calls: list[tuple[PersistArticleRevision, datetime]] = []
        self.metadata_calls: list[tuple[PersistArticleRevision, datetime]] = []

    def permits_metadata_retention(
        self,
        revision: PersistArticleRevision,
        *,
        at: datetime,
    ) -> bool:
        self.metadata_calls.append((revision, at))
        return self.metadata_allowed

    def permits_persistent_storage(
        self,
        revision: PersistArticleRevision,
        *,
        at: datetime,
    ) -> bool:
        self.calls.append((revision, at))
        return self.allowed


class FakeIdempotency:
    def __init__(self) -> None:
        self.entries: dict[tuple[str, str], tuple[str, PersistArticleRevisionResult | None]] = {}

    def claim(
        self,
        *,
        scope: str,
        key: str,
        request_fingerprint: str,
        uow: FakeUnitOfWork,
    ) -> PersistArticleRevisionResult | None:
        identity = (scope, key)
        previous = self.entries.get(identity)
        if previous is None:
            self.entries[identity] = (request_fingerprint, None)
            return None
        if previous[0] != request_fingerprint:
            raise GeniError(
                ErrorCode.IDEMPOTENCY_KEY_REUSE_CONFLICT,
                "Idempotency key was reused.",
                correlation_id="correlation-1",
            )
        return previous[1]

    def complete(
        self,
        *,
        scope: str,
        key: str,
        request_fingerprint: str,
        result: PersistArticleRevisionResult,
        uow: FakeUnitOfWork,
    ) -> None:
        self.entries[(scope, key)] = (request_fingerprint, result)


class FakeArticleRepository:
    def __init__(self) -> None:
        self.items: dict[str, ArticleProjection] = {}
        self.save_calls = 0

    def get_by_id(self, article_id: str) -> ArticleProjection | None:
        return self.items.get(article_id)

    def find_by_source_identity(
        self,
        source_id: str,
        external_identity: SourceArticleIdentity,
    ) -> ArticleProjection | None:
        return next(
            (
                item
                for item in self.items.values()
                if item.source_id == source_id
                and item.source_article_identity.canonical_source_identifier
                == external_identity.canonical_source_identifier
                and item.source_article_identity.normalization_version
                == external_identity.normalization_version
            ),
            None,
        )

    def save_projection(
        self,
        article: ArticleProjection,
        expected_version: str | None,
        uow: FakeUnitOfWork,
    ) -> ArticleProjection:
        self.save_calls += 1
        version_number = (
            1
            if expected_version is None
            else int(expected_version.rsplit("-", 1)[-1]) + 1
        )
        saved = replace(article, aggregate_version=f"article-version-{version_number}")
        self.items[saved.article_id] = saved
        return saved


class FakeArticleRevisionRepository:
    def __init__(self) -> None:
        self.current: dict[str, ArticleRevisionRecord] = {}
        self.append_calls = 0

    def get_by_id(self, revision_id: str) -> ArticleRevisionRecord | None:
        return next(
            (item for item in self.current.values() if item.revision_id == revision_id),
            None,
        )

    def get_current_for_article(self, article_id: str) -> ArticleRevisionRecord | None:
        return self.current.get(article_id)

    def find_current_by_revision_fingerprint(
        self,
        article_id: str,
        revision_fingerprint: str,
        schema_version: str,
    ) -> ArticleRevisionRecord | None:
        item = self.current.get(article_id)
        if (
            item is not None
            and item.revision_fingerprint == revision_fingerprint
            and item.revision_fingerprint_schema_version == schema_version
        ):
            return item
        return None

    def append_revision(
        self,
        article_id: str,
        revision: PersistArticleRevision,
        expected_article_version: str | None,
        uow: FakeUnitOfWork,
    ) -> ArticleRevisionRecord:
        self.append_calls += 1
        previous = self.current.get(article_id)
        record = ArticleRevisionRecord(
            revision_id=f"revision-{self.append_calls}",
            article_id=article_id,
            revision_number=1 if previous is None else previous.revision_number + 1,
            payload=revision,
            revision_fingerprint=revision.revision_fingerprint,
            revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
            created_at=revision.observed_at,
        )
        self.current[article_id] = record
        return record


def build_service(
    *,
    articles: FakeArticleRepository | None = None,
    revisions: FakeArticleRevisionRepository | None = None,
    authorization: FakeAuthorization | None = None,
    rights: FakeContentRights | None = None,
    idempotency: FakeIdempotency | None = None,
    clock: object | None = None,
) -> tuple[ArticleRevisionService, dict[str, object]]:
    dependencies: dict[str, object] = {
        "articles": articles or FakeArticleRepository(),
        "revisions": revisions or FakeArticleRevisionRepository(),
        "authorization": authorization or FakeAuthorization(),
        "rights": rights or FakeContentRights(),
        "idempotency": idempotency or FakeIdempotency(),
        "uow_factory": FakeUnitOfWorkFactory(),
        "ids": FakeArticleIds(),
        "clock": clock or FakeClock(),
    }
    service = ArticleRevisionService(
        articles=dependencies["articles"],  # type: ignore[arg-type]
        revisions=dependencies["revisions"],  # type: ignore[arg-type]
        idempotency=dependencies["idempotency"],  # type: ignore[arg-type]
        unit_of_work_factory=dependencies["uow_factory"],  # type: ignore[arg-type]
        authorization=dependencies["authorization"],  # type: ignore[arg-type]
        content_rights=dependencies["rights"],  # type: ignore[arg-type]
        article_ids=dependencies["ids"],  # type: ignore[arg-type]
        clock=dependencies["clock"],  # type: ignore[arg-type]
    )
    return service, dependencies


def test_new_article_append_and_projection_share_one_unit_of_work() -> None:
    service, deps = build_service()
    result = service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))

    articles = deps["articles"]
    revisions = deps["revisions"]
    uow_factory = deps["uow_factory"]
    assert isinstance(articles, FakeArticleRepository)
    assert isinstance(revisions, FakeArticleRevisionRepository)
    assert isinstance(uow_factory, FakeUnitOfWorkFactory)
    assert result == PersistArticleRevisionResult(
        article_id="article-1",
        revision_id="revision-1",
        created=True,
        article_version="article-version-1",
    )
    assert articles.items["article-1"].current_revision_id == "revision-1"
    assert articles.items["article-1"].created_at == FakeClock().now()
    with pytest.raises(TypeError):
        articles.items["article-1"].metadata["mutate"] = "not allowed"
    assert revisions.current["article-1"].revision_number == 1
    assert uow_factory.items[0].committed
    assert not uow_factory.items[0].rolled_back


def test_same_current_fingerprint_reuses_revision_without_projection_write() -> None:
    articles = FakeArticleRepository()
    revisions = FakeArticleRevisionRepository()
    revision = make_revision()
    record = ArticleRevisionRecord(
        revision_id="revision-existing",
        article_id="article-existing",
        revision_number=1,
        payload=revision,
        revision_fingerprint=revision.revision_fingerprint,
        revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        created_at=NOW,
    )
    revisions.current["article-existing"] = record
    articles.items["article-existing"] = ArticleProjection(
        article_id="article-existing",
        source_id=revision.source_id,
        source_article_identity=revision.source_article_identity,
        url=revision.original_url,
        canonical_url=revision.source_article_identity.canonical_url,
        external_id=revision.external_id,
        title=revision.normalized_title,
        content_availability=revision.content_availability,
        content_reference=revision.content_reference,
        content_hash=revision.content_hash,
        content_normalization_version=revision.content_normalization_version,
        summary=revision.summary,
        author=revision.author,
        language=revision.language,
        published_at=revision.published_at,
        current_revision_id=record.revision_id,
        metadata={},
        aggregate_version="article-version-4",
        created_at=NOW,
        updated_at=NOW,
    )
    service, deps = build_service(articles=articles, revisions=revisions)
    result = service.execute(
        PersistArticleRevisionCommand(
            make_metadata("article-version-4"),
            revision,
            article_id="article-existing",
        )
    )

    assert result.revision_id == "revision-existing"
    assert not result.created
    assert articles.save_calls == 0
    assert revisions.append_calls == 0
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items[0].committed



def test_explicit_article_update_rejects_stale_version_even_when_revision_is_current() -> None:
    articles = FakeArticleRepository()
    revisions = FakeArticleRevisionRepository()
    revision = make_revision()
    record = ArticleRevisionRecord(
        revision_id="revision-existing",
        article_id="article-existing",
        revision_number=1,
        payload=revision,
        revision_fingerprint=revision.revision_fingerprint,
        revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        created_at=NOW,
    )
    revisions.current["article-existing"] = record
    articles.items["article-existing"] = ArticleProjection(
        article_id="article-existing",
        source_id=revision.source_id,
        source_article_identity=revision.source_article_identity,
        url=revision.original_url,
        canonical_url=revision.source_article_identity.canonical_url,
        external_id=revision.external_id,
        title=revision.normalized_title,
        content_availability=revision.content_availability,
        content_reference=revision.content_reference,
        content_hash=revision.content_hash,
        content_normalization_version=revision.content_normalization_version,
        summary=revision.summary,
        author=revision.author,
        language=revision.language,
        published_at=revision.published_at,
        current_revision_id=record.revision_id,
        metadata={},
        aggregate_version="article-version-4",
        created_at=NOW,
        updated_at=NOW,
    )
    service, deps = build_service(articles=articles, revisions=revisions)

    with pytest.raises(GeniError) as exc:
        service.execute(
            PersistArticleRevisionCommand(
                make_metadata("article-version-3"),
                revision,
                article_id="article-existing",
            )
        )

    assert exc.value.code is ErrorCode.STALE_VERSION
    assert articles.save_calls == 0
    assert revisions.append_calls == 0
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items[0].rolled_back



def test_current_revision_must_belong_to_the_addressed_article() -> None:
    articles = FakeArticleRepository()
    revisions = FakeArticleRevisionRepository()
    revision = make_revision()
    record = ArticleRevisionRecord(
        revision_id="revision-existing",
        article_id="another-article",
        revision_number=1,
        payload=revision,
        revision_fingerprint=revision.revision_fingerprint,
        revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        created_at=NOW,
    )
    revisions.current["article-existing"] = record
    articles.items["article-existing"] = ArticleProjection(
        article_id="article-existing",
        source_id=revision.source_id,
        source_article_identity=revision.source_article_identity,
        url=revision.original_url,
        canonical_url=revision.source_article_identity.canonical_url,
        external_id=revision.external_id,
        title=revision.normalized_title,
        content_availability=revision.content_availability,
        content_reference=revision.content_reference,
        content_hash=revision.content_hash,
        content_normalization_version=revision.content_normalization_version,
        summary=revision.summary,
        author=revision.author,
        language=revision.language,
        published_at=revision.published_at,
        current_revision_id=record.revision_id,
        metadata={},
        aggregate_version="article-version-4",
        created_at=NOW,
        updated_at=NOW,
    )
    service, deps = build_service(articles=articles, revisions=revisions)

    with pytest.raises(GeniError) as exc:
        service.execute(
            PersistArticleRevisionCommand(
                make_metadata("article-version-4"),
                revision,
                article_id="article-existing",
            )
        )

    assert exc.value.code is ErrorCode.INVARIANT_VIOLATION
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items[0].rolled_back


def test_authorization_denial_prevents_transaction_start() -> None:
    authorization = FakeAuthorization(allowed=False)
    service, deps = build_service(authorization=authorization)

    with pytest.raises(GeniError) as exc:
        service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))

    assert exc.value.code is ErrorCode.AUTHORIZATION_DENIED
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items == []


def test_metadata_only_revision_checks_metadata_rights_not_full_text_rights() -> None:
    rights = FakeContentRights()
    service, _ = build_service(rights=rights)
    service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))
    assert rights.calls == []
    assert len(rights.metadata_calls) == 1


def test_changed_source_identity_requires_explicit_versioned_update() -> None:
    articles = FakeArticleRepository()
    revisions = FakeArticleRevisionRepository()
    original = make_revision()
    record = ArticleRevisionRecord(
        revision_id="revision-current",
        article_id="article-existing",
        revision_number=1,
        payload=original,
        revision_fingerprint=original.revision_fingerprint,
        revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        created_at=NOW,
    )
    revisions.current["article-existing"] = record
    articles.items["article-existing"] = ArticleProjection(
        article_id="article-existing",
        source_id=original.source_id,
        source_article_identity=original.source_article_identity,
        url=original.original_url,
        canonical_url=original.source_article_identity.canonical_url,
        external_id=original.external_id,
        title=original.normalized_title,
        content_availability=original.content_availability,
        content_reference=original.content_reference,
        content_hash=original.content_hash,
        content_normalization_version=original.content_normalization_version,
        summary=original.summary,
        author=original.author,
        language=original.language,
        published_at=original.published_at,
        current_revision_id=record.revision_id,
        metadata={},
        aggregate_version="article-version-2",
        created_at=NOW,
        updated_at=NOW,
    )
    service, _ = build_service(articles=articles, revisions=revisions)

    with pytest.raises(GeniError) as exc:
        service.execute(
            PersistArticleRevisionCommand(
                make_metadata(),
                make_revision("Central bank changes rates"),
            )
        )

    assert exc.value.code is ErrorCode.CONFLICT


def test_persistent_content_is_denied_when_rights_verifier_fails() -> None:
    content = "Permitted full text for this synthetic test."
    import hashlib

    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    revision = PersistArticleRevision(
        source_id="source-1",
        source_article_identity=IDENTITY,
        original_url="https://example.com/article/123",
        external_id="123",
        normalized_title="Central bank holds rates",
        content_availability=ContentAvailability.AVAILABLE,
        content_reference="content://synthetic/article-123",
        content_hash=digest,
        content_normalization_version="normalization-v1",
        summary=None,
        author=None,
        language="en",
        published_at=None,
        observed_at=NOW,
        change_reason="INITIAL_COLLECTION",
        rights_assessment_references=("storage-assessment-1",),
    )
    rights = FakeContentRights(allowed=False)
    service, deps = build_service(rights=rights)

    with pytest.raises(GeniError) as exc:
        service.execute(PersistArticleRevisionCommand(make_metadata(), revision))

    assert exc.value.code is ErrorCode.RIGHTS_NOT_ALLOWED
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items == []
    assert rights.calls[0][1] == datetime(2026, 11, 27, 9, 0, tzinfo=UTC)


def test_metadata_rights_denial_prevents_metadata_only_persistence() -> None:
    rights = FakeContentRights(metadata_allowed=False)
    service, deps = build_service(rights=rights)

    with pytest.raises(GeniError) as exc:
        service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))

    assert exc.value.code is ErrorCode.RIGHTS_NOT_ALLOWED
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items == []



def test_identical_retry_replays_result_after_rechecking_authorization_and_rights() -> None:
    service, deps = build_service()
    command = PersistArticleRevisionCommand(make_metadata(), make_revision())

    first = service.execute(command)
    second = service.execute(command)

    articles = deps["articles"]
    revisions = deps["revisions"]
    rights = deps["rights"]
    authorization = deps["authorization"]
    factory = deps["uow_factory"]
    assert isinstance(articles, FakeArticleRepository)
    assert isinstance(revisions, FakeArticleRevisionRepository)
    assert isinstance(rights, FakeContentRights)
    assert isinstance(authorization, FakeAuthorization)
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert first == second
    assert articles.save_calls == 1
    assert revisions.append_calls == 1
    assert len(authorization.calls) == 2
    assert len(rights.metadata_calls) == 2
    assert factory.items[1].rolled_back


def test_reusing_idempotency_key_for_changed_request_is_rejected() -> None:
    service, deps = build_service()
    service.execute(
        PersistArticleRevisionCommand(make_metadata(), make_revision())
    )

    with pytest.raises(GeniError) as exc:
        service.execute(
            PersistArticleRevisionCommand(
                make_metadata(),
                make_revision("Central bank changes rates"),
            )
        )

    assert exc.value.code is ErrorCode.IDEMPOTENCY_KEY_REUSE_CONFLICT
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items[1].rolled_back


def test_available_content_requires_both_metadata_and_persistent_storage_rights() -> None:
    import hashlib

    body = "Synthetic article text used only in this test."
    revision = PersistArticleRevision(
        source_id="source-1",
        source_article_identity=IDENTITY,
        original_url="https://example.com/article/123",
        external_id="123",
        normalized_title="Central bank holds rates",
        content_availability=ContentAvailability.AVAILABLE,
        content_reference="content://synthetic/article-123",
        content_hash=hashlib.sha256(body.encode("utf-8")).hexdigest(),
        content_normalization_version="normalization-v1",
        summary="Policy decision summary",
        author="A. Writer",
        language="en",
        published_at=None,
        observed_at=NOW,
        change_reason="INITIAL_COLLECTION",
        rights_assessment_references=(
            "metadata-assessment-1",
            "storage-assessment-1",
        ),
    )
    rights = FakeContentRights()
    service, deps = build_service(rights=rights)

    result = service.execute(
        PersistArticleRevisionCommand(make_metadata(), revision)
    )

    assert result.created
    assert len(rights.metadata_calls) == 1
    assert len(rights.calls) == 1
    assert rights.calls[0][1] == rights.metadata_calls[0][1]
    assert rights.calls[0][1] == datetime(2026, 11, 27, 9, 0, tzinfo=UTC)
    articles = deps["articles"]
    assert isinstance(articles, FakeArticleRepository)
    assert articles.items[result.article_id].content_availability is ContentAvailability.AVAILABLE


def test_revision_without_rights_assessment_references_is_denied() -> None:
    revision = replace(make_revision(), rights_assessment_references=())
    service, deps = build_service()

    with pytest.raises(GeniError) as exc:
        service.execute(PersistArticleRevisionCommand(make_metadata(), revision))

    assert exc.value.code is ErrorCode.RIGHTS_NOT_ALLOWED
    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items == []


def test_idempotency_key_reuse_with_changed_canonical_url_is_rejected() -> None:
    service, _ = build_service()
    first = make_revision()
    second = replace(
        first,
        source_article_identity=SourceArticleIdentity(
            IDENTITY.canonical_source_identifier,
            IDENTITY.normalization_version,
            canonical_url="https://example.com/canonical/123",
        ),
    )
    service.execute(PersistArticleRevisionCommand(make_metadata(), first))

    with pytest.raises(GeniError) as exc:
        service.execute(PersistArticleRevisionCommand(make_metadata(), second))

    assert exc.value.code is ErrorCode.IDEMPOTENCY_KEY_REUSE_CONFLICT


def test_interrupt_during_append_rolls_back_the_unit_of_work() -> None:
    class InterruptedRevisions(FakeArticleRevisionRepository):
        def append_revision(
            self,
            article_id: str,
            revision: PersistArticleRevision,
            expected_article_version: str | None,
            uow: FakeUnitOfWork,
        ) -> ArticleRevisionRecord:
            raise KeyboardInterrupt

    service, deps = build_service(revisions=InterruptedRevisions())

    with pytest.raises(KeyboardInterrupt):
        service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))

    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items[0].rolled_back
    assert not factory.items[0].committed


def test_addressed_article_without_aggregate_version_is_an_invariant_violation() -> None:
    articles = FakeArticleRepository()
    revisions = FakeArticleRevisionRepository()
    service, _ = build_service(articles=articles, revisions=revisions)
    created = service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))
    articles.items[created.article_id] = replace(
        articles.items[created.article_id], aggregate_version=None
    )
    changed = make_revision("Central bank cuts rates")
    metadata = replace(
        make_metadata(created.article_version),
        command_id="command-2",
        idempotency_key="request-2",
    )

    with pytest.raises(GeniError) as exc:
        service.execute(
            PersistArticleRevisionCommand(metadata, changed, article_id=created.article_id)
        )

    assert exc.value.code is ErrorCode.INVARIANT_VIOLATION
    assert revisions.append_calls == 1


def test_rights_are_evaluated_at_trusted_clock_not_source_observation_time() -> None:
    revision = make_revision()
    rights = FakeContentRights()
    service, _ = build_service(rights=rights)

    service.execute(PersistArticleRevisionCommand(make_metadata(), revision))

    assert rights.metadata_calls[0][1] == datetime(2026, 11, 27, 9, 0, tzinfo=UTC)
    assert rights.metadata_calls[0][1] != revision.observed_at


def test_non_semantic_url_and_external_id_changes_refresh_projection_without_revision() -> None:
    articles = FakeArticleRepository()
    revisions = FakeArticleRevisionRepository()
    original = make_revision()
    record = ArticleRevisionRecord(
        revision_id="revision-existing",
        article_id="article-existing",
        revision_number=1,
        payload=original,
        revision_fingerprint=original.revision_fingerprint,
        revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        created_at=NOW,
    )
    revisions.current["article-existing"] = record
    articles.items["article-existing"] = ArticleProjection(
        article_id="article-existing",
        source_id=original.source_id,
        source_article_identity=original.source_article_identity,
        url=original.original_url,
        canonical_url=original.source_article_identity.canonical_url,
        external_id=original.external_id,
        title=original.normalized_title,
        content_availability=original.content_availability,
        content_reference=original.content_reference,
        content_hash=original.content_hash,
        content_normalization_version=original.content_normalization_version,
        summary=original.summary,
        author=original.author,
        language=original.language,
        published_at=original.published_at,
        current_revision_id=record.revision_id,
        metadata={},
        aggregate_version="article-version-4",
        created_at=NOW,
        updated_at=NOW,
    )
    changed_identity = SourceArticleIdentity(
        IDENTITY.canonical_source_identifier,
        IDENTITY.normalization_version,
        canonical_url="https://example.com/canonical/123",
    )
    changed = replace(
        original,
        source_article_identity=changed_identity,
        original_url="https://example.com/new-path/123",
        external_id="publisher-123-new",
    )
    service, _ = build_service(articles=articles, revisions=revisions)

    result = service.execute(
        PersistArticleRevisionCommand(
            make_metadata("article-version-4"),
            changed,
            article_id="article-existing",
        )
    )

    saved = articles.items["article-existing"]
    assert result.revision_id == "revision-existing"
    assert not result.created
    assert saved.url == changed.original_url
    assert saved.external_id == changed.external_id
    assert saved.canonical_url == changed_identity.canonical_url
    assert saved.current_revision_id == "revision-existing"
    assert saved.aggregate_version == "article-version-5"
    assert revisions.append_calls == 0
    assert articles.save_calls == 1


def test_naive_trusted_clock_fails_before_transaction_start() -> None:
    class NaiveClock:
        def now(self) -> datetime:
            return datetime(2026, 11, 27, 9, 0)

    service, deps = build_service(clock=NaiveClock())

    with pytest.raises(ValueError, match="timezone-aware"):
        service.execute(PersistArticleRevisionCommand(make_metadata(), make_revision()))

    factory = deps["uow_factory"]
    assert isinstance(factory, FakeUnitOfWorkFactory)
    assert factory.items == []

def test_source_identity_authorization_reference_is_unambiguous() -> None:
    first_revision = replace(
        make_revision(),
        source_id="a:b",
        source_article_identity=SourceArticleIdentity("d", "c"),
    )
    second_revision = replace(
        make_revision(),
        source_id="a",
        source_article_identity=SourceArticleIdentity("d", "b:c"),
    )
    first = PersistArticleRevisionCommand(make_metadata(), first_revision)
    second = PersistArticleRevisionCommand(make_metadata(), second_revision)

    first_reference = ArticleRevisionService._resource_reference(first)
    second_reference = ArticleRevisionService._resource_reference(second)

    assert first_reference == 'source-article:v1:["a:b","c","d"]'
    assert second_reference == 'source-article:v1:["a","b:c","d"]'
    assert first_reference != second_reference
