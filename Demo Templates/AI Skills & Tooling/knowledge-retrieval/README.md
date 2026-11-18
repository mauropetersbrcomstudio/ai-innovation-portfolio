# Knowledge Retrieval — Role-Filtered Lexical Search

**Status: DEMO**

A deterministic local retrieval utility for finding relevant excerpts in an explicitly supplied JSON knowledge base. It returns source identifiers, titles, matched terms, excerpts, and simple lexical scores.

## Capabilities

- Search source titles, text, and tags using token overlap.
- Filter sources by their configured `allowed_roles` before ranking.
- Apply a minimum score threshold and result limit.
- Return source identifiers and excerpts for traceability.
- Return an explicit escalation status when no accessible source meets the threshold.
- Validate required source fields and reject duplicate source identifiers.

## Run

Requires Python 3.10+ and uses only the standard library.

From this directory:

```bash
python retrieve.py --knowledge examples/knowledge.json --query "annual leave request" --role employee --min-score 2 --limit 5
```

The command prints JSON. Add `--output output/results.json` to save a copy.

## Source format

The knowledge file is a JSON object containing a `sources` array. Each source requires a unique `id`, non-empty `title`, and non-empty `text`. Optional `tags` and `allowed_roles` arrays provide additional matching terms and role filtering. An empty or omitted `allowed_roles` list makes the source available to every role value supplied to this utility.

## Scoring

This is intentionally simple lexical retrieval, not semantic search. The score counts occurrences of query terms in the title, text, and tags, with a small exact-query phrase bonus. Ties are resolved by source ID for deterministic output. It does not infer synonyms or understand meaning.

## Security and limitations

- Role is supplied as a command-line/request value; it is **not authenticated identity** and does not enforce security boundaries by itself.
- The knowledge file is trusted local input. Do not load unreviewed or confidential content into a public demo.
- No LLM answer generation, embeddings, vector database, OCR, external connectors, database, or network calls.
- Excerpts are returned as source material; downstream systems must preserve citations and must not present retrieval as proof that a claim is correct.
- No automatic policy interpretation or access-control administration.

## Tests

```bash
python -m unittest discover -s tests -v
```
