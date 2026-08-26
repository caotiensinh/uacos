# UACOS Language Policy

UACOS repository prose must be written in English by default.

This policy exists so the project can be reviewed, tested, published, and reused by developers outside the original conversation context without removing technically necessary localization or Unicode support.

## Scope

English-first prose applies to:

- root `README.md`
- all files under `docs/`
- examples and report templates
- CLI help text and default user-facing command output
- source-code comments and docstrings
- test names and explanatory assertions intended to document behavior
- PR titles, PR descriptions, and release notes

## Allowed technical exceptions

Non-English text is allowed when the text itself is technically necessary, for example:

- runtime localization labels or translated UI strings
- multilingual keyword tables used by parsing, search, classification, or extraction logic
- fixture data that intentionally tests Unicode or localization behavior
- user-provided sample input required for a parser or encoding test
- external product names, organization names, or proper nouns
- quoted protocol payloads where the original language is part of the test case

Keep exceptions isolated and explain their purpose in English when the reason is not obvious from the surrounding code.

## Automated check

Run:

```bash
python scripts/check_english_docs.py --repo . --summary
```

The release gate also runs this check as `english_language_check`.

The checker intentionally distinguishes repository prose from runtime data:

- Python files: comments and real module/class/function docstrings are checked; ordinary runtime string literals are not scanned so localization and Unicode fixtures remain supported.
- Markdown, JSON, TOML, YAML, text, INI, and CFG files: text is checked line by line.
- An isolated technically necessary exception can be documented with `language-policy: allow-non-english` on the same line or immediately preceding line.
- Isolated possessive proper names are accepted as proper-noun exceptions; ordinary non-English prose is still rejected.

This is a conservative text-policy gate, not a language-detection model.

## Required style

Use clear technical English:

- short sentences
- concrete commands
- explicit limitations
- evidence-based claims
- no unsupported marketing language

## Forbidden in repository prose

Do not add Vietnamese or other non-English prose to project documentation, code comments, docstrings, CLI messages, PR descriptions, release notes, or user-facing examples unless one of the technical exceptions above applies.

Do not claim:

- UACOS saves 99% of tokens
- UACOS always saves 80-90% of tokens
- UACOS replaces AI coding agents
- UACOS guarantees correct patches

unless a benchmark or validation report directly supports the exact claim.

## Review checklist

Before merging documentation or user-facing changes, check:

- Is new repository prose in English?
- Is any non-English runtime text technically necessary and isolated?
- Does `python scripts/check_english_docs.py --repo . --summary` pass?
- Is the target reader clear?
- Is each public claim supported by evidence?
- Is the limitation stated when needed?
- Are links routed through `docs/README.md` when possible?

## Note for maintainers

Conversation with maintainers may happen in another language, but committed repository prose should remain English unless one of the allowed technical exceptions applies.
