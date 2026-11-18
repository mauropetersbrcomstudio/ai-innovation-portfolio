# SME Internal Knowledge Assistant

**Status: DEMO**

A local, deterministic retrieval demonstration for answering internal questions from a small set of approved knowledge sources. It filters sources by the requester's declared role, returns matching source excerpts with citations, and escalates when no sufficiently relevant accessible source is found.

This is not an LLM-powered assistant and does not generate answers. It retrieves source text only. The role field is a demonstration input, not authentication or a security boundary for real users.

## What it demonstrates

- Retrieval from a local, explicitly supplied source catalogue.
- Per-source role filtering before retrieval.
- Source identifiers and titles returned as citations.
- Human escalation when the question is empty, the role is missing, or no accessible source meets the relevance threshold.
- Duplicate source-ID validation.
- A JSON output record with the result and limitations.

## Run locally

Requires Python 3.10 or newer. No third-party packages are required.

```bash
python assistant.py
```

The sample request searches for the vacation procedure as an employee. The result is written to `output/retrieval_result.json`.

To use different files:

```bash
python assistant.py --sources approved_sources.json --request sample_request.json --output output/retrieval_result.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Source catalogue

`approved_sources.json` contains sample documents with:

- A unique source ID.
- A title and source text.
- An `allowed_roles` list.

The included content is synthetic and intended only to demonstrate retrieval. Replace it with current, business-approved documents before adapting the pattern.

## Retrieval and escalation behavior

The demo tokenizes the question and each accessible source, applies a simple overlap score, and returns up to three matches above a fixed illustrative threshold. This is keyword matching, not semantic search. It may miss relevant material or retrieve imperfect matches; users must inspect the excerpts and citations.

If no accessible source passes the threshold, the result is `ESCALATE` with no excerpts. The program does not disclose restricted source titles or contents in that result.

## Security, privacy, and limitations

- The role is supplied in the request JSON; it is not verified against an identity provider.
- Role filtering is an educational example, not production-grade access control.
- Sources are local files; the demo makes no network calls and sends no data externally.
- No LLM, vector database, embeddings, document ingestion pipeline, authentication, audit service, or enterprise connector is included.
- Retrieved excerpts are not generated answers and may be incomplete or outdated.
- Human review is required before acting on any retrieved information.

A real implementation would need authenticated identity, enforced authorization at the source layer, approved document ownership and lifecycle controls, secure storage, access logging, stronger retrieval evaluation, and tested escalation procedures.

---

This is an independently developed portfolio demonstration, not a completed client engagement or a production knowledge system.
