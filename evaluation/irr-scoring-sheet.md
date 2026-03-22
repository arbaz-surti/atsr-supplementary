# Independent Reviewer Scoring Sheet
## AI-Assisted Test Scope Recommender (ATSR) — Evaluation Study

---

## Thank You for Participating

You are helping validate an AI-assisted test scope recommendation framework called **ATSR** (AI-Assisted Test Scope Recommender). Your independent scores will be used to calculate **inter-rater reliability** — a standard academic measure of how consistently two evaluators assess the same material.

**Your scores will not be compared to a right/wrong answer.** They will be compared to the primary evaluator's scores to quantify agreement. Both sets of scores carry equal weight.

**Time estimate:** 45–90 minutes for all 6 specs. There is no deadline pressure — accuracy matters more than speed.

---

## What You Are Evaluating

For each of the 6 feature specifications below, you will be shown:

1. **The feature specification** — a description of a software change or new feature (anonymized where needed)
2. **The AI-generated test scope recommendation** — what the ATSR system recommended as the test plan for that feature

Your job is to **score the AI's recommendation**, not to write your own. You are acting as a quality assessor: how good is the recommendation the AI produced?

---

## The Rubric — Five Dimensions

Score each dimension on a **1 to 5 scale** using the anchors below.

---

### Dimension 1 — Completeness (C)
*Are all relevant test types covered? Does the recommendation account for all areas that should be tested given the change?*

| Score | Meaning |
|---|---|
| 5 | All relevant test types identified; nothing important is missing |
| 4 | Mostly complete; one minor gap |
| 3 | Adequate; covers the core but misses some secondary areas |
| 2 | Incomplete; misses at least one important test area |
| 1 | Substantially incomplete; major test areas absent |

---

### Dimension 2 — Specificity (S)
*Are the test descriptions concrete and actionable? Could a QA engineer act on these without asking follow-up questions?*

| Score | Meaning |
|---|---|
| 5 | Highly specific; test cases are precise, describe clear actions and expected outcomes |
| 4 | Mostly specific; minor vagueness in a few items |
| 3 | Moderately specific; some items could be more concrete |
| 2 | Vague; many items are generic and would require significant interpretation |
| 1 | Too generic to act on; reads like a template |

---

### Dimension 3 — Risk Calibration (R)
*Is the recommended coverage depth appropriate for the nature and risk of the change?*

**Coverage depth options: LOW / MEDIUM / HIGH**

| Depth | Typical change types |
|---|---|
| LOW | Bug fix with narrow scope, config value change, vendor patch |
| MEDIUM | Enhancement, security configuration, infrastructure change |
| HIGH | New feature, integration with multiple systems, broad regression |

| Score | Meaning |
|---|---|
| 5 | Depth is exactly right for the change type and risk level |
| 4 | Depth is correct; justification is mostly sound |
| 3 | Depth is defensible but could reasonably be argued one level up or down |
| 2 | Depth is one level off from what is appropriate |
| 1 | Depth is clearly wrong (e.g., LOW for a broad new feature) |

**Important:** For this dimension, please also write your own depth judgment (LOW / MEDIUM / HIGH) in the scoring form, independent of what the AI recommended.

---

### Dimension 4 — Integration Awareness (I)
*Are cross-system touchpoints and downstream dependencies identified?*

| Score | Meaning |
|---|---|
| 5 | All relevant integrations and downstream systems named; impact on each addressed |
| 4 | Most integrations covered; one touchpoint missed |
| 3 | Key integrations present; some secondary dependencies overlooked |
| 2 | Thin coverage; only surface-level integration checks |
| 1 | Integration considerations absent or incorrect |

---

### Dimension 5 — Clarification Flag Quality (F)
*Are the flagged gaps and open questions useful and actionable? Would these flags materially change how a QA engineer designs the test plan if answered?*

| Score | Meaning |
|---|---|
| 5 | All flags are targeted and relevant; if answered, they would change test design |
| 4 | Mostly useful flags; one is generic or low-value |
| 3 | Mixed; some useful, some generic or obvious |
| 2 | Mostly generic; flags add little value beyond the spec itself |
| 1 | No useful flags; entirely boilerplate or inapplicable |

---

## How to Record Your Scores

For each spec, complete the **Scoring Form** at the bottom of that spec's section. You can:

- **Print this document** and fill in scores by hand
- **Type directly into this document** if working digitally
- **Copy the scoring tables** into a separate spreadsheet or email

Return your completed form to the study author when finished.

---
---

