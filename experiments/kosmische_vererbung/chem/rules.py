"""Synthetic yield rules for V5: how star formation reacts to local Z.

Every rule maps the birth metallicity Z of the gas in a zone to a YieldModel
(net convention, metals carried as O, H balances). All numbers are synthetic
and declared in protocol_v5.json; they are not stellar physics.

* ``linear``      Z-blind, constant net yield: the null model. With star
                  formation proportional to gas mass, the mean metallicity is
                  an exact sufficient statistic (lumpable).
* ``pop3``        threshold rule: Z < z_crit forms "Pop III" parcels with a
                  higher yield and shorter lifetime, otherwise "Pop II".
* ``saturation``  Z-blind but saturated ejecta metallicity, no Pop III
                  special case (counter-model requested by the SCF session):
                  net O = R * min(y, Z_max - Z), clipped at 0.
"""
from __future__ import annotations

from .kernel import YieldModel


def _model(name, return_fraction, net_o, lifetime):
    return YieldModel(name, return_fraction, {"H": -net_o, "O": net_o}, lifetime)


def make_rule(spec: dict):
    kind = spec["kind"]
    R = spec["return_fraction"]
    if kind == "linear":
        m = _model("linear", R, spec["net_o"], spec["lifetime_myr"])
        return lambda z: m
    if kind == "pop3":
        pop3 = _model("pop3", R, spec["pop3_net_o"], spec["pop3_lifetime_myr"])
        pop2 = _model("pop2", R, spec["pop2_net_o"], spec["pop2_lifetime_myr"])
        z_crit = spec["z_crit"]
        return lambda z: pop3 if z < z_crit else pop2
    if kind == "saturation":
        y, z_max, lifetime = spec["y"], spec["z_max"], spec["lifetime_myr"]
        return lambda z: _model("saturation", R, R * min(y, max(z_max - z, 0.0)), lifetime)
    raise ValueError(f"unknown rule kind {kind!r}")
