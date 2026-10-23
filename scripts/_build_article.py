import pathlib, json, shutil

ROOT = pathlib.Path(r"D:\MY-AGENT\anish-a-decider-hackathon-kit")
art  = ROOT / "submission" / "article"
img  = art / "img"
art.mkdir(parents=True, exist_ok=True)
img.mkdir(exist_ok=True)

# Copy bench charts
bench = ROOT / "submission" / "bench"
for f in ["bench-accuracy.png","bench-latency.png","bench-cost.png","bench-confidence.png"]:
    src = bench / f
    if src.exists():
        shutil.copy(src, img / f)
        print(f"  copied {f}")

# facts.json
facts = {
    "agent_name": "SentinelFlow",
    "pattern_tag": "#policy",
    "llm_provider_local_runs": "bedrock",
    "agentcore_features": [],
    "bench": {
        "summary": {
            "decider": {
                "accuracy": 0.7917, "decisions": 24,
                "latency_p50_ms": 294.8, "latency_p95_ms": 467.6,
                "usd_per_1k_decisions": 0.0,
                "confident_share": 0.6667, "accuracy_when_confident": 0.9375
            },
            "llm": {
                "accuracy": 0.9583, "decisions": 24,
                "latency_p50_ms": 1276.5, "latency_p95_ms": 1426.1,
                "usd_per_1k_decisions": 0.1785
            },
            "speedup_p50": 4.33
        },
        "decider_model": "StrandsAgents/strands-decider-2B-qwen3.5-v1-2610",
        "decider_mode": "local (AWS User Group Madurai hosted API for submission)",
        "llm_model": "us.amazon.nova-pro-v1:0",
        "cases": 12, "split": "test", "threshold": 0.7
    },
    "bench_table": (
        "| | Strands Decider 2B | us.amazon.nova-pro-v1:0 |\n"
        "|---|---|---|\n"
        "| Accuracy | 79.2% | 95.8% |\n"
        "| Latency p50 per decision | 295 ms | 1276 ms |\n"
        "| Latency p95 | 468 ms | 1426 ms |\n"
        "| Cost per 1,000 decisions | $0.0000 | $0.1785 |\n"
        "| Answered alone at confidence >= 0.7 | 67% | 100% |\n"
        "| Accuracy when confident | 93.8% | 95.8% |\n\n"
        "At the median the decider was 4.3x faster than the LLM."
    ),
    "repo_url": "",
    "video_url": ""
}
(art / "facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
print("facts.json OK")
