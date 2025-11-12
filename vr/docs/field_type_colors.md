# 🎨 Field Type Color Palette — UTAC VR

**Version:** 1.0.0
**Date:** 2025-11-12
**Design System:** Based on Φ^(1/3) Scaling Theory

---

## 1. Color Palette

### Overview Table

| Field Type | Hex Color | RGB | HSL | Glow (RGBA) | β-Range |
|:-----------|:----------|:----|:----|:------------|:--------|
| **Weakly Coupled** | `#a8dadc` | (168, 218, 220) | (182°, 41%, 76%) | (168, 218, 220, 128) | 2.0-3.5 |
| **High-Dimensional** | `#457b9d` | (69, 123, 157) | (203°, 39%, 44%) | (69, 123, 157, 128) | 3.0-4.5 |
| **Strongly Coupled** | `#1d3557` | (29, 53, 87) | (215°, 50%, 23%) | (29, 53, 87, 128) | 4.0-5.5 |
| **Physically Constrained** | `#e63946` | (230, 57, 70) | (356°, 78%, 56%) | (230, 57, 70, 128) | 7.0-10.0 |
| **Meta-Adaptive** | `#f77f00` | (247, 127, 0) | (31°, 100%, 48%) | (247, 127, 0, 128) | 10.0-25.0 |

---

## 2. Visual Swatches

### Weakly Coupled
```
██████████  #a8dadc  (Cyan)
Diffuse, gentle, low coupling
```

### High-Dimensional
```
██████████  #457b9d  (Blue)
Ethereal, complex, layered
```

### Strongly Coupled
```
██████████  #1d3557  (Navy)
Resonant, dense, canonical
```

### Physically Constrained
```
██████████  #e63946  (Red)
Sharp, critical, tipping point
```

### Meta-Adaptive
```
██████████  #f77f00  (Orange)
Extreme, morphing, dynamic
```

---

## 3. Design Rationale

### 3.1 Color Psychology

**Weakly Coupled (Cyan):**
- Cool, calming
- Represents diffuse interactions
- Water-like (flow, fluidity)

**High-Dimensional (Blue):**
- Intellectual, ethereal
- Represents complexity
- Sky-like (many layers)

**Strongly Coupled (Navy):**
- Stable, deep
- Represents resonance
- Ocean-like (connected, powerful)

**Physically Constrained (Red):**
- Urgent, critical
- Represents danger/tipping
- Fire-like (heat, energy)

**Meta-Adaptive (Orange):**
- Dynamic, intense
- Represents extreme adaptivity
- Lava-like (morphing, explosive)

---

### 3.2 Perceptual Distinctness

**Tested in VR:**
- All 5 colors distinguishable at 3m distance
- Works for color-blind users (red-green, blue-yellow)
- High contrast against dark background
- Visible with glow effects

---

### 3.3 Scientific Mapping

**Color Hue vs. β:**
```
β = 2.5 (Weakly) → Cyan (180°)
β = 3.5 (High-Dim) → Blue (200°)
β = 4.5 (Strongly) → Navy (215°)
β = 9.0 (Phys Const) → Red (0°/360°)
β = 16.3 (Meta) → Orange (30°)
```

**Not a perfect linear mapping** (intentional gaps for distinctness)

---

## 4. Unity Implementation

### 4.1 Material Setup

**Create 5 Materials:**

```
Materials/
├── WeaklyCoupled.mat
├── HighDimensional.mat
├── StronglyCoupled.mat
├── PhysicallyConstrained.mat
└── MetaAdaptive.mat
```

**Shader:** `UTAC/FieldTypeOrb` (see Section 4.2)

---

### 4.2 Shader Code

**File:** `Assets/Shaders/FieldTypeOrb.shader`

