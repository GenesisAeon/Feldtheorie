# 🌟 Acknowledgements

The **Feldtheorie** project builds upon work from the open-source community, particularly the **Open Climate Fix** initiative. We gratefully acknowledge their contributions.

---

## Open Climate Fix (OCF)

Portions of the Feldtheorie data pipelines are inspired by or adapted from the following **Open Climate Fix** repositories:

### 1. **graph_weather** (MIT License)
- **Repository:** [github.com/openclimatefix/graph_weather](https://github.com/openclimatefix/graph_weather)
- **Description:** Graph-based weather forecasting with GNNs
- **Usage in Feldtheorie:** Modular NWP ingestion patterns, xarray/zarr workflows
- **Original Authors:** © Open Climate Fix contributors
- **License:** MIT (see repository for full license text)

### 2. **skillful_nowcasting** (MIT License)
- **Repository:** [github.com/openclimatefix/skillful_nowcasting](https://github.com/openclimatefix/skillful_nowcasting)
- **Description:** Implementation of DeepMind's DGMR radar nowcasting
- **Usage in Feldtheorie:** Radar data loading patterns (Nimrod/MRMS), HuggingFace Datasets integration
- **Original Authors:** © Open Climate Fix contributors
- **License:** MIT (see repository for full license text)

### 3. **PVNet** (MIT License)
- **Repository:** [github.com/openclimatefix/PVNet](https://github.com/openclimatefix/pvnet)
- **Description:** Multi-modal PV forecasting (NWP + Satellite + Measurements)
- **Usage in Feldtheorie:** ICON-EU Zarr ingestion patterns, HuggingFace Datasets references
- **Original Authors:** © Open Climate Fix contributors
- **License:** MIT (see repository for full license text)

### 4. **open-source-quartz-solar-forecast** (MIT License)
- **Repository:** [github.com/openclimatefix/open-source-quartz-solar-forecast](https://github.com/openclimatefix/open-source-quartz-solar-forecast)
- **Description:** Open-source solar site-level forecasting
- **Usage in Feldtheorie:** API/CLI patterns, Pydantic configuration examples
- **Original Authors:** © Open Climate Fix contributors
- **License:** MIT (see repository for full license text)

---

## Data Sources

### ICON-EU (DWD)
- **Provider:** Deutscher Wetterdienst (DWD)
- **Access:** Via Open Climate Fix HuggingFace Datasets
- **Dataset:** [huggingface.co/datasets/openclimatefix/dwd-icon-eu](https://huggingface.co/datasets/openclimatefix/dwd-icon-eu)
- **License:** Open data (check provider terms)

### Nimrod/MRMS Radar Data
- **Providers:** MetOffice (Nimrod), NOAA (MRMS)
- **Access:** Via Open Climate Fix infrastructure
- **License:** Check respective provider terms

---

## Attribution Requirements

As per OCF's MIT license, we provide the following attribution:

> **Original code portions © Open Climate Fix contributors**
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.

**Full OCF MIT License:** See individual repositories for complete license text.

---

## Other Dependencies

The Feldtheorie project also relies on the following open-source libraries:

- **xarray** (Apache 2.0)
- **dask** (BSD 3-Clause)
- **zarr** (MIT)
- **fsspec** (BSD 3-Clause)
- **pandas** (BSD 3-Clause)
- **numpy** (BSD 3-Clause)

See `requirements-ocf.txt` for full dependency list.

---

## Contributing

If you'd like to contribute to Feldtheorie or report issues with OCF integration, please see:

- **Issues:** [github.com/GenesisAeon/Feldtheorie/issues](https://github.com/GenesisAeon/Feldtheorie/issues)
- **Pull Requests:** [github.com/GenesisAeon/Feldtheorie/pulls](https://github.com/GenesisAeon/Feldtheorie/pulls)

---

## Citation

If you use Feldtheorie in your research, please cite:

```bibtex
@software{feldtheorie2025,
  title={Feldtheorie: Universal Threshold Activation Criticality Framework},
  author={Römer, Johann and Contributors},
  year={2025},
  url={https://github.com/GenesisAeon/Feldtheorie},
  note={Data pipelines portions inspired by Open Climate Fix (MIT)}
}
```

---

**Created:** 2025-11-12
**Maintained by:** Johann Römer, Claude Code
**License:** See LICENSE file in repository root

*"Standing on the shoulders of giants - with gratitude to Open Climate Fix."* 🌍✨
