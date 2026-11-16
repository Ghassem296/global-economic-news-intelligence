# Architecture Decision Record (ADR) Template

**Project:** Global Economic News Intelligence
**ADR ID:** GENI-ADR-NNN
**Title:** [Short and Descriptive Decision Title]
**Status:** Proposed
**Version:** 1.0
**Date:** YYYY-MM-DD
**Decision Owner:** Product Owner
**Prepared By:** AI Architecture Assistant
**Approved By:** Not yet approved
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Describe the architectural problem, requirement, or situation that requires a decision.

Explain:

- What problem are we trying to solve?
- Why is this decision necessary?
- What triggered the need for this decision?
- What happens if no decision is made?
- What existing architectural assumptions or constraints must be considered?
- Which product capabilities or implementation stages depend on this decision?

The context should describe the problem without prematurely assuming a particular solution.

## 2. Decision Question

State the exact question that needs to be answered.

The question should be:

- Specific.
- Unambiguous.
- Answerable through an architectural decision.
- Limited to a clearly defined scope.

Avoid combining unrelated decisions into a single ADR.

## 3. Requirements and Constraints

List the relevant requirements and constraints.

### 3.1 Functional Requirements

- [Requirement 1]
- [Requirement 2]

### 3.2 Technical Constraints

- [Constraint 1]
- [Constraint 2]

### 3.3 Business and Product Constraints

- [Constraint 1]
- [Constraint 2]

### 3.4 Security and Privacy Constraints

- [Constraint 1]
- [Constraint 2]

### 3.5 Operational and Cost Constraints

- [Constraint 1]
- [Constraint 2]

### 3.6 Legal and Content-Rights Constraints

- [Constraint 1]
- [Constraint 2]

### 3.7 Explicit Non-Goals

List concerns that are intentionally outside the scope of this decision.

- [Non-goal 1]
- [Non-goal 2]

## 4. Alternatives Considered

Document the realistic alternatives evaluated.

Include the existing approach or doing nothing when it is a meaningful alternative.

### 4.1 Alternative A: [Name]

**Description:**

[Explain the alternative.]

**Advantages:**

- [Advantage]

**Disadvantages:**

- [Disadvantage]

**Risks:**

- [Risk]

**Estimated Complexity:** Low / Medium / High

### 4.2 Alternative B: [Name]

**Description:**

[Explain the alternative.]

**Advantages:**

- [Advantage]

**Disadvantages:**

- [Disadvantage]

**Risks:**

- [Risk]

**Estimated Complexity:** Low / Medium / High

### 4.3 Alternative C: [Optional]

[Repeat the same structure when necessary.]

If an alternative is not considered, explain why it was excluded when that omission could materially affect the decision.

## 5. Evaluation and Comparison

Compare the alternatives using criteria relevant to this decision.

| Evaluation Criterion | Alternative A | Alternative B | Alternative C |
|---|---|---|---|
| Product Fit | | | |
| Functional Suitability | | | |
| Reliability | | | |
| Scalability | | | |
| Complexity | | | |
| Initial Cost | | | |
| Operational Cost | | | |
| Security | | | |
| Maintainability | | | |
| Flexibility | | | |
| Reversibility | | | |
| Implementation Effort | | | |

Explain:

- Which criteria are most important and why.
- Which alternatives satisfy the critical requirements.
- Which trade-offs are acceptable or unacceptable.
- Which assumptions could change the comparison.

Do not use arbitrary numerical scores without defining their meaning and evaluation method.

If reliable cost or performance estimates are unavailable, state that explicitly rather than inventing values.

## 6. Recommended Decision

**Recommended Alternative:** [Name]

Describe the recommended solution in sufficient detail to support a formal decision.

Explain:

- Why this option is preferred.
- Why the other alternatives were not selected.
- Which requirements it satisfies.
- What assumptions support the recommendation.
- What limitations remain.
- Whether the decision is reversible.
- What conditions could justify reconsidering the recommendation.

**Recommendation Prepared By:** AI Architecture Assistant

**Recommendation Date:** YYYY-MM-DD

> Important: A recommendation is not an approved decision. The decision owner must explicitly accept or reject the proposal.

## 7. Final Decision

This section records the formal outcome of the review.

**Selected Alternative:** [Name / Not selected]

**Decision Status:** Proposed / Accepted / Rejected

**Decision Owner:** Product Owner

**Approved By:** [Name or Role / Not applicable]

**Approval Date:** [YYYY-MM-DD / Not applicable]

**Decision Rationale:**

[Record the final reasoning and any differences between the recommendation and the approved decision.]