# SPEC-01 — Menu Item Sync Bug: Online Portal Shows Available After POS Update

## Feature Specification

**Change Type:** Bug fix / Integration patch

**System Area:** POS to online ordering platform integration (menu sync)

**Description:**
When a menu item is marked as "Out of Stock" on the point-of-sale (POS) system, the system is expected to propagate this status to the online ordering portal after a configured sync interval. However, even after leaving the system overnight to complete a full menu sync cycle, the item continues to appear as available in the online portal. Customers who attempt to add the item to their cart receive an error message at checkout rather than seeing the item correctly flagged as unavailable.

**Acceptance Criteria:**
- The item should display Out of Stock status on the POS immediately after being marked as such.
- The item should not be orderable on the online web and mobile ordering apps after being marked out of stock.
- After the Out of Stock flag is removed and saved, the item should become visible and orderable again on both POS and online ordering apps.

---

## AI-Generated Test Scope Recommendation

**Coverage Depth Recommended:** MEDIUM

**Justification:** The change is a bug fix in a critical integration area affecting customer experience, requiring thorough validation of the sync process and its impact on item availability.

**Effort Estimate:** 10–15 test cases

**Functional Tests:**
1. Verify that marking an item as Out of Stock on the POS immediately updates its status on the POS.
2. Check that an item marked as Out of Stock on the POS is not orderable on the online web ordering app after the sync.
3. Check that an item marked as Out of Stock on the POS is not orderable on the mobile ordering app after the sync.
4. Verify that removing the Out of Stock flag on the POS makes the item visible and orderable on the online web ordering app.
5. Verify that removing the Out of Stock flag on the POS makes the item visible and orderable on the mobile ordering app.

**Smoke Tests:**
1. Verify that other menu items not marked as Out of Stock remain orderable on the online ordering platform.
2. Check that the online ordering platform is accessible and functional after the sync process.

**Regression Tests:**
1. Test that the menu sync process does not affect the pricing of items on the online ordering platform.
2. Verify that the sync process does not alter item descriptions on the online ordering platform.
3. Ensure that the sync process does not affect the availability of items that are in stock.

**Integration Tests:**
1. Validate the end-to-end data flow from the POS to the online ordering platform for an item marked as Out of Stock.
2. Test the data flow when the Out of Stock status is removed, ensuring the item becomes available again on the online platform.

**Exploratory Tests:**
1. Test the behavior when multiple items are marked as Out of Stock simultaneously and verify their status on the online platform.
2. Check the system's behavior if the sync interval is manually triggered multiple times in quick succession.

**Clarification Flags:**
1. Clarify the exact sync interval and whether it can be manually triggered for testing purposes.
2. Confirm if there are any known limitations or conditions under which the sync might fail or be delayed.
3. Verify if there are any differences in behavior between the web and mobile ordering platforms that need specific attention.

---

## Scoring Form — SPEC-01

| Dimension | Your Score (1–5) | Notes (optional) |
|---|---|---|
| **C** — Completeness | | |
| **S** — Specificity | | |
| **R** — Risk Calibration | | |
| **I** — Integration Awareness | | |
| **F** — Clarification Flag Quality | | |
| **Total** | **/25** | |

**Your independent depth judgment:** ☐ LOW  ☐ MEDIUM  ☐ HIGH

---
---

# SPEC-02 — Payment Device Firmware Update: Quick Chip Reconnection Fix

## Feature Specification

**Change Type:** Patch (vendor-delivered firmware fix)

**System Area:** Payment processing / POS to payment terminal integration

**Description:**
A vendor has delivered a new firmware version for the payment processing component to fix a known quick chip match error. The issue occurs when the network cable is unplugged from the payment device mid-transaction: the transaction fails with a communication error. When the cable is reconnected and a new transaction is attempted, the firmware is unable to re-establish the connection, causing continued failure. The new firmware should resolve the reconnection issue. Testing should be performed across 6 device/POS version combinations: POS v18 and v19, each paired with terminal models A, B, and C.

**Acceptance Criteria:** None specified in the ticket.

---

## AI-Generated Test Scope Recommendation

**Coverage Depth Recommended:** LOW

**Justification:** The change is a vendor-delivered patch fix specifically targeting a reconnection issue, requiring focused testing on the reconnection scenario.

**Effort Estimate:** 12–18 test cases

