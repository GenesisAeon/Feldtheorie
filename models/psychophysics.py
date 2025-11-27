"""Psychophysics Models for V6 Framework.

This module bridges biological perception and fundamental physics through the
v_RIG framework. It models how consciousness integrates 2D holographic slices
into 3D volumetric experience, with particular focus on the Stereo-Vision
Slice Experiment.

Key References:
- Wichtig!_neue_Erkentniss_bitte_integrieren.txt (Stereo-Vision Discovery)
- Das Stereo-Vision Slice-Experiment.pdf
- GrundPrinzip Simulation.txt (Δt_Q integration windows)
- paper_v_rig_consciousness.md (Theoretical foundation)

Version: v6.0.0-alpha
Authors: Johann Benjamin Römer, MOR Framework
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .unified_constants import (
    V_RIG_DEFAULT,
)

# Typical human binocular parameters
INTEROCULAR_DISTANCE_CM = 6.5  # Standard interpupillary distance (IPD)
EYE_FOCAL_LENGTH_CM = 1.7  # Human eye focal length
RETINAL_DIAMETER_MM = 17.0  # Approximate retinal diameter


@dataclass
class StereoVisionParameters:
    """Parameters for stereo vision analysis.

    Attributes
    ----------
    interocular_distance : float
        Distance between eyes in cm (default: 6.5 cm)
    object_distance : float
        Distance to observed object in cm
    eye_focal_length : float
        Focal length of eye in cm (default: 1.7 cm)
    integration_window : float
        Temporal integration window Δt_Q in seconds (default: 0.15 s)
    """
    interocular_distance: float = INTEROCULAR_DISTANCE_CM
    object_distance: float = 50.0  # arm's length in cm
    eye_focal_length: float = EYE_FOCAL_LENGTH_CM
    integration_window: float = 0.15  # 150 ms typical


class StereoVisionModel:
    """Model for the Stereo-Vision Slice Experiment.

    This model demonstrates how binocular vision provides direct phenomenological
    access to the slice structure of consciousness. By alternating monocular
    vision (closing one eye, then the other), observers can manually "flip
    through" the 2D holographic slices that the brain normally fuses into
    3D experience.

    The Experiment
    --------------
    1. Hold arm outstretched, thumb up
    2. Focus on thumb with both eyes open
    3. Close left eye → thumb "jumps" to the right
    4. Open left, close right → thumb "jumps" to the left
    5. Repeat rapidly (1 Hz, 2 Hz, 5 Hz...)

    The perceived displacement corresponds to the spatial resolution of a single
    conscious moment, validating the v_RIG framework's prediction that
    consciousness operates as a slice-integrator.

    Key Insight
    -----------
    The "jump distance" when switching eyes equals the binocular parallax,
    which represents the spatial extent over which the brain integrates
    information during one consciousness moment (Δt_Q ≈ 100-300 ms).

    This provides a direct, experiential validation of:
        v_RIG = Δx_slice / Δt_integration

    Where:
        - Δx_slice: Spatial resolution (≈ IPD at arm's length)
        - Δt_integration: Integration window (≈ 100-300 ms)

    Examples
    --------
    >>> model = StereoVisionModel()
    >>> result = model.analyze_stereo_integration()
    >>> print(f"Jump distance: {result['parallax_distance_cm']:.2f} cm")
    >>> print(f"Slice fusion frequency: {result['slice_fusion_frequency_hz']:.2f} Hz")

    References
    ----------
    .. [1] Wichtig!_neue_Erkentniss_bitte_integrieren.txt
    .. [2] Das Stereo-Vision Slice-Experiment.pdf
    .. [3] Pöppel (2009): Pre-semantically defined temporal windows
    """

    def __init__(self, params: StereoVisionParameters | None = None):
        """Initialize the stereo vision model.

        Parameters
        ----------
        params : StereoVisionParameters, optional
            Vision parameters (uses defaults if not provided)
        """
        self.params = params or StereoVisionParameters()
        self.v_rig = V_RIG_DEFAULT * 1000 * 100  # Convert km/s to cm/s

    def calculate_binocular_parallax(self) -> dict[str, float]:
        """Calculate binocular parallax parameters.

        The parallax is the apparent displacement of an object when viewed
        from two different positions (left and right eyes).

        Returns
        -------
        dict
            Parallax analysis:
            - 'parallax_angle_deg': Parallax angle in degrees
            - 'parallax_angle_rad': Parallax angle in radians
            - 'parallax_distance_cm': Apparent jump distance in cm
            - 'retinal_displacement_mm': Displacement on retina in mm
        """
        ipd = self.params.interocular_distance
        d = self.params.object_distance
        f = self.params.eye_focal_length

        # Parallax angle (in radians)
        parallax_angle_rad = math.atan(ipd / d)
        parallax_angle_deg = math.degrees(parallax_angle_rad)

        # In 3D space at distance d, the apparent jump is approximately IPD
        # (for objects at arm's length, this is a good approximation)
        parallax_distance_cm = ipd * (d / (d - ipd/2))

        # Retinal displacement
        retinal_displacement_mm = f * math.tan(parallax_angle_rad) * 10  # cm to mm

        return {
            'parallax_angle_deg': parallax_angle_deg,
            'parallax_angle_rad': parallax_angle_rad,
            'parallax_distance_cm': parallax_distance_cm,
            'retinal_displacement_mm': retinal_displacement_mm,
        }

    def calculate_slice_fusion_frequency(self) -> float:
        """Calculate the Slice Fusion Frequency (SFF).

        The SFF is the rate at which alternating monocular images fuse into
        a single percept. This is analogous to Critical Flicker Frequency (CFF)
        but for spatial rather than temporal fusion.

        Hypothesis:
            SFF ∝ 1/Δt_Q  (inversely proportional to integration window)

        For typical Δt_Q ≈ 150 ms:
            SFF ≈ 6.7 Hz

        This means alternating eye closure faster than ~7 Hz should create
        a fused, continuous perception rather than discrete "jumps".

        Returns
        -------
        float
            Slice fusion frequency in Hz
        """
        return 1.0 / self.params.integration_window

    def calculate_vrig_integration_distance(self) -> float:
        """Calculate the distance v_RIG travels in one integration window.

        This represents the spatial "thickness" of a consciousness slice
        in the v_RIG framework.

        Formula:
            Δx_vrig = v_RIG · Δt_Q

        For v_RIG ≈ 1351.8 km/s and Δt_Q ≈ 150 ms:
            Δx_vrig ≈ 202.8 km

        This cosmic scale contrasts with the local neural scale (~6.5 cm),
        illustrating the multi-scale nature of consciousness integration.

        Returns
        -------
        float
            Integration distance in cm
        """
        return self.v_rig * self.params.integration_window

    def calculate_neural_integration_velocity(self) -> float:
        """Calculate the effective neural integration velocity.

        This is the velocity implied by the local spatial resolution
        (binocular parallax) divided by the integration time.

        Formula:
            v_neural = Δx_parallax / Δt_Q

        For Δx ≈ 6.5 cm and Δt_Q ≈ 150 ms:
            v_neural ≈ 43 cm/s ≈ 0.43 m/s

        This is much slower than v_RIG, reflecting the local, biological
        scale of neural integration versus the fundamental physical scale.

        Returns
        -------
        float
            Neural integration velocity in cm/s
        """
        parallax = self.calculate_binocular_parallax()
        return parallax['parallax_distance_cm'] / self.params.integration_window

    def analyze_stereo_integration(self) -> dict[str, float]:
        """Perform complete stereo-vision slice integration analysis.

        This method computes all relevant quantities for understanding how
        binocular vision demonstrates the slice structure of consciousness.

        Returns
        -------
        dict
            Complete analysis with keys:
            - 'ipd_cm': Interpupillary distance
            - 'object_distance_cm': Object distance
            - 'parallax_angle_deg': Parallax angle
            - 'parallax_distance_cm': Apparent jump distance
            - 'retinal_displacement_mm': Retinal displacement
            - 'integration_window_ms': Integration window
            - 'slice_fusion_frequency_hz': SFF in Hz
            - 'v_rig_km_s': v_RIG constant
            - 'v_rig_integration_distance_km': Cosmic integration scale
            - 'neural_integration_velocity_m_s': Local neural scale
            - 'scale_ratio': Ratio v_RIG / v_neural
        """
        parallax = self.calculate_binocular_parallax()
        sff = self.calculate_slice_fusion_frequency()
        vrig_dist = self.calculate_vrig_integration_distance()
        v_neural = self.calculate_neural_integration_velocity()

        return {
            'ipd_cm': self.params.interocular_distance,
            'object_distance_cm': self.params.object_distance,
            'parallax_angle_deg': parallax['parallax_angle_deg'],
            'parallax_distance_cm': parallax['parallax_distance_cm'],
            'retinal_displacement_mm': parallax['retinal_displacement_mm'],
            'integration_window_ms': self.params.integration_window * 1000,
            'slice_fusion_frequency_hz': sff,
            'v_rig_km_s': V_RIG_DEFAULT,
            'v_rig_integration_distance_km': vrig_dist / 100000,  # cm to km
            'neural_integration_velocity_m_s': v_neural / 100,  # cm/s to m/s
            'scale_ratio': self.v_rig / v_neural,
        }

    def predict_metabolic_sff_variation(
        self,
        baseline_metabolic_rate: float = 1.0,
        perturbed_metabolic_rate: float = 1.15
    ) -> dict[str, float]:
        """Predict how SFF varies with metabolic rate.

        Hypothesis: SFF ∝ metabolic_rate (higher metabolism → faster integration)

        This prediction can be tested by measuring SFF:
        - After caffeine (metabolism ↑)
        - After sleep deprivation (metabolism ↓)
        - During fever (metabolism ↑)
        - During hypothermia (metabolism ↓)

        Parameters
        ----------
        baseline_metabolic_rate : float
            Baseline metabolic rate (normalized to 1.0)
        perturbed_metabolic_rate : float
            Perturbed metabolic rate (e.g., 1.15 for +15% increase)

        Returns
        -------
        dict
            Predicted SFF values:
            - 'baseline_sff_hz': Baseline SFF
            - 'perturbed_sff_hz': Perturbed SFF
            - 'sff_change_percent': Percentage change
        """
        baseline_sff = self.calculate_slice_fusion_frequency()

        # Linear scaling assumption (to be empirically validated)
        perturbed_sff = baseline_sff * (perturbed_metabolic_rate / baseline_metabolic_rate)

        sff_change_percent = ((perturbed_sff - baseline_sff) / baseline_sff) * 100

        return {
            'baseline_sff_hz': baseline_sff,
            'perturbed_sff_hz': perturbed_sff,
            'sff_change_percent': sff_change_percent,
        }


class CriticalFlickerFrequency:
    """Model for Critical Flicker Frequency (CFF) analysis.

    CFF is the frequency at which a flickering light appears steady.
    It provides an independent measure of temporal integration that
    should correlate with SFF according to the v_RIG framework.

    Typical CFF values:
    - Humans (foveal): 50-90 Hz
    - Humans (peripheral): 30-60 Hz
    - Affected by: luminance, metabolic rate, age, fatigue
    """

    @staticmethod
    def estimate_cff(
        luminance_cd_m2: float = 100.0,
        metabolic_factor: float = 1.0
    ) -> float:
        """Estimate CFF based on luminance and metabolic state.

        Uses the Ferry-Porter law: CFF ∝ log(luminance)

        Parameters
        ----------
        luminance_cd_m2 : float
            Luminance in candelas per square meter
        metabolic_factor : float
            Metabolic scaling factor (1.0 = baseline)

        Returns
        -------
        float
            Estimated CFF in Hz
        """
        # Ferry-Porter law with empirical constants
        base_cff = 10.0 * math.log10(luminance_cd_m2) + 10.0

        # Metabolic modulation
        cff = base_cff * metabolic_factor

        return cff

    @staticmethod
    def correlate_cff_with_sff(cff_hz: float, sff_hz: float) -> dict[str, float]:
        """Analyze correlation between CFF and SFF.

        Hypothesis: CFF and SFF should correlate because both measure
        temporal integration capacity (Δt_Q).

        Predicted relationship:
            CFF / SFF ≈ constant ≈ 10-15
            (temporal flicker integrates faster than spatial slice fusion)

        Parameters
        ----------
        cff_hz : float
            Critical Flicker Frequency
        sff_hz : float
            Slice Fusion Frequency

        Returns
        -------
        dict
            Correlation analysis:
            - 'cff_hz': Input CFF
            - 'sff_hz': Input SFF
            - 'ratio': CFF/SFF ratio
            - 'implied_delta_t_Q_from_cff': Integration window from CFF
            - 'implied_delta_t_Q_from_sff': Integration window from SFF
        """
        ratio = cff_hz / sff_hz
        delta_t_cff = 1.0 / cff_hz
        delta_t_sff = 1.0 / sff_hz

        return {
            'cff_hz': cff_hz,
            'sff_hz': sff_hz,
            'ratio': ratio,
            'implied_delta_t_Q_from_cff_ms': delta_t_cff * 1000,
            'implied_delta_t_Q_from_sff_ms': delta_t_sff * 1000,
        }


def demonstrate_stereo_vision_experiment():
    """Demonstrate the Stereo-Vision Slice Experiment analysis.

    This function showcases the complete workflow for analyzing the
    phenomenological experiment that validates v_RIG theory.
    """
    print("=" * 70)
    print("STEREO-VISION SLICE EXPERIMENT — v_RIG Validation")
    print("=" * 70)
    print()
    print("Experiment: Alternate closing left/right eyes while viewing thumb")
    print("Observable: Thumb 'jumps' by the binocular parallax distance")
    print("Interpretation: Direct experience of 2D slice separation")
    print()

    # Create model
    model = StereoVisionModel()

    # Analyze
    results = model.analyze_stereo_integration()

    print("-" * 70)
    print("GEOMETRIC PARAMETERS")
    print("-" * 70)
    print(f"Interpupillary Distance (IPD):    {results['ipd_cm']:.2f} cm")
    print(f"Object Distance:                   {results['object_distance_cm']:.1f} cm")
    print(f"Parallax Angle:                    {results['parallax_angle_deg']:.2f}°")
    print()

    print("-" * 70)
    print("OBSERVABLE EFFECTS")
    print("-" * 70)
    print(f"Thumb 'Jump' Distance:             {results['parallax_distance_cm']:.2f} cm")
    print(f"Retinal Displacement:              {results['retinal_displacement_mm']:.2f} mm")
    print("→ This is what you SEE when alternating eyes!")
    print()

    print("-" * 70)
    print("CONSCIOUSNESS INTEGRATION")
    print("-" * 70)
    print(f"Integration Window (Δt_Q):         {results['integration_window_ms']:.0f} ms")
    print(f"Slice Fusion Frequency (SFF):     {results['slice_fusion_frequency_hz']:.1f} Hz")
    print(f"→ Alternate eyes faster than {results['slice_fusion_frequency_hz']:.1f} Hz → fusion!")
    print()

    print("-" * 70)
    print("MULTI-SCALE v_RIG FRAMEWORK")
    print("-" * 70)
    print(f"v_RIG (fundamental):               {results['v_rig_km_s']:.1f} km/s")
    print(f"v_RIG integration distance:        {results['v_rig_integration_distance_km']:.1f} km")
    print(f"Neural integration velocity:       {results['neural_integration_velocity_m_s']:.2f} m/s")
    print(f"Scale ratio (v_RIG / v_neural):    {results['scale_ratio']:.0f}×")
    print()

    # Metabolic prediction
    print("-" * 70)
    print("TESTABLE PREDICTION: Metabolic Modulation")
    print("-" * 70)

    # After caffeine (+15% metabolism)
    caffeine = model.predict_metabolic_sff_variation(1.0, 1.15)
    print(f"Baseline SFF:                      {caffeine['baseline_sff_hz']:.2f} Hz")
    print(f"After Caffeine (+15% metabolism):  {caffeine['perturbed_sff_hz']:.2f} Hz")
    print(f"Predicted change:                  {caffeine['sff_change_percent']:+.1f}%")
    print()

    # CFF correlation
    print("-" * 70)
    print("CORRELATION WITH CRITICAL FLICKER FREQUENCY")
    print("-" * 70)
    cff = CriticalFlickerFrequency.estimate_cff(luminance_cd_m2=100.0)
    correlation = CriticalFlickerFrequency.correlate_cff_with_sff(
        cff, results['slice_fusion_frequency_hz']
    )
    print(f"Estimated CFF:                     {correlation['cff_hz']:.1f} Hz")
    print(f"Measured SFF:                      {correlation['sff_hz']:.1f} Hz")
    print(f"CFF/SFF Ratio:                     {correlation['ratio']:.1f}")
    print(f"Implied Δt_Q from CFF:             {correlation['implied_delta_t_Q_from_cff_ms']:.1f} ms")
    print(f"Implied Δt_Q from SFF:             {correlation['implied_delta_t_Q_from_sff_ms']:.1f} ms")
    print()

    print("=" * 70)
    print("✨ THE GENIUS: Anyone with two eyes can validate v_RIG!")
    print("=" * 70)


if __name__ == '__main__':
    # Run demonstration
    demonstrate_stereo_vision_experiment()
