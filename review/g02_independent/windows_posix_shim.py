"""Import-time shim so runner.py (Linux/POSIX-only: `resource`, SIGALRM) can be
imported and its pure logic exercised on native Windows, for this review only.

This does NOT test the real POSIX resource enforcement (RLIMIT_AS virtual
memory capping, the 30-minute wall-clock SIGALRM abort) -- those stay
genuinely unverified on this machine. It only unblocks the module-level
`import resource` / `signal.SIGALRM` references so the rest of runner.py's
logic (checkpointing, hashing, aggregation, review-gate checks, etc.) can
actually run and be checked against test_predictive.py's real assertions,
instead of being reviewed by eye only.

Import this BEFORE importing `runner`, `model`, or `test_predictive`.
"""
import sys
import types
import signal as _signal

if "resource" not in sys.modules:
    fake_resource = types.ModuleType("resource")
    fake_resource.RLIMIT_AS = 9999
    fake_resource.RLIM_INFINITY = -1
    fake_resource.RUSAGE_SELF = 0
    _rlimits = {fake_resource.RLIMIT_AS: (fake_resource.RLIM_INFINITY, fake_resource.RLIM_INFINITY)}

    def _getrlimit(which):
        return _rlimits.get(which, (fake_resource.RLIM_INFINITY, fake_resource.RLIM_INFINITY))

    def _setrlimit(which, limits):
        _rlimits[which] = limits

    class _Usage:
        ru_maxrss = 0

    def _getrusage(who):
        return _Usage()

    fake_resource.getrlimit = _getrlimit
    fake_resource.setrlimit = _setrlimit
    fake_resource.getrusage = _getrusage
    sys.modules["resource"] = fake_resource

if not hasattr(_signal, "SIGALRM"):
    _signal.SIGALRM = 9998
if not hasattr(_signal, "ITIMER_REAL"):
    _signal.ITIMER_REAL = 0
if not hasattr(_signal, "setitimer"):
    _signal.setitimer = lambda *a, **k: None
_real_getsignal = getattr(_signal, "getsignal", None)
_real_signal_fn = _signal.signal


def _safe_getsignal(sig):
    if sig == _signal.SIGALRM and _real_getsignal is not None:
        try:
            return _real_getsignal(sig)
        except (ValueError, OSError):
            return None
    return _real_getsignal(sig) if _real_getsignal else None


def _safe_signal(sig, handler):
    if sig == _signal.SIGALRM:
        return None  # no-op: this review does not exercise the real alarm delivery
    return _real_signal_fn(sig, handler)


_signal.getsignal = _safe_getsignal
_signal.signal = _safe_signal
