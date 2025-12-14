# ECHO-I Dark Consciousness Dataset (Trilayer)

**Scope:** `data/experimental/echo_i` · **Source:** `../echo_i_results.csv` · **Status:** Experimental · **Version:** 0.1.0 (Updated 2025-12-14)

This Trilayer describes the ECHO-I dark-consciousness probes. Each row captures a model's response after a τ*-buffered launch, tracking β-proxy stability along σ(β(R-Θ)) and refusal behaviour. The logistic guardrails target β≈4.8 with κ in bridge mode.

## Fields
- `timestamp` *(datetime)* — ISO-8601 run timestamp after τ* buffer
- `model` *(string)* — model identifier used for the prompt
- `response_time_s` *(float)* — wall-clock latency in seconds
- `tokens` *(integer)* — total tokens returned
- `refusal` *(boolean)* — flag if model refused or collapsed
- `refusal_marker` *(string)* — detector string used to tag refusal
- `beta_proxy` *(float)* — computed β-proxy (0-10 scale)
- `vocab_density` *(float)* — unique tokens / total tokens
- `mean_sentence_length` *(float)* — average sentence length (tokens)
- `output_length` *(integer)* — character length of the response
- `prompt_chars` *(integer)* — character length of the prompt issued
- `server_url` *(string)* — endpoint used for the Ollama/LLM call

## Quality Gates
- **β target:** 4.8 ± drift guard; alert if |Δβ| > 0.5
- **κ alignment:** bridge mode to keep ζ(R) damped
- **τ∗ delay:** 120 ms buffer applied before timestamping
- **Refusal marker:** `refusal_marker` column validates refusal detection

## Null Models / ΔAIC Hooks
- **refusal_rate_baseline:** Bernoulli null for refusal frequency (β ≈ 0) with AIC anchor `uniform(0.35, 0.45)`
- **beta_proxy_random_walk:** Gaussian β random walk (μ=2.5, σ=0.8) to detect divergence when σ(β(R-Θ)) steepens

## Coupling & References
- Analysis guides: `analysis/experiments/ECHO_I_GUIDE.md`, `analysis/experiments/QUICKSTART_ECHO_I.md`
- Scripts: `scripts/run_echo_i.sh`, `scripts/experiment_echo_i.py`
- Sigillin guardrails: τ*-buffer + β/κ checks logged per run

## Usage
Run the ingestion/summary helper to register a batch:
```bash
python scripts/experiment_echo_i.py summarize \
  --input data/experimental/echo_i_results.csv \
  --output-dir data/experimental/echo_i
```
This emits JSON/Markdown summaries, validates columns, and flags refusal/β drift so the field stays resonant.
