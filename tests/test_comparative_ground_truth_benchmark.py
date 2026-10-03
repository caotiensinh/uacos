from uacos.benchmarks.comparative import BenchmarkThresholds, evaluate_comparative_benchmark


def _manifest():
    return {
        "version": 1,
        "tasks": [
            {
                "id": "task-1",
                "required_symbols": ["app:target"],
                "required_relations": ["app:target->svc:work"],
            }
        ],
    }


def _rows(*, uacos_tokens: int = 100, uacos_pass: bool = True):
    rows = []
    for mode, tokens, selected in [
        ("full_repo", 1000, ["app:target", "noise:a", "noise:b", "noise:c"]),
        ("grep", 300, ["app:target", "noise:a"]),
        ("uacos", uacos_tokens, ["app:target"]),
    ]:
        for repeat in (1, 2, 3):
            rows.append(
                {
                    "task_id": "task-1",
                    "mode": mode,
                    "repeat": repeat,
                    "provider": "codex",
                    "model": "same-model",
                    "passed": uacos_pass if mode == "uacos" else True,
                    "retries": 0,
                    "tool_calls": 2,
                    "input_tokens": tokens,
                    "total_tokens": tokens + 50,
                    "latency_ms": 100,
                    "index_overhead_ms": 5 if mode == "uacos" else 0,
                    "selected_symbols": selected,
                    "selected_relations": ["app:target->svc:work"],
                }
            )
    return rows


def test_comparative_benchmark_passes_only_with_required_repeats_and_targets():
    report = evaluate_comparative_benchmark(_manifest(), _rows())
    assert report["status"] == "pass"
    assert report["findings"] == []
    assert all(report["target_checks"].values())
    assert report["summaries"]["uacos"]["required_symbol_recall"] == 1.0
    assert report["summaries"]["uacos"]["noise_rate"] == 0.0


def test_comparative_benchmark_rejects_insufficient_repeats():
    report = evaluate_comparative_benchmark(_manifest(), _rows()[:-1])
    assert report["status"] == "fail"
    assert "insufficient_repeats:task-1:uacos:2" in report["findings"]


def test_comparative_benchmark_rejects_provider_model_mismatch():
    rows = _rows()
    rows[-1]["model"] = "different-model"
    report = evaluate_comparative_benchmark(_manifest(), rows)
    assert report["status"] == "fail"
    assert "provider_or_model_mismatch:task-1" in report["findings"]


def test_comparative_benchmark_rejects_pass_rate_regression_and_token_regression():
    report = evaluate_comparative_benchmark(_manifest(), _rows(uacos_tokens=1200, uacos_pass=False))
    assert report["status"] == "fail"
    assert report["target_checks"]["pass_rate_not_below_full_repo"] is False
    assert report["target_checks"]["input_tokens_below_full_repo"] is False


def test_thresholds_are_explicit_and_configurable():
    report = evaluate_comparative_benchmark(
        _manifest(),
        _rows(),
        thresholds=BenchmarkThresholds(min_required_symbol_recall=0.95, max_noise_rate=0.20, min_repeats=3),
    )
    assert report["thresholds"]["min_required_symbol_recall"] == 0.95
    assert report["thresholds"]["max_noise_rate"] == 0.20
    assert report["thresholds"]["min_repeats"] == 3
