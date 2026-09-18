# Synthetic Feature Specifications for ATSR Evaluation
# Generated from real POS QA tickets — all company/brand/person identifiers replaced
# For use in the paper's evaluation section only

---

## SPEC-01
**Title:** Online Ordering Portal Still Shows Menu Item as Available After Overnight Menu Sync

**Change Type:** Bug fix / Integration patch

**System Area:** POS ↔ Online ordering platform integration (menu sync)

**Description:**
When a menu item is marked as "Out of Stock" on the POS, the system is expected to propagate this status to the online ordering portal after the configured sync interval. However, even after leaving the system overnight to complete a full menu sync cycle, the item continues to appear as available in the online portal. Customers who attempt to add the item to their cart receive an error message at checkout rather than seeing the item correctly flagged as unavailable.

**Acceptance Criteria:**
- The item should display "Out of Stock" status on the POS immediately after being marked as such.
- The item should not be orderable on the online web and mobile ordering apps after being marked out of stock.
- After the "Out of Stock" flag is removed and saved, the item should become visible and orderable again on both POS and online ordering apps.

**Detail level:** High
**Actual test scope (ground truth):** Functional tests on POS status change behavior; integration tests on POS-to-portal sync; smoke test on online ordering checkout flow; regression on other menu item availability states.

---

## SPEC-02
**Title:** Payment Device Firmware Update — Quick Chip Reconnection Fix

**Change Type:** Patch (vendor-delivered firmware fix)

**System Area:** Payment processing / POS ↔ payment terminal integration

**Description:**
Vendor has delivered a new firmware version for the payment processing component to fix a known quick chip match error. The issue occurs when the network cable is unplugged from the payment device mid-transaction: the transaction fails with a communication error. When the cable is reconnected and a new transaction is attempted, the firmware is unable to re-establish the connection, causing continued failure. The new firmware should resolve the reconnection issue.

Testing should be performed across the following device/system combinations:
- POS version 18 + terminal model A
- POS version 18 + terminal model B
- POS version 18 + terminal model C
- POS version 19 + terminal model A
- POS version 19 + terminal model B
- POS version 19 + terminal model C

**Detail level:** Sparse (no acceptance criteria defined)
**Actual test scope (ground truth):** Functional tests on payment reconnection flow; matrix testing across 6 device/version combinations; smoke test on standard transaction flow post-fix.

---

## SPEC-03
**Title:** New Wi-Fi Access Point Hardware Rollout — Indoor Wi-Fi 7 Model

**Change Type:** Infrastructure / hardware replacement

**System Area:** Network infrastructure (store connectivity, line-busting, POS communication)

**Description:**
A new indoor Wi-Fi 7 access point model is being introduced to replace existing Wi-Fi 6 models. The new hardware has been installed in lab environments on both primary and secondary network templates. Testing is required across all production network types, including the line-busting tablet network.

Networks to be tested (not limited to):
- Staff/management network — test with management device
- Brand-approved device network — test with any approved device
- POS/line-busting network — test with line-busting tablet
- Guest network — test with any device

**Detail level:** Medium (no acceptance criteria; scope partially defined by network list)
**Actual test scope (ground truth):** Connectivity functional tests across all 4 network types; device-specific testing on line-busting tablet; regression on POS communication over new AP; smoke test on guest network access.

---

## SPEC-04
**Title:** New Catering Voucher Tender Key Implementation on POS

**Change Type:** New feature (new payment tender type)

**System Area:** Payment processing, POS, reporting (financial + analytics), third-party data pipeline

**Description:**
Implement a dedicated catering voucher tender key on the POS that behaves like a voucher payment while maintaining existing in-store catering order type behavior.

**In Scope:**
- Transaction experience with catering voucher tendering
- POS functionality for catering voucher tender behavior and processing
- Regression testing to confirm no adverse impact on existing POS functionality
- POS reporting for catering voucher in Property Financial, Employee Financial, and Revenue Center Financial reports
- Analytics reports including system sales, tender media, POS category, tax, 24h sales summary, and new tender detail for catering voucher
- Third-party reporting of sales and subsequent data flow to business intelligence platform

**Out of Scope:**
- Database-level changes or schema updates
- Validation of configuration workflows for enabling or managing the tender (not yet defined)
- Routing of orders to kitchen display unit (not yet implemented)
- Validation of loyalty program transactions or loyalty-related impacts
- Any third-party reference implementation

**Detail level:** High (explicit in/out of scope)
**Actual test scope (ground truth):** Full functional testing of tender flow; regression across all existing payment tender types; integration tests on financial reporting (3 report types); analytics report validation (6 report types); third-party data pipeline validation; exploratory testing on edge cases (partial tender, combined tenders, refunds).

---

## SPEC-05
**Title:** New Extra-Large Beverage Size Addition to Menu

**Change Type:** New feature (menu item / size tier addition)

**System Area:** Menu configuration, POS ordering, pricing engine

**Description:**
A new "extra-large" size tier is being introduced for the following beverage categories:
- Iced Coffee
- Iced Latte
- Refreshers (standard varieties)

Additional hero build items are also being introduced for specific seasonal varieties within these categories.

The new size introduces a new tier in threshold pricing. The default modifier/add-on count is set to 6. The size should price and appear as 2x the medium beverage price. No suggested retail price is applied to the default modifier build (syrups/swirls/shots). All modifications should remain available.

**Detail level:** Medium (pricing rules defined; no acceptance criteria)
**Actual test scope (ground truth):** Functional tests on ordering each new size across all 3 beverage categories; pricing validation (threshold pricing, 2x medium calculation, modifier pricing); hero build validation for seasonal variants; regression on existing size tiers and pricing; smoke test on POS order flow.