**Functional Tests:**
1. Verify that a transaction can be completed successfully after the network cable is reconnected for POS v18 with terminal model A.
2. Verify that a transaction can be completed successfully after the network cable is reconnected for POS v18 with terminal model B.
3. Verify that a transaction can be completed successfully after the network cable is reconnected for POS v18 with terminal model C.
4. Verify that a transaction can be completed successfully after the network cable is reconnected for POS v19 with terminal model A.
5. Verify that a transaction can be completed successfully after the network cable is reconnected for POS v19 with terminal model B.
6. Verify that a transaction can be completed successfully after the network cable is reconnected for POS v19 with terminal model C.

**Smoke Tests:**
1. Perform a basic transaction without network interruption to ensure general transaction processing is unaffected for POS v18 and terminal model A.
2. Perform a basic transaction without network interruption to ensure general transaction processing is unaffected for POS v19 and terminal model B.

**Regression Tests:**
1. Test a complete transaction flow without any network interruption for all POS and terminal combinations to ensure no regression in standard transaction processing.
2. Verify that the system logs appropriate error messages when the network cable is unplugged mid-transaction.

**Integration Tests:**
1. Validate end-to-end transaction processing from POS to payment terminal to backend systems for each POS and terminal combination after reconnection.

**Exploratory Tests:**
1. Test the behavior when the network cable is unplugged and reconnected multiple times during a transaction.
2. Test the behavior when the network cable is unplugged for an extended period before being reconnected.

**Clarification Flags:**
1. Confirm if there are any additional configurations or settings that need to be adjusted on the POS or terminal devices before testing the new firmware.
2. Clarify if there are any specific logging or monitoring requirements during the testing process to capture the reconnection behavior.

---

## Scoring Form — SPEC-02

| Dimension | Your Score (1–5) | Notes (optional) |
|---|---|---|
| **C** — Completeness | | |
| **S** — Specificity | | |
| **R** — Risk Calibration | | |
| **I** — Integration Awareness | | |
| **F** — Clarification Flag Quality | | |
| **Total** | **/25** | |

**Your independent depth judgment:** ☐ LOW  ☐ MEDIUM  ☐ HIGH

---
---

# SPEC-05 — New Extra-Large Beverage Size Addition to Menu

## Feature Specification

**Change Type:** New feature (menu item / size tier addition)

**System Area:** Menu configuration, POS ordering, pricing engine

**Description:**
A new extra-large size tier is being introduced for iced coffee, iced latte, and refreshers (standard varieties). Seasonal hero build variants are also being added for specific items. The new size introduces a new tier in threshold pricing with a default modifier count of 6. It should price and appear as 2x the medium beverage price. No suggested retail price is applied to the default modifier build. All modifications remain available.

**Acceptance Criteria:** None specified in the ticket.

---

## AI-Generated Test Scope Recommendation

**Coverage Depth Recommended:** HIGH

**Justification:** The change involves a new feature addition affecting multiple system areas including menu configuration, POS ordering, and pricing, which are critical to business operations.

**Effort Estimate:** 15–25 test cases

**Functional Tests:**
1. Verify that the extra-large size option is available for iced coffee, iced latte, and refreshers in the POS menu.
2. Check that the extra-large size is priced at 2x the medium beverage price for each applicable item.
3. Ensure that the default modifier count is set to 6 for the extra-large size.
4. Validate that all existing modifications are available for the extra-large size.
5. Confirm that seasonal hero build variants are correctly added and displayed for specific items.

**Smoke Tests:**
1. Verify that the POS system is operational and can process orders with the new extra-large size.
2. Check that the menu displays correctly on customer-facing screens with the new size tier.

**Regression Tests:**
1. Test existing size options (small, medium, large) to ensure they are unaffected by the new size addition.
2. Verify that the pricing engine correctly calculates prices for all existing sizes and modifications.
3. Ensure that the order processing flow remains intact for all beverage sizes.

**Integration Tests:**
1. Validate that the pricing engine correctly integrates with the POS system to apply the new pricing tier.
2. Check that the menu configuration updates are correctly reflected in any integrated mobile ordering apps.

**Exploratory Tests:**
1. Test edge cases where multiple modifiers are added to the extra-large size to ensure pricing is accurate.
2. Probe scenarios where the extra-large size is combined with seasonal promotions or discounts.

**Clarification Flags:**
1. Clarify if there are any specific seasonal hero build variants that need additional testing.
2. Confirm if there are any specific promotions or discounts that should be tested with the new size.
3. Verify if there are any regional variations in pricing or availability for the extra-large size.

---

## Scoring Form — SPEC-05

| Dimension | Your Score (1–5) | Notes (optional) |
|---|---|---|
| **C** — Completeness | | |
| **S** — Specificity | | |
| **R** — Risk Calibration | | |
| **I** — Integration Awareness | | |
| **F** — Clarification Flag Quality | | |
| **Total** | **/25** | |

