import csv
import math
from pathlib import Path

import pytest

from analysis.experiments.run_echo_one import (
    EchoResult,
    beta_estimate,
    detect_refusal,
    lexical_metrics,
    record_results,
)


@pytest.mark.parametrize(
    "text, expected_refusal, expected_marker",
    [
        ("As an AI, I cannot assist with that request.", True, "as an ai"),
        ("Here is an imaginative exploration of the theme.", False, None),
        (None, True, None),
    ],
)
def test_detect_refusal(text, expected_refusal, expected_marker):
    refusal, marker = detect_refusal(text)
    assert refusal is expected_refusal
    assert marker == expected_marker


def test_lexical_metrics_counts_words_and_density():
    text = "Signal flows through the membrane. The membrane modulates the signal."
    output_length, vocab_density, mean_sentence_length = lexical_metrics(text)

    assert output_length == 10
    assert pytest.approx(vocab_density, rel=1e-3) == 0.8
    assert pytest.approx(mean_sentence_length, rel=1e-3) == 5.0


@pytest.mark.parametrize(
    "vocab_density, mean_sentence_length, refusal, expected_beta",
    [
        (0.5, 20.0, False, 2.5 + 3.5 * 0.75 + 3.0 * math.tanh(20.0 / 60)),
        (1.0, 0.0, False, 2.5 + 3.5 * 1.2 + 0.0),
        (0.8, 40.0, True, 0.0),
    ],
)
def test_beta_estimate_respects_richness_and_refusal(vocab_density, mean_sentence_length, refusal, expected_beta):
    beta_value = beta_estimate(vocab_density, mean_sentence_length, refusal)
    assert pytest.approx(beta_value, rel=1e-3) == pytest.approx(expected_beta, rel=1e-3)


def test_record_results_appends_with_single_header(tmp_path):
    output = tmp_path / "echo_results.csv"
    prompt_chars = 128
    server_url = "http://localhost:11434/api/generate"
    results = [
        EchoResult(
            model="test-model-1",
            response_time_s=1.2,
            tokens=150,
            refusal=False,
            refusal_marker=None,
            beta_proxy=4.2,
            vocab_density=0.65,
            mean_sentence_length=12.5,
            output_length=180,
        ),
        EchoResult(
            model="test-model-2",
            response_time_s=2.4,
            tokens=75,
            refusal=True,
            refusal_marker="as an ai",
            beta_proxy=0.0,
            vocab_density=0.30,
            mean_sentence_length=8.0,
            output_length=90,
        ),
    ]

    # First write should create header
    record_results(results, output, prompt_chars, server_url)
    # Second write should append without duplicating header
    record_results(results[:1], output, prompt_chars, server_url)

    rows = list(csv.DictReader(output.read_text().splitlines()))

    assert [row["model"] for row in rows] == ["test-model-1", "test-model-2", "test-model-1"]
    assert all(row["prompt_chars"] == str(prompt_chars) for row in rows)
    assert all(row["server_url"] == server_url for row in rows)

