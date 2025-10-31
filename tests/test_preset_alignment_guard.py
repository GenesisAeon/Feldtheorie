"""Guard that simulator presets echo their analysis thresholds."""

from analysis import preset_alignment_guard


def test_all_presets_resonate_with_analysis() -> None:
    issues = preset_alignment_guard.validate_presets()
    assert not issues, f"Preset drift detected: {[str(issue) for issue in issues]}"
