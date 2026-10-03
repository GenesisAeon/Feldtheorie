"""Browser smoke test of both views (index.html, lab.html) against the running
local service -- real clicks and slider changes in headless Edge, driven over
the Chrome DevTools Protocol with a minimal stdlib websocket client (no new
installation). Local tool, not part of pytest (needs Edge and a free port).

It starts serve.py with a SEPARATE explore folder (--explore-dir), runs the
steps below, records every JS exception/console error, takes screenshots and
checks the stored explorative files and that benchmark files are unchanged.

    python experiments/mandala_memory/tools/browser_smoke.py --out D:/mandala/mandala-memory-results/<check-folder>
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
REPO = EXP.parents[1]
EDGE = Path(r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
BENCH = Path(r"D:/mandala/mandala-memory-results")


class WS:
    """Minimal RFC 6455 client: text frames, client masking, no extensions."""

    def __init__(self, url: str):
        assert url.startswith("ws://")
        host_port, path = url[5:].split("/", 1)
        host, port = host_port.split(":")
        self.s = socket.create_connection((host, int(port)), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{path} HTTP/1.1\r\nHost: {host_port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            resp += self.s.recv(1)
        if b" 101 " not in resp.split(b"\r\n")[0]:
            raise RuntimeError(resp.decode(errors="replace"))
        self.id = 0
        self.events = []

    def _recv_exact(self, n):
        b = b""
        while len(b) < n:
            chunk = self.s.recv(n - len(b))
            if not chunk:
                raise ConnectionError("websocket closed")
            b += chunk
        return b

    def _recv_msg(self) -> dict:
        data = b""
        while True:
            h = self._recv_exact(2)
            fin, op, ln = h[0] & 0x80, h[0] & 0x0F, h[1] & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._recv_exact(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._recv_exact(8))[0]
            payload = self._recv_exact(ln)
            if op == 0x9:                                   # ping -> pong
                self._send(payload, 0xA)
                continue
            data += payload
            if fin:
                return json.loads(data.decode("utf-8"))

    def _send(self, payload: bytes, op: int = 0x1):
        mask = os.urandom(4)
        n = len(payload)
        head = bytes([0x80 | op]) + (bytes([0x80 | n]) if n < 126 else
                                     bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else
                                     bytes([0x80 | 127]) + struct.pack(">Q", n))
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def call(self, method: str, **params):
        self.id += 1
        my = self.id
        self._send(json.dumps({"id": my, "method": method, "params": params}).encode())
        while True:
            m = self._recv_msg()
            if m.get("id") == my:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
            self.events.append(m)


def js(ws: WS, expr: str):
    r = ws.call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
    if "exceptionDetails" in r:
        raise RuntimeError(f"JS error in {expr!r}: {r['exceptionDetails']}")
    return r["result"].get("value")


def wait_for(ws: WS, expr: str, timeout: float = 15.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        v = js(ws, expr)
        if v:
            return v
        time.sleep(0.15)
    raise TimeoutError(f"{expr}  (page: {js(ws, 'location.href')}, body: {js(ws, 'document.body ? document.body.innerText.slice(0, 200) : null')!r})")


def bench_state():
    files = [p for d in ("smoke", "research", "m9") for p in (BENCH / d).glob("*.json")] if BENCH.exists() else []
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ui", type=Path, default=Path(r"D:/mandala/unified-mandala/experiments/memory_lab"))
    ap.add_argument("--repo", type=Path, default=REPO, help="Feldtheorie checkout whose serve.py is started")
    a = ap.parse_args(argv)
    if a.out.drive.upper().startswith("C"):
        raise SystemExit("--out must not be on C:")
    out, explore = a.out, a.out / "explore"
    out.mkdir(parents=True, exist_ok=True)
    before = bench_state()
    port, dbg = free_port(), free_port()
    env = {**os.environ, "PYTHONPATH": str(a.repo), "PYTHONDONTWRITEBYTECODE": "1", "OPENBLAS_NUM_THREADS": "2",
           "TMP": r"D:/mandala/.tmp/mandala-memory", "TEMP": r"D:/mandala/.tmp/mandala-memory"}
    srv = subprocess.Popen([sys.executable, "-m", "experiments.mandala_memory.serve", "--port", str(port), "--ui", str(a.ui),
                            "--explore-dir", str(explore)], cwd=a.repo, env=env)
    edge = None
    steps, ok = [], True

    def step(name, cond, detail=""):
        nonlocal ok
        steps.append({"step": name, "passed": bool(cond), "detail": detail})
        ok = ok and bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")

    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/preset", timeout=2)
                break
            except OSError:
                time.sleep(0.1)
        edge = subprocess.Popen([str(EDGE), "--headless=new", "--disable-gpu", f"--remote-debugging-port={dbg}",
                                 f"--user-data-dir={out / 'edge-profile'}", "--window-size=1400,2200", "about:blank"])
        page = None
        for _ in range(200):
            try:
                targets = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{dbg}/json", timeout=2).read())
                page = next(t for t in targets if t["type"] == "page" and t.get("url") == "about:blank")
                break
            except (OSError, StopIteration):
                time.sleep(0.2)
        if page is None:
            raise RuntimeError("headless Edge did not open its debugging port within 40 s")
        ws = WS(page["webSocketDebuggerUrl"])
        for dom in ("Runtime", "Page", "Log"):
            ws.call(f"{dom}.enable")
        base = f"http://127.0.0.1:{port}"

        def shot(name):
            data = ws.call("Page.captureScreenshot", format="png", captureBeyondViewport=True)["data"]
            (out / name).write_bytes(base64.b64decode(data))

        # --- M6 comparison view -------------------------------------------------
        ws.call("Page.navigate", url=base + "/?autostart")
        txt = wait_for(ws, "(()=>{const t=document.querySelector('#result')?.innerText||''; return t.includes('Run-ID') ? t : ''})()")
        step("index: autostart comparison shows run id and Bayes accuracy", "68.3 %" in txt, txt.split("\n")[2][:90] if "\n" in txt else txt[:90])
        js(ws, "document.querySelector('#delay').value=4; document.querySelector('#delay').dispatchEvent(new Event('input')); document.querySelector('#start').click(); true")
        txt = wait_for(ws, "(()=>{const t=document.querySelector('#result').innerText; return t.includes('93.5 %') ? t : ''})()")
        step("index: delay slider 4 + start -> 93.5 %", bool(txt))
        n_logs = js(ws, "document.querySelectorAll('#log li').length")
        step("index: session log lists both runs", n_logs == 2, f"{n_logs} entries")
        shot("index_after_two_runs.png")

        # --- M8 knob lab ----------------------------------------------------------
        ws.call("Page.navigate", url=base + "/lab.html?autostart")
        s = wait_for(ws, "(()=>{const t=document.querySelector('#summary').innerText; return t.includes('Run-ID') ? t : ''})()")
        step("lab: autostart benchmark -> D = 6", "D = 6 Schritte" in s)
        step("lab: curve drawn (current, reference, bound)", js(ws, "document.querySelectorAll('#curve path').length") >= 3)

        def set_and_wait(selector, value, event="change"):
            prev = js(ws, "document.querySelectorAll('#log li').length")
            js(ws, f"(()=>{{const e=document.querySelector('{selector}'); e.value={json.dumps(value)}; e.dispatchEvent(new Event('input')); e.dispatchEvent(new Event('{event}')); return true}})()")
            wait_for(ws, f"document.querySelectorAll('#log li').length > {prev}")
            return js(ws, "document.querySelector('#summary').innerText")

        s = set_and_wait("#c", "0.05")
        d_c005 = int(s.split("D = ")[1].split(" ")[0])
        step("lab: c 0.25 -> 0.05 (live) lengthens memory", d_c005 > 6, f"D = {d_c005}")
        s = set_and_wait("#readout", "sum")
        step("lab: readout = sum -> no memory ('keine')", "D = keine" in s)
        set_and_wait("#readout", "full")
        js(ws, "document.querySelector('#bench').click(); true")
        time.sleep(1.0)
        s = wait_for(ws, "(()=>{const t=document.querySelector('#summary').innerText; return t.includes('D = 6 Schritte') ? t : ''})()")
        step("lab: 'Benchmark-Werte' resets to D = 6", bool(s))
        prev = js(ws, "document.querySelectorAll('#log li').length")
        js(ws, "document.querySelector('#pD svg [data-e]').dispatchEvent(new MouseEvent('click', {bubbles: true})); true")
        wait_for(ws, f"document.querySelectorAll('#log li').length > {prev}")
        step("lab: click on an edge ablates it (count 1, dashed edge drawn)",
             js(ws, "document.querySelector('#abCount').textContent") == "1" and js(ws, "document.querySelectorAll('#pD .edge.ablated').length") == 1)
        s = set_and_wait("#clear", "module")
        step("lab: clear one module recomputes", "Run-ID" in s)
        js(ws, "document.querySelector('#t').value=3; document.querySelector('#t').dispatchEvent(new Event('input')); true")
        step("lab: time slider shows phase text", "d = 2" in js(ws, "document.querySelector('#phase').textContent"))
        js(ws, "document.querySelector('#pin').click(); true")
        step("lab: pin keeps a curve", js(ws, "document.querySelectorAll('#curve .c-pin').length") == 1)
        shot("lab_after_interaction.png")
        def is_error(e):
            return e.get("method") == "Runtime.exceptionThrown" or (
                e.get("method") == "Log.entryAdded" and e["params"]["entry"]["level"] == "error"
                and "favicon" not in e["params"]["entry"].get("url", ""))

        js(ws, "true")                                     # flush pending events
        errors = [e for e in ws.events if is_error(e)]
        step("no JS exceptions or console errors during normal use", not errors, json.dumps(errors)[:300] if errors else "")
        n_before = len(ws.events)
        bad_status = js(ws, "fetch('/api/lab',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({knobs:{gamma:2}})}).then(r=>r.status)")
        js(ws, "true")
        after = [e for e in ws.events[n_before:] if is_error(e)]
        step("lab: invalid knob from the browser -> HTTP 400, only the expected network error",
             bad_status == 400 and all(e.get("method") == "Log.entryAdded" and e["params"]["entry"].get("source") == "network"
                                       and e["params"]["entry"].get("url", "").endswith("/api/lab") for e in after),
             f"{len(after)} expected network error entry")
        n_ui_runs = js(ws, "document.querySelectorAll('#log li').length")
    finally:
        if edge:
            # the Edge launcher may exit and leave its children orphaned: end every msedge process
            # that uses THIS run's private profile folder (and nothing else)
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(edge.pid)], capture_output=True)
            prof = str(out / "edge-profile").replace("/", "\\").replace("'", "''")
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process -Filter \"Name='msedge.exe'\" | Where-Object { $_.CommandLine -and "
                            f"$_.CommandLine.Replace('/', '\\').Contains('{prof}') }} | ForEach-Object {{ try {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }} catch {{}} }}"],
                           capture_output=True)
        srv.terminate()
        try:
            srv.wait(timeout=10)
        except subprocess.TimeoutExpired:
            srv.kill()

    lines = [json.loads(l) for l in (explore / "protocol.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    labs = [l for l in lines if l.get("kind") == "lab"]
    files_ok = all((explore / f"{l['run_id']}.json").is_file() for l in lines)
    step("storage: every request logged in the SEPARATE explore folder with its own file",
         files_ok and len(lines) == 2 + n_ui_runs and len(labs) == n_ui_runs,
         f"{len(lines)} protocol lines ({len(labs)} lab), {n_ui_runs} lab runs in the UI log + 2 comparison runs; the rejected request is not logged")
    step("storage: benchmark and M9 result files unchanged (SHA-256)", bench_state() == before, f"{len(before)} files")
    report = {"passed": ok, "steps": steps, "explore_dir": str(explore), "ui": str(a.ui), "repo": str(a.repo),
              "created_unix": time.time()}
    (out / "browser_smoke.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"browser smoke: {'PASSED' if ok else 'FAILED'} ({sum(s['passed'] for s in steps)}/{len(steps)})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
