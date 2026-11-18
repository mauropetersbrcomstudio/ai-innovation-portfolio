# SME Customer Support Automation

**Status: DEMO**

A small, local Python demonstration of a customer-support workflow for an SME. It reads sample requests, assigns a category using transparent rules, prepares a draft from a small approved knowledge base, and sends uncertain or sensitive cases to human review.

The demo is intentionally limited. It does not use a language model, contact customers, or connect to a CRM, WhatsApp, email, or any other live system.

## Try the demo

Requires Python 3.10 or newer. No third-party packages are needed.

From this directory, run:

```bash
python support_demo.py
```

The example reads `sample_requests.json` and `knowledge_base.json`, then writes the results to `output/results.json`.

To use another request file:

```bash
python support_demo.py --input my_requests.json --output my_results/results.json
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## What it demonstrates

- Classifies requests into a small set of support categories.
- Uses only response drafts stored in the local knowledge-base file.
- Routes unclear, multi-category, sensitive, or unsupported requests to human review.
- Records the category, route, reason, source, and draft (when available).
- Keeps the original request data local and produces a JSON result file.

## Sample scenarios

The included synthetic requests cover an order-status question, an invoice request, a refund request, an account-access issue, and a question outside the sample knowledge base.

## Safety and limitations

- **No messages are sent.** A draft is produced for review only.
- **No external actions occur.** The demo does not change orders, accounts, invoices, or customer records.
- **No live data is included.** The sample requests are synthetic.
- **Rule-based classification only.** This is not an LLM-powered agent; its keyword rules are deliberately simple.
- **Limited knowledge base.** The sample answers ask for information or direct the request to a team. They do not claim to know a company's actual policies.
- **Human review is essential.** Refunds, complaints, account changes, legal or safety matters, ambiguous requests, and unsupported questions should not be handled automatically.

A real deployment would require business-approved content, privacy and access controls, validated integrations, monitoring, and explicit authorization for any customer-facing action.

---

This is an independently developed portfolio demonstration, not a completed client engagement or a production support system.
