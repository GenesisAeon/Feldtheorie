"""Generate synthetic PSRM maps for a quick demo run."""

from __future__ import annotations

from pathlib import Path

from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.neuro_profile_model import (
    NeuroProfile,
)
from experiments.Phaethon_Geminiden_Bennu.NeuroProfile.code.psrm_mapper import (
    PSRMMapper,
    write_psrm_trilayer,
)


def main() -> None:
    print(
        "Permission Request: Do you accept this task? We aim for a joyful and efficient collaboration."
    )
    output_dir = Path("data/sigillin_maps")
    output_dir.mkdir(parents=True, exist_ok=True)

    for index in range(5):
        subject_id = f"demo_{index:03d}"
        print(f"\n🧠 Generating PSRM for subject {index + 1} ({subject_id})...")

        profile = NeuroProfile(subject_id=subject_id)
        profile.load_synthetic_data()
        profile.analyze()

        mapper = PSRMMapper(profile)
        sigillin_map = mapper.generate_sigillin_map()
        payload = sigillin_map.payload
        layer_1 = payload["layer_1_signal"]

        output_stem = output_dir / f"psrm_{payload['user_id']}"
        write_psrm_trilayer(sigillin_map, output_stem=output_stem)

        print(f"   β-cluster: {layer_1['beta_cluster']}")
        print(f"   CREP aggregate: {layer_1['crep_aggregate']:.3f}")
        print(f"   Map saved: {output_stem}.yaml/.json/.md")

    print("\n🎉 Demo complete! Check data/sigillin_maps/ for outputs.")


if __name__ == "__main__":
    main()
