# WS1 Intelligence Engine V2 completion checklist

This checklist records the final six WS1 items implemented together for validation.

- [x] Route -> handler -> service -> database semantic topology
- [x] Test -> production dependency edges
- [x] Changed-lines -> symbol mapping
- [x] Incremental graph rebuild with unchanged parsed-document reuse
- [x] Generated/vendor source policy
- [x] Symbol/relation recall evaluator

Validation requirements before merge:

- Python 3.9 / 3.11 / 3.13 CI
- compileall
- full pytest
- self-check
- release gate

The recall evaluator reports missing symbols/relations explicitly and uses fail thresholds rather than silently treating unresolved relations as covered.