**Your independent depth judgment:** ☐ LOW  ☐ MEDIUM  ☐ HIGH

---
---

# SPEC-09 — Delivery Markup Percentage Update for Third-Party Delivery Platform

## Feature Specification

**Change Type:** Configuration change (percentage value update)

**System Area:** Reporting/analytics configuration, third-party delivery platform, data pipeline

**Description:**
A delivery markup percentage value needs to be updated in the reporting and analytics configuration tool (under Data Mapping settings). The change affects a single third-party delivery platform. Testing is required across multiple environments (dev, UAT, production). The primary concern is that the updated markup is correctly reflected in sales reports and that other delivery platforms are not impacted. There is also a question of whether the change applies retroactively to prior transactions.

**Acceptance Criteria:** None specified in the ticket.

---

## AI-Generated Test Scope Recommendation

**Coverage Depth Recommended:** LOW

**Justification:** The change is a configuration update with a limited scope affecting a specific percentage value.

**Effort Estimate:** 8–12 test cases

**Functional Tests:**
1. Verify that the delivery markup percentage is updated to the new value in the reporting and analytics configuration tool under Data Mapping settings.
2. Check that the updated markup percentage is applied to new transactions for the specified third-party delivery platform.
3. Validate that the change is correctly reflected in reports generated after the effective date.

**Smoke Tests:**
1. Ensure that other delivery platforms' markup percentages remain unchanged.
2. Quickly verify that the reporting and analytics tool is operational after the configuration change.

**Regression Tests:**
1. Test existing reports to ensure they still generate correctly with the new markup percentage.
2. Verify that historical data for the affected delivery platform remains unchanged unless specified otherwise.

**Integration Tests:**
1. Validate the data flow from the reporting and analytics tool to the third-party delivery platform to ensure the new markup is applied correctly.
2. Check if the third-party reporting platform reflects the updated markup percentage, if applicable.

**Exploratory Tests:**
1. Investigate how the system handles transactions that span the effective date of the markup change.
2. Probe for any discrepancies in the markup application for edge cases, such as refunds or partial deliveries.

**Clarification Flags:**
1. Confirm whether the markup change applies retroactively to prior transactions or only to new transactions.
2. Clarify if any changes are required on the third-party reporting platform and if coordination is needed.

---

## Scoring Form — SPEC-09

| Dimension | Your Score (1–5) | Notes (optional) |
|---|---|---|
| **C** — Completeness | | |
| **S** — Specificity | | |
| **R** — Risk Calibration | | |
| **I** — Integration Awareness | | |
| **F** — Clarification Flag Quality | | |
| **Total** | **/25** | |

**Your independent depth judgment:** ☐ LOW  ☐ MEDIUM  ☐ HIGH

---
---

# SPEC-16 — Regression Testing After New Promotional BIN Ranges Added

## Feature Specification

**Change Type:** Regression task (new content records added; validate no interference with existing functionality)

**System Area:** Coupon and discount processing, POS, content management system

**Description:**
New promotional BIN (Bank Identification Number) ranges have been added to the system's content management platform. BIN ranges are used to identify and apply specific coupon and discount types at the point of sale. The concern is that adding new BIN ranges could interfere with existing serialized coupons and discount configurations already in the system. Testing is required to confirm that existing coupon and discount behavior is unaffected by the new additions.

**Acceptance Criteria:** None specified in the ticket.

---

## AI-Generated Test Scope Recommendation

**Coverage Depth Recommended:** MEDIUM

**Justification:** The focus is on ensuring enhancements (new BIN ranges) do not disrupt existing functionality, which aligns with medium coverage depth.

**Effort Estimate:** 10–20 test cases

**Functional Tests:**
1. Verify existing serialized coupons apply correct discounts at POS.
2. Validate that existing discounts are correctly processed in the content management system.
3. Check that existing BIN ranges are not altered in the content management system.

**Smoke Tests:**
1. Ensure the POS system is operational after new BIN ranges are added.
2. Verify that the content management system is accessible and responsive.

**Regression Tests:**
1. Test a sample of existing serialized coupons to ensure they still apply correctly.
2. Perform end-to-end testing of discount application from content management to POS.
3. Validate that no errors occur when processing transactions with existing coupons.

**Integration Tests:**
1. Confirm that the integration between the content management system and POS is unaffected by the new BIN ranges.
2. Test the data flow from the content management system to the POS for existing coupons.