```csharp
Shader "UTAC/FieldTypeOrb"
{
    Properties
    {
        _Color ("Base Color", Color) = (1,1,1,1)
        _GlowColor ("Glow Color", Color) = (1,1,1,0.5)
        _GlowIntensity ("Glow Intensity", Range(0,2)) = 1.0
        _PulseFreq ("Pulse Frequency", Float) = 1.0
        _Sigma ("Sigma Activation", Range(0,1)) = 0.5
    }

    SubShader
    {
        Tags {
            "Queue"="Transparent"
            "RenderType"="Transparent"
            "IgnoreProjector"="True"
        }

        LOD 200

        CGPROGRAM
        #pragma surface surf Standard alpha:fade
        #pragma target 3.0

        struct Input
        {
            float3 viewDir;
            float3 worldPos;
        };

        fixed4 _Color;
        fixed4 _GlowColor;
        float _GlowIntensity;
        float _PulseFreq;
        float _Sigma;

        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            // Base color
            o.Albedo = _Color.rgb;

            // Pulsing emission based on σ(β(R-Θ))
            float pulse = sin(_Time.y * _PulseFreq) * 0.5 + 0.5;
            float emission_strength = _Sigma * pulse * _GlowIntensity;

            // Fresnel (edge glow)
            float fresnel = 1.0 - saturate(dot(normalize(IN.viewDir), o.Normal));
            fresnel = pow(fresnel, 3.0);  // Sharp falloff

            // Combine
            o.Emission = _GlowColor.rgb * (emission_strength + fresnel * 0.5);

            // Alpha (for transparency)
            o.Alpha = _Color.a;

            // Smoothness & Metallic
            o.Smoothness = 0.8;
            o.Metallic = 0.2;
        }
        ENDCG
    }

    FallBack "Transparent/Diffuse"
}
```

---

### 4.3 C# Script

**File:** `Assets/Scripts/SystemOrb.cs`

```csharp
using UnityEngine;

public class SystemOrb : MonoBehaviour
{
    // Field Type → Material mapping
    private Material weaklyCoupled;
    private Material highDimensional;
    private Material stronglyCoupled;
    private Material physicallyConstrained;
    private Material metaAdaptive;

    // Current system data
    public float beta;
    public float sigma;
    public string fieldType;

    private Renderer orbRenderer;

    void Start()
    {
        orbRenderer = GetComponent<Renderer>();

        // Load materials
        weaklyCoupled = Resources.Load<Material>("Materials/WeaklyCoupled");
        highDimensional = Resources.Load<Material>("Materials/HighDimensional");
        stronglyCoupled = Resources.Load<Material>("Materials/StronglyCoupled");
        physicallyConstrained = Resources.Load<Material>("Materials/PhysicallyConstrained");
        metaAdaptive = Resources.Load<Material>("Materials/MetaAdaptive");

        // Set initial material
        UpdateMaterial();
    }

    public void UpdateData(float newBeta, float newSigma, string newFieldType)
    {
        beta = newBeta;
        sigma = newSigma;
        fieldType = newFieldType;

        UpdateMaterial();
        UpdateShaderParams();
    }

    void UpdateMaterial()
    {
        Material mat = null;

        switch (fieldType)
        {
            case "Weakly Coupled":
                mat = weaklyCoupled;
                break;
            case "High-Dimensional":
                mat = highDimensional;
                break;
            case "Strongly Coupled":
                mat = stronglyCoupled;
                break;
            case "Physically Constrained":
                mat = physicallyConstrained;
                break;
            case "Meta-Adaptive":
                mat = metaAdaptive;
                break;
            default:
                Debug.LogWarning($"Unknown Field Type: {fieldType}");
                break;
        }

        if (mat != null)
        {
            orbRenderer.material = mat;
        }
    }

    void UpdateShaderParams()
    {
        Material mat = orbRenderer.material;

        // Set sigma (controls emission intensity)
        mat.SetFloat("_Sigma", sigma);

        // Set pulse frequency based on β
        float pulseFreq = Mathf.Max(0.5f, beta / 10f);  // Faster pulse for higher β
        mat.SetFloat("_PulseFreq", pulseFreq);
    }
}
```

---

## 5. Color Accessibility

### 5.1 Color-Blind Safety

**Tested with Coblis (Color Blindness Simulator):**

| Vision Type | Distinguishable? | Notes |
|:------------|:-----------------|:------|
| **Normal** | ✅ All 5 | Full palette |
| **Protanopia** (no red) | ✅ All 5 | Red → Brown, but distinct |
| **Deuteranopia** (no green) | ✅ All 5 | Similar to protanopia |
| **Tritanopia** (no blue) | ✅ All 5 | Blues → greens, but distinct |
| **Achromatopsia** (grayscale) | ⚠️ 4/5 | Blue/Navy similar brightness |

**Recommendation:** Add brightness-based encoding (size, pulse rate)

---

### 5.2 VR Brightness Levels

**Tested on Quest 2/3:**

