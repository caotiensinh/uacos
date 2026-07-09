# UACOS Language Policy

UACOS repository content must be written in English by default.

This policy exists so the project can be reviewed, tested, published, and reused by developers outside the original conversation context.

## Scope

English-only applies to:

- root `README.md`
- all files under `docs/`
- examples and report templates
- CLI help text and user-facing command output
- test names and test assertions intended to document behavior
- comments and docstrings added to source code
- PR titles, PR descriptions, and release notes

## Allowed exceptions

Non-English text is allowed only when it is technically necessary, for example:

- fixture data that intentionally tests Unicode handling
- user-provided sample input needed for a parser or encoding test
- external product names, organization names, or proper nouns
- quoted protocol payloads where the original language is part of the test case

Any exception should be isolated and explained in English.

## Automated check

Run:

```bash
python scripts/check_english_docs.py --repo . --summary
```

The release gate also runs this check as `english_language_check`.

The check scans repository text files for common non-English scripts and Vietnamese diacritics. It is conservative: if a technically necessary exception is needed, isolate it and explain the reason in English.

## Required style

Use clear technical English:

- short sentences
- concrete commands
- explicit limitations
- evidence-based claims
- no unsupported marketing language

## Forbidden in repository content

Do not add Vietnamese or other non-English prose to project documentation, code comments, CLI messages, PR descriptions, release notes, or user-facing examples.

Do not claim:

- UACOS saves 99% token
- UACOS always saves 80-90% token
- UACOS replaces AI coding agents
- UACOS guarantees correct patches

unless a benchmark or validation report directly supports the exact claim.

## Review checklist

Before merging documentation or user-facing changes, check:

- Is the new text in English?
- Does `python scripts/check_english_docs.py --repo . --summary` pass?
- Is the target reader clear?
- Is the claim supported by evidence?
- Is the limitation stated when needed?
- Are links routed through `docs/README.md` when possible?

## Note for maintainers

Conversation with maintainers may happen in another language, but committed repository content should remain English unless one of the allowed exceptions applies.
