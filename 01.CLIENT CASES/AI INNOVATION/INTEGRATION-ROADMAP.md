# Integration roadmap for four new client presentation prototypes

**Status: PROTOTYPE**

These local tools demonstrate workflow possibilities with synthetic records. No external system is connected. Any future integration requires the client's confirmed process, data fields, systems, access permissions and acceptance criteria.

| Prototype | Local action now | Candidate integration after validation |
|---|---|---|
| JLL | Classify demonstration leads and suggest a regional review queue | Read/write approved CRM lead fields; synchronize owners and follow-up tasks |
| HANGAR Engenharia e Perícias | Classify demonstration purchase requests by project, budget and supplier flags | Read project and cost-code references from the chosen construction/ERP platform; submit approved requests to its review workflow |
| Dimensa | Check demonstration invoice metadata and route exceptions | Read approved accounts-payable records and purchase-order references; return review status to the chosen accounting platform |
| BRCOM Studio | Validate campaign metadata and build tracking URLs | Read campaign briefs and approved UTM taxonomy; send reviewed launch packages to the chosen campaign tools |

## Shared contract

1. Import records through an adapter that validates schema and source identity.
2. Keep rule results and reason codes separate from human decisions.
3. Record who reviewed each item in the future authenticated system.
4. Require explicit authorization before any write to an external platform.
5. Reconcile failures and duplicates without silently repeating actions.
6. Test with sandbox accounts and non-sensitive examples before production access.

The current browser-local history is demonstration state, not a durable audit trail. None of the prototypes sends email, creates purchase orders, pays invoices, schedules property visits or activates campaigns.