---

## SPEC-06
**Title:** Menu Item Availability App — Time Window Configuration Enhancement

**Change Type:** Enhancement (software behavior change in version update)

**System Area:** POS extension app / menu item scheduling

**Description:**
A new build of the Menu Item Availability extension app changes how scheduling windows are configured. The existing version uses a single combined start datetime and end datetime, meaning the app only runs once for that specific datetime range. The new version separates start/end date from start/end time, allowing the app to run every day at the defined time window until the end date.

Old config format: combined `StartDateTime` and `EndDateTime` fields.
New config format: separate `StartDate`, `EndDate`, `DailyStartTime`, `DailyEndTime` fields.

The extension app is available in both version 18.x and 19.x of the POS platform. Testing in the older version is time-sensitive due to a dependency on non-traditional store locations.

**Detail level:** Technical/medium (behavior described via config examples; no acceptance criteria)
**Actual test scope (ground truth):** Functional tests on daily recurrence behavior (runs every day at correct window); date boundary tests (does not run after end date); backward compatibility test (old config format handling); regression on menu item availability behavior in both platform versions.

---

## SPEC-08
**Title:** Role-Based Access Control — Restrict Void on Empty Check for Fraud Prevention

**Change Type:** Security / access control configuration change

**System Area:** POS role configuration, transaction management

**Description:**
A fraud pattern has been identified in production where external actors call stores and instruct staff to initiate a void on an empty check, bypassing the standard transaction return process. A system option bit exists to block this behavior at the role level. This option bit will be disabled for all roles that currently have it enabled, across both brands. Approval has been obtained from both brand stakeholders.

Roles currently permitted to void on empty check (to be restricted):
- Brand A: Shift Lead (standard), Shift Lead (plus), Assistant Manager, Manager, Multi-Unit, Field Engineer
- Brand B: Franchisee, Manager, Shift Leader

Roles already requiring authorization (no change needed):
- Brand A: Crew, Crew Plus
- Brand B: Crew Member, Senior Crew Member

Testing should confirm that disabling the option bit blocks the void-on-empty-check behavior without disrupting legitimate operations such as voiding individual items, transaction returns, and opening closed checks.

Note: The void-on-empty-check scenario can be replicated using a bakery/food item order flow, not a beverage order.

**Detail level:** High (roles explicitly listed, test objective clear)
**Actual test scope (ground truth):** Functional tests for each affected role attempting void on empty check (should be blocked); regression tests on legitimate void/return/closed check operations for all manager-level roles; smoke test on crew-level roles (authorization flow unchanged).

---

## SPEC-09
**Title:** Delivery Markup Percentage Update for Third-Party Delivery Platform

**Change Type:** Configuration change (percentage value update)

**System Area:** Reporting/analytics configuration, third-party delivery platform, data pipeline

**Description:**
Per updated contractual agreement, the delivery markup for one specific third-party delivery platform is being increased from 25% to 26%, effective a defined date. This change applies to both brands but only to this one delivery platform — other delivery platforms are unaffected.

The change is made in the reporting and analytics configuration tool under Data Mapping settings. After the change, QA must confirm whether the markup change applies retroactively to prior transactions or only prospectively.

Testing environments: UAT, Pre-Production, and Production.

Additional dependency: a separate third-party reporting platform may also require a corresponding change on their side — this needs to be verified and coordinated.

**Detail level:** Medium (clear what changes, unclear on retroactivity and third-party coordination)
**Actual test scope (ground truth):** Functional test of delivery markup value in reporting tool (UAT → Pre-Prod → Prod); validation of markup in sales reports for the affected platform; verification that other delivery platforms are unaffected; coordination check with third-party reporting platform; retroactivity determination (new open question).

---

## SPEC-10
**Title:** SSL Certificate Renewal for Loyalty Platform Integration

**Change Type:** Infrastructure / security (certificate rotation)

**System Area:** POS terminals, tablets, loyalty platform integration, EMC configuration

**Description:**
Existing SSL certificates for a loyalty platform integration are expiring in early February. New certificates must be in place by mid-January to avoid service disruption. This renewal affects only one brand (the second brand has migrated away from this integration).

A process runs on POS terminals and tablets to import the certificates, which are then referenced by the POS platform based on content management page settings. A new environment zone has been created in UAT for testing. Certificates have been sent to the external loyalty platform vendor for installation on their servers. Target deployment start: early January.

**Detail level:** Sparse (process described at high level; no acceptance criteria)
**Actual test scope (ground truth):** Functional test of certificate import process on POS terminals and tablets; connectivity validation to loyalty platform after cert rotation; smoke test on loyalty transactions end-to-end; UAT validation before Pre-Prod and Prod deployment.

---

## Summary Table

| Spec ID | Change Type | System Area | Detail Level | Complexity |
|---------|-------------|-------------|--------------|------------|
| SPEC-01 | Bug fix | POS ↔ Online ordering sync | High | Medium |
| SPEC-02 | Patch (firmware) | Payment processing | Sparse | Low |
| SPEC-03 | Hardware rollout | Network infrastructure | Medium | Medium |
| SPEC-04 | New feature | Payment + reporting + analytics | High | High |
| SPEC-05 | New feature (menu) | Menu config + pricing | Medium | Medium |
| SPEC-06 | Enhancement | POS scheduling extension app | Technical | Medium |
| SPEC-08 | Security/access control | POS role config | High | Medium |
| SPEC-09 | Config change | Reporting + delivery platform | Medium | Low-Medium |
| SPEC-10 | Infrastructure (cert rotation) | POS + loyalty integration | Sparse | Low |