**Conditions or Restrictions:**

[Record any conditions attached to the approval.]

**Deferred Questions:**

[List questions intentionally left unresolved.]

For a Proposed ADR, the selected alternative and approval fields must remain explicitly unapproved or pending.

An ADR must not be marked Accepted merely because a recommendation has been written or reviewed.

## 8. Consequences and Trade-Offs

Describe the expected consequences of the accepted decision.

### 8.1 Positive Consequences

- [Expected benefit]
- [Expected benefit]

### 8.2 Negative Consequences

- [Expected limitation or cost]
- [Expected limitation or cost]

### 8.3 Technical Trade-Offs

[Explain the technical compromises introduced by the decision.]

### 8.4 Operational Consequences

[Explain changes to deployment, monitoring, maintenance, recovery, and operational responsibilities.]

### 8.5 Product and Business Consequences

[Explain the effects on product capabilities, user experience, delivery, and business requirements.]

### 8.6 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| [Risk 1] | Low / Medium / High | Low / Medium / High | [Mitigation] |
| [Risk 2] | Low / Medium / High | Low / Medium / High | [Mitigation] |

Do not present uncertain benefits or mitigations as guaranteed outcomes.

## 9. Impact on Architecture and Documentation

Identify the project components and documents affected by this decision.

### 9.1 Affected Components

- [Component or service]
- [Component or service]

### 9.2 Affected Data Models and Interfaces

- [Entity, repository, interface, schema, or contract]
- [Entity, repository, interface, schema, or contract]

### 9.3 Affected Documents

- [Document path and section]
- [Document path and section]

### 9.4 Related ADRs

| ADR ID | Relationship | Explanation |
|---|---|---|
| [GENI-ADR-NNN] | Depends on / Related to / Supersedes / Superseded by | [Explanation] |

If no related ADR exists, state `None identified`.

All affected documents must be reviewed after an ADR is accepted. The ADR records the decision rationale; the relevant architecture and specification documents describe the resulting design.

## 10. Implementation Implications

Describe what must change if the decision is accepted.

### 10.1 Required Implementation Work

- [Implementation task]
- [Implementation task]

### 10.2 Migration or Compatibility Requirements

[Describe data migration, backward compatibility, transition steps, or state that none are required.]

### 10.3 Dependencies

[List technical, organizational, external, or infrastructure dependencies.]

### 10.4 Implementation Sequence

[List important implementation steps in dependency order.]

### 10.5 Verification Requirements

[Describe how the implementation will be verified against the accepted decision.]

An Accepted ADR does not imply that implementation has started or completed.

## 11. Acceptance Criteria

Define observable conditions that demonstrate the decision has been implemented correctly.

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | [Measurable condition] | [Test, inspection, or operational verification] |
| AC-02 | [Measurable condition] | [Test, inspection, or operational verification] |

Acceptance criteria should be specific and testable where practical.

If implementation is not part of the current scope, state that implementation verification is deferred.

## 12. Review and Reconsideration

Define the conditions under which this decision should be reviewed.

### 12.1 Review Triggers

Examples include:

- A major change in product requirements.
- A significant change in technical constraints.
- New security, privacy, or legal requirements.
- Material changes in cost or operational complexity.
- Evidence that the selected approach does not meet its requirements.
- A new capability or dependency that changes the original trade-offs.

### 12.2 Review Schedule

**Review Date:** [YYYY-MM-DD / Not scheduled]

**Review Owner:** [Name or Role]

### 12.3 Reconsideration Conditions

[Describe specific conditions that could justify revisiting the decision.]

A review does not automatically invalidate an Accepted ADR. Any replacement decision must be documented through the ADR lifecycle.

## 13. References and Supporting Evidence

List the sources used to develop and evaluate this decision.

Examples:

- Project requirements.
- Architecture and design documents.
- Technical specifications.
- Official product or provider documentation.
- Security and legal guidance.
- Performance measurements or evaluation results.
- Relevant research or external references.

| Reference | Type | Relevance |
|---|---|---|
| [Document, URL, or source] | Internal / External / Research / Measurement | [Explanation] |

Distinguish verified evidence from assumptions, estimates, and recommendations.

## 14. Decision History

Maintain a chronological record of significant changes to this ADR.

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | YYYY-MM-DD | Proposed | Initial proposal | [Name or Role] |

Accepted decisions must not be silently rewritten. Significant changes to an accepted decision require a new ADR that references the original decision.

Minor editorial corrections that do not alter the decision may be recorded as document revisions.

---

**End of ADR Template**