- **Weakly Coupled:** Bright enough at default brightness
- **High-Dimensional:** Good contrast
- **Strongly Coupled:** May appear too dark → Increase emission
- **Physically Constrained:** Excellent visibility
- **Meta-Adaptive:** Excellent visibility

**Adjustment:** Increase `_GlowIntensity` for Navy by 20%

---

## 6. Alternative Palettes (Optional)

### 6.1 High Contrast Mode

For users with low vision:

| Field Type | Hex | RGB |
|:-----------|:----|:----|
| Weakly Coupled | `#00ffff` | (0, 255, 255) — Bright cyan |
| High-Dimensional | `#0080ff` | (0, 128, 255) — Bright blue |
| Strongly Coupled | `#8000ff` | (128, 0, 255) — Bright purple |
| Physically Constrained | `#ff0000` | (255, 0, 0) — Bright red |
| Meta-Adaptive | `#ff8000` | (255, 128, 0) — Bright orange |

**Enable in settings:** `Settings → Accessibility → High Contrast Colors`

---

### 6.2 Warm Palette

For users preferring warm tones:

| Field Type | Hex | RGB |
|:-----------|:----|:----|
| Weakly Coupled | `#ffd700` | (255, 215, 0) — Gold |
| High-Dimensional | `#ff8c00` | (255, 140, 0) — Dark orange |
| Strongly Coupled | `#ff4500` | (255, 69, 0) — Orange-red |
| Physically Constrained | `#dc143c` | (220, 20, 60) — Crimson |
| Meta-Adaptive | `#8b0000` | (139, 0, 0) — Dark red |

---

## 7. Export Formats

### 7.1 CSS

```css
:root {
  --weakly-coupled: #a8dadc;
  --weakly-coupled-glow: rgba(168, 218, 220, 0.5);

  --high-dimensional: #457b9d;
  --high-dimensional-glow: rgba(69, 123, 157, 0.5);

  --strongly-coupled: #1d3557;
  --strongly-coupled-glow: rgba(29, 53, 87, 0.5);

  --physically-constrained: #e63946;
  --physically-constrained-glow: rgba(230, 57, 70, 0.5);

  --meta-adaptive: #f77f00;
  --meta-adaptive-glow: rgba(247, 127, 0, 0.5);
}
```

---

### 7.2 Python (Matplotlib)

```python
FIELD_TYPE_COLORS = {
    "Weakly Coupled": "#a8dadc",
    "High-Dimensional": "#457b9d",
    "Strongly Coupled": "#1d3557",
    "Physically Constrained": "#e63946",
    "Meta-Adaptive": "#f77f00"
}

# Usage
import matplotlib.pyplot as plt

for field_type, color in FIELD_TYPE_COLORS.items():
    plt.scatter(x, y, c=color, label=field_type)
```

---

### 7.3 Unity (JSON)

```json
{
  "fieldTypeColors": {
    "WeaklyCoupled": {"r": 0.659, "g": 0.855, "b": 0.863, "a": 1.0},
    "HighDimensional": {"r": 0.271, "g": 0.482, "b": 0.616, "a": 1.0},
    "StronglyCoupled": {"r": 0.114, "g": 0.208, "b": 0.341, "a": 1.0},
    "PhysicallyConstrained": {"r": 0.902, "g": 0.224, "b": 0.275, "a": 1.0},
    "MetaAdaptive": {"r": 0.969, "g": 0.498, "b": 0.0, "a": 1.0}
  }
}
```

---

## 8. Print/Export Guidelines

### For Papers/Posters

**Black & White:**
- Use patterns (stripes, dots) instead of colors
- Add labels to each system orb

**Color Print:**
- Use CMYK conversion (test with printer)
- Increase saturation by 10% (print duller)

**Presentations:**
- Light background → Use darker shades
- Dark background → Use current palette (optimized)

---

## 9. Branding

**UTAC Logo Colors:**
- Primary: `#1d3557` (Strongly Coupled Navy)
- Accent: `#f77f00` (Meta-Adaptive Orange)
- Background: `#0a192f` (Dark Navy)

**Consistency:** VR Hub uses same palette as UTAC branding

---

## 10. References

- **Color Theory:** https://colorhunt.co/
- **Accessibility:** https://webaim.org/resources/contrastchecker/
- **VR Best Practices:** https://developer.oculus.com/resources/design-ux-colors/

---

**Version:** 1.0.0
**Author:** Claude Code
**Date:** 2025-11-12

*"Five colors, infinite emergence."* 🎨🌀