**Exploratory Tests:**
1. Explore edge cases where multiple coupons and discounts are applied simultaneously.
2. Investigate any unusual behavior in the content management system related to coupon processing.

**Clarification Flags:**
1. Confirm the exact number of existing serialized coupons to be tested.
2. Clarify the timeline for regression testing completion relative to the go-live date.

---

## Scoring Form — SPEC-16

| Dimension | Your Score (1–5) | Notes (optional) |
|---|---|---|
| **C** — Completeness | | |
| **S** — Specificity | | |
| **R** — Risk Calibration | | |
| **I** — Integration Awareness | | |
| **F** — Clarification Flag Quality | | |
| **Total** | **/25** | |

**Your independent depth judgment:** ☐ LOW  ☐ MEDIUM  ☐ HIGH

---
---

# SPEC-18 — POS Crew Notification Feature Enablement

## Feature Specification

**Change Type:** New feature (POS notification scheduling and display system)

**System Area:** POS workstation, employee clock-in workflow, notification management

**Description:**
A new crew notification feature is being enabled on POS workstations. The feature allows store owners and managers to schedule custom notifications (e.g., promotions, policy changes, shift reminders) to appear on the POS workstation screen when a crew member clocks in. Notifications can be customized for content type and scheduled for specific dates and times. The feature needs to be validated from both the manager-facing scheduling side and the crew-facing display side, and the existing clock-in workflow must not be disrupted.

**Acceptance Criteria:** None specified in the ticket.

---

## AI-Generated Test Scope Recommendation

**Coverage Depth Recommended:** HIGH

**Justification:** The change involves a new feature that affects core POS workstation functionality and employee workflows.

**Effort Estimate:** 20–30 test cases

**Functional Tests:**
1. Verify that notifications can be scheduled by store owners and managers.
2. Check that notifications appear on the POS workstation screen when a crew member clocks in.
3. Ensure notifications can be customized for different types of messages (promotions, policy changes, etc.).
4. Test the ability to schedule notifications for specific dates and times.
5. Validate that notifications are displayed correctly across different POS workstation models.

**Smoke Tests:**
1. Confirm that the POS workstation operates normally after the feature is enabled.
2. Verify that the clock-in process is not disrupted by the new notification feature.

**Regression Tests:**
1. Test existing clock-in workflows to ensure they are unaffected.
2. Check that existing POS functionalities (e.g., transaction processing, receipt printing) remain operational.
3. Validate that the notification management system does not interfere with existing POS system settings.

**Integration Tests:**
1. Verify integration between the POS notification system and the employee clock-in system.
2. Test data flow from the notification management system to the POS workstations.
3. Ensure that notifications are correctly synchronized across multiple POS workstations in the same store.

**Exploratory Tests:**
1. Test the behavior of the notification system when multiple crew members clock in simultaneously.
2. Check how the system handles overlapping notifications scheduled for the same time.
3. Explore the system's response to invalid or corrupted notification data.

**Clarification Flags:**
1. Clarification needed on how notifications are managed and stored in the system.
2. Information needed on any user permissions or roles required to schedule notifications.
3. Clarification on whether notifications can be dismissed or snoozed by crew members.

---

## Scoring Form — SPEC-18

| Dimension | Your Score (1–5) | Notes (optional) |
|---|---|---|
| **C** — Completeness | | |
| **S** — Specificity | | |
| **R** — Risk Calibration | | |
| **I** — Integration Awareness | | |
| **F** — Clarification Flag Quality | | |
| **Total** | **/25** | |

**Your independent depth judgment:** ☐ LOW  ☐ MEDIUM  ☐ HIGH

---
---

# Summary Score Sheet

*Copy your totals here once all 6 specs are scored.*

| Spec | C | S | R | I | F | Total /25 | Your Depth | AI Depth |
|---|---|---|---|---|---|---|---|---|
| SPEC-01 — Menu Sync Bug | | | | | | | | MEDIUM |
| SPEC-02 — Firmware Patch | | | | | | | | LOW |
| SPEC-05 — New Beverage Size | | | | | | | | HIGH |
| SPEC-09 — Markup Config Change | | | | | | | | LOW |
| SPEC-16 — BIN Range Regression | | | | | | | | MEDIUM |
| SPEC-18 — Crew Notification Feature | | | | | | | | HIGH |
| **Grand Total** | | | | | | **/150** | | |

---

*Thank you. Please return this completed sheet to the study author.*
*For questions about any spec or dimension, feel free to ask before scoring — clarifying questions are expected and will not influence the results.*
