# UACOS Public Benchmark Report Template

Use this template when publishing benchmark evidence. Do not publish token-saving claims without filling every required section.

## Summary

- Report name:
- Date:
- UACOS version/commit:
- Benchmark manifest:
- Benchmark runner:
- Hardware/OS:
- Python version:

## Repositories

| Repo | Type | Commit/Version | Included? | Reason if skipped |
|---|---|---|---:|---|
| UACOS | self repo | | yes | |
| Bear Detector | app/product | | | |
| RTSP Recorder | app/product | | | |
| SuperConnect | network/video infra | | | |
| EMSTONE/VMS Integration | integration | | | |

## Tasks

| Task ID | Repo | Task description | Task-local baseline tokens | Full-repo baseline tokens | UACOS context tokens | Reduction % | Test/validation result |
|---|---|---|---:|---:|---:|---:|---|
| | | | | | | | |

## Claim calculation

Define exactly how each metric is calculated.

- Full-repo input-context reduction:
- Task-local context reduction:
- Context quality score:
- Test pass rate:
- Skipped task policy:

## Results

| Metric | Value |
|---|---:|
| Repo count benchmarked | |
| Task count benchmarked | |
| Average full-repo input-context reduction | |
| Average task-local context reduction | |
| Tasks meeting 95% full-repo reduction | |
| Tasks meeting 99% full-repo reduction | |
| Test/validation pass rate | |
| Skipped repos/tasks | |

## Allowed claims from this report

Write only claims that are directly supported by the table above.

- 

## Claims not supported by this report

List claims that should not be made from this data.

- 

## Limitations

- Token counts are estimates unless provider billing records are attached.
- Full-repo input-context reduction is not the same as total workflow token reduction.
- Passing tests does not prove production correctness.
- Static analysis may miss dynamic framework behavior.

## Evidence links or file paths

- Raw benchmark report:
- Release gate report:
- Patch lifecycle reports:
- CI run:
