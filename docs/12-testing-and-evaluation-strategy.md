# GENI-EVAL-012 — Testing and Evaluation Strategy

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-EVAL-012  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

---

## 1. Purpose

Defines reproducible verification and evaluation. It connects architecture invariants, workflow contracts, AI task quality, operational reliability, and release decisions; complements Document 04 and GENI-ADR-017. Passing unit tests does not prove analytical quality. Provider success does not prove AI correctness. Report test and evaluation results separately.

## 2. Verification Layers

| Layer | Purpose | Evidence |
|---|---|---|
| Static/schema | Document, schema, configuration checks | CI/schema results |
| Unit/domain | Pure rules, invariants, state transitions | Deterministic tests |
| Repository/contract | Persistence and interface semantics | Contract suite |
| Integration | Components, providers, transactions | Integration results |
| End-to-end | Acquisition-to-report workflows | Traceable scenarios |
| Security | Trust boundaries and abuse controls | Threat-linked results |
| Reliability | Retry, idempotency, recovery | Fault-injection evidence |
| AI evaluation | Classification, extraction, matching, assessment, report quality | Versioned datasets/rubrics |
| Operational acceptance | Deployment, backup, monitoring, runbooks | Release checklist/exercises |

## 3. Dataset Governance

Each dataset has immutable ID/version, purpose, scope, inclusion/exclusion rules, provenance, rights basis, annotation schema, split, and change history.

Cases cover monetary policy, inflation, labor, growth, fiscal policy, debt, trade, energy, financial markets, geopolitical risks with/without economic channels, conflicting reports, exact/near duplicates, syndication, multi-event articles, multiple articles per event, related-but-distinct/ambiguous matches, corrections/retractions, multilingual content, rights-denied/expired/revoked content, provider timeouts, malformed responses, and partial failures.

Annotation instructions define unit, evidence, labels, unknown handling, adjudication, and inter-annotator agreement. High-impact labels require human review. Dataset rights must permit intended use. Group related articles/events into the same split where needed to prevent duplicate leakage.

## 4. Metric Definitions

Every metric report defines numerator, denominator, unit, inclusion criteria, aggregation, dataset version, and uncertainty treatment where appropriate.

| Metric | Definition | Failure exposed |
|---|---|---|
| Event Matching Precision | Correct accepted matches / all accepted matches | False associations |
| Event Matching Recall | Correct accepted matches / reference-positive opportunities | Missed associations |
| False Merge Rate | Incorrect merges / evaluated merge operations; also report count/severity | Distinct events conflated |
| Duplicate Delivery Rate | Duplicate deliveries / logical delivery operations | Repeated side effects |
| Unsupported Material Assertion Rate | Material assertions lacking sufficient support / evaluated material assertions | Unsupported reporting |
| Evidence Provenance Completeness | Valid required provenance links/fields / required provenance items | Untraceable claims |
| False Causal Attribution Rate | Causal claims exceeding evidence support / evaluated causal claims | Overstated causality |
| Taxonomy Macro/Micro F1 | Per-label and aggregate F1 under declared multi-label protocol | Classification weakness |
| Source Independence Error | Incorrect origin assessments / reviewed origin assessments | Corroboration double-counting |
| Recovery Success Rate | Recoverable injected failures restored consistently / recovery cases | Incomplete recovery |

Metric names alone are insufficient. If denominator is zero, report N/A, not zero. Define formula before using results for release decisions.

## 5. AI Evaluation Protocol

For each task record task ID, dataset/case version, expected schema, model/provider/version, prompt/template/config versions, output reference/hash, evaluator version, human-review status, token/cost provenance, latency, retry, and fallback metadata.

Evaluate schema validity and semantic quality separately. Valid structure may still be factually wrong. Use task-specific rubrics and human adjudication for material claims. Model self-confidence is not calibrated probability. Model/prompt/retrieval/taxonomy/rubric changes trigger regression suites against the same held-out cases; disclose changed conditions.

## 6. Reliability and Security Tests

Test duplicate replay, concurrent stale writes, rollback, worker restart, partial batch completion, timeout with unknown external outcome, rate limits, provider outage, rights revocation, and deletion propagation. Security tests map to Document 08. Use safe test targets for external effects.

## 7. Thresholds and Release Gates

No universal numeric threshold is asserted. Set thresholds only after baseline measurement on representative reviewed datasets and according to false-positive/false-negative costs.

Each gate defines metric/formula, dataset/version, acceptable result and rationale, sample size/uncertainty, severity-based blockers, exception authority, and regression comparison. Critical invariants—unauthorized publication, unsupported rights use, duplicate side effects, lost immutable history, invalid event identity operations—block release regardless of aggregate model score.

## 8. Evaluation Artifacts and Reporting

Evaluation runs/results are versioned artifacts outside production business tables, consistent with GENI-ADR-017. Preserve dataset/case refs, model/prompt versions, metrics/rubric, evaluator provenance, output hashes/refs, and quality/cost/latency. Protect artifacts under source rights and data classification.

Reports disclose composition, exclusions, missing labels, annotation disagreement, sample size, uncertainty, and limitations. Do not compare materially different datasets as equivalent.

## 9. Acceptance Criteria

Ready for release use when critical tasks have reviewed datasets/rubrics; metric formulas/denominators are versioned; baselines are reproducible; regression gates map to change types; and exceptions are auditable. Until then, quality claims remain qualitative and limited.

## 10. Related Documents

Documents 04, 08, 10, and 11; GENI-ADR-008, 011, 017, and 019.

---

**Document ID:** GENI-EVAL-012  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**End of Document**
