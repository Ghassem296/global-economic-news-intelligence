# GENI-TAX-011 — Economic Taxonomy Specification

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-TAX-011  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

---

## 1. Purpose and Scope

Defines governance and representation rules for GENI's economic subject taxonomy and formalizes the seven initial subject areas in Document 01. It does not claim the detailed vocabulary or every classification rule is approved. Taxonomy classifies subject matter; it is not event importance, source credibility, economic relevance, causal attribution, or market-impact forecast.

## 2. Design Principles

1. Every concept has a stable machine-readable ID independent of display labels.
2. Each has preferred labels per supported language, synonyms, and definition.
3. Parent-child relations form an acyclic hierarchy; other relations are typed.
4. Multi-label classification is allowed when several subjects are materially relevant.
5. Unknown, unclassified, not applicable, and insufficient evidence remain distinct.
6. Historical classifications retain the taxonomy version used.
7. LLMs propose labels only; deterministic validation checks ID existence and version validity.

## 3. Proposed Initial Top-Level Vocabulary

| Proposed ID | Preferred label | Scope |
|---|---|---|
| GENI.TOPIC.MONETARY_POLICY | Monetary Policy | Central-bank decisions, rates, balance sheets, guidance, transmission |
| GENI.TOPIC.FINANCIAL_MARKETS | Financial Markets | Equity, bond, FX, credit, derivatives, liquidity, market structure |
| GENI.TOPIC.MACROECONOMICS | Macroeconomics | Inflation, output, employment, productivity, growth, indicators |
| GENI.TOPIC.TRADE_INDUSTRY | Trade and Industry | Trade, supply chains, manufacturing, industrial policy, business activity |
| GENI.TOPIC.ENERGY_NATURAL_RESOURCES | Energy and Natural Resources | Oil, gas, electricity, renewables, minerals, resource supply/demand |
| GENI.TOPIC.FISCAL_PUBLIC_DEBT | Fiscal Policy and Public Debt | Taxation, spending, budgets, deficits, sovereign debt |
| GENI.TOPIC.GEOPOLITICAL_ECONOMIC_RISK | Geopolitical Economic Risk | Geopolitical events with material trade, financial, energy, sanctions, or macro channels |

These IDs are proposed canonical identifiers, not evidence of a deployed taxonomy. Review them before production persistence.

## 4. Concept and Classification Rules

A concept record contains ID, namespace/version, preferred label/definition, language labels/synonyms, parent IDs and typed relations, scope/inclusion/exclusion notes, lifecycle status, effective dates, replacement reference, and change provenance.

IDs are never reused for another concept. Editorial label correction does not require a new ID if meaning is unchanged. Semantic split/merge requires explicit mapping and migration rules.

Assign a concept only when content supports its definition. Prefer the narrowest supported concept while retaining broader roll-up. Do not infer topic solely from a named country/person/organization/instrument. Use UNCLASSIFIED when no concept fits; use INSUFFICIENT_INFORMATION when evidence is inadequate. Preserve method, model/prompt version, confidence semantics, taxonomy version, and supporting evidence. Uncalibrated model confidence is not probability.

## 5. Hierarchy, Versioning, and Governance

Add child concepts only when useful for search, analysis, reporting, or evaluation; do not create a category for every entity or keyword. Taxonomy releases are immutable and versioned. Changes are editorial, additive, deprecation, semantic change, or split/merge. Semantic changes and split/merge require migration maps, compatibility analysis, regression evaluation, and approval. Historical results remain reproducible; reclassification creates a new versioned result and preserves the old one.

The Project Owner is the proposed approval authority. Change requests state problem, ID/definition, parent relation, examples/counterexamples, affected reports/queries, migration impact, and evaluation cases. No used concept may be silently renamed, repurposed, or deleted. Canonical artifact format and language set remain open.

## 6. Distinction from Other Assessments

Taxonomy answers “what subject area is this about?” Event Importance measures significance/attention; Economic Relevance measures the nature/strength of economic connection; Economic Impact assesses observed/estimated effects; Claim Assessment evaluates evidence. Topic labels must not substitute for these dimensions.

## 7. Evaluation and Acceptance

The reference set includes boundary cases, multi-topic events, geopolitical stories with/without economic relevance, and ambiguous/insufficient cases. Evaluate per-label precision/recall, macro/micro aggregates, multi-label performance, hierarchy consistency, unknown handling, and version regression; report class imbalance and annotation disagreement.

Ready for implementation when IDs, definitions, hierarchy, unknown states, versioning, and approval workflow are accepted; a reviewed initial release exists; and tests target that release. Section 3 remains proposed until review.

## 8. Related Documents

Documents 01, 02, 03, and 12; GENI-ADR-003, 018, and 019.

---

**Document ID:** GENI-TAX-011  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**End of Document**
