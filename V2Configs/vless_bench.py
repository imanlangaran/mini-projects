#!/usr/bin/env python3
"""
VLESS Proxy Benchmark — Automate subscription fetch, real-delay test,
download-speed test, and ranking.

Usage:
    python3 vless_bench.py <subscription_url>
    python3 vless_bench.py <subscription_url> --speedtest    # also run speed tests
    python3 vless_bench.py <subscription_url> --max 20       # test only first 20
    python3 vless_bench.py <file_with_vless_links.txt>       # local file instead

What it does:
  1. Fetch subscription URL (base64-decoded) OR read a local file of vless:// links
  2. For each config, start xray locally, measure REAL HTTP latency (not TCP ping)
     via an actual HTTPS request through the SOCKS5 inbound.
  3. Filter out dead/unreachable configs (timeout / connection error).
  4. (Optional) Download-speed test each surviving config.
  5. Output a ranked table sorted by latency, then speed.

Requires: xray-core in PATH, Python 3.9+, curl.
"""

import argparse
import atexit
import base64
import concurrent.futures
import json
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Config defaults
# ---------------------------------------------------------------------------
SOCKS_PORT = 10888
HTTP_PORT = 10889
BASE_SOCKS_PORT = 10008          # base port for parallel workers
BASE_HTTP_PORT = 10009           # base HTTP port for parallel workers
XRAY_EXEC = os.environ.get("XRAY_EXEC", "xray")
LATENCY_TIMEOUT = 10       # seconds per config for real-delay test
SPEEDTEST_TIMEOUT = 30     # seconds per config for download test
PARALLEL_LATENCY = 5       # number of parallel latency tests
PARALLEL_SPEED = 3         # number of parallel speed tests
SPEEDTEST_URL = os.environ.get(
    "SPEEDTEST_URL",
    "https://speedtest.selectel.ru/10MB",
    # Alternative: "http://speedtest.tele2.net/10MB.zip"
)
LATENCY_TARGET = os.environ.get("LATENCY_TARGET", "https://www.google.com/generate_204")
PROBE_TIMEOUT = 3          # how long to wait for xray to start listening
SOCKET_READY_WAIT = 0.3    # poll interval when waiting for port

# ---------------------------------------------------------------------------
# Global xray process tracking (for Ctrl+C cleanup)
# ---------------------------------------------------------------------------
_xray_procs: list[subprocess.Popen] = []
_xray_procs_lock = threading.Lock()
_cleanup_registered = False


def _track_proc(proc: subprocess.Popen) -> None:
    """Register an xray process for cleanup on exit."""
    global _cleanup_registered
    with _xray_procs_lock:
        if not _cleanup_registered:
            _cleanup_registered = True
            atexit.register(_kill_all_xray)
        _xray_procs.append(proc)


def _untrack_proc(proc: subprocess.Popen) -> None:
    """Remove a process from the tracking list."""
    with _xray_procs_lock:
        try:
            _xray_procs.remove(proc)
        except ValueError:
            pass


def _kill_all_xray() -> None:
    """Kill all tracked xray processes (called on exit / signal)."""
    with _xray_procs_lock:
        for proc in list(_xray_procs):
            try:
                proc.kill()
                proc.wait(timeout=3)
            except Exception:
                pass
        _xray_procs.clear()


def _sighandler(signum, frame) -> None:
    """Signal handler that cleans up xray processes and lets KeyboardInterrupt propagate."""
    print("\n  Interrupted — killing xray processes...", file=sys.stderr)
    _kill_all_xray()
    raise KeyboardInterrupt()


@dataclass
class VlessConfig:
    """Parsed VLESS config from a share link."""
    link: str
    remark: str = ""
    uuid: str = ""
    host: str = ""
    port: int = 0
    protocol: str = "vless"

    # stream settings
    network: str = "tcp"          # tcp, kcp, ws, http, quic, grpc
    security: str = "none"        # none, tls, xtls, reality
    encryption: str = "none"
    flow: str = ""

    # tls / reality
    sni: str = ""
    fp: str = ""                  # fingerprint
    pbk: str = ""                 # public key (reality)
    sid: str = ""                 # short id (reality)
    spx: str = ""                 # spider x (reality)

    # websocket
    ws_path: str = ""
    ws_host: str = ""

    # grpc
    grpc_service_name: str = ""

    # tcp
    header_type: str = "none"

    # result fields
    latency_s: Optional[float] = None
    latency_error: Optional[str] = None
    speed_mbps: Optional[float] = None
    speed_error: Optional[str] = None

    def display_name(self) -> str:
        if self.remark:
            return self.remark
        return f"{self.host}:{self.port}"


# ---------------------------------------------------------------------------
# Parse VLESS subscription / share links
# ---------------------------------------------------------------------------

def parse_vless_uri(uri: str) -> Optional[VlessConfig]:
    """Parse a 'vless://...' URI into a VlessConfig."""
    if not uri.startswith("vless://"):
        return None

    cfg = VlessConfig(link=uri)

    # Strip trailing fragment (remark)
    fragment = ""
    if "#" in uri:
        uri, frag_part = uri.split("#", 1)
        try:
            fragment = urllib.parse.unquote(frag_part)
        except Exception:
            fragment = frag_part

    parsed = urllib.parse.urlparse(uri)
    # userinfo = uuid
    userinfo = parsed.username or ""
    cfg.uuid = userinfo

    # host:port
    cfg.host = parsed.hostname or ""
    try:
        cfg.port = parsed.port or 0
    except ValueError:
        return None

    # Query params
    qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)

    def first(key: str, default: str = "") -> str:
        vals = qs.get(key, [])
        return vals[0].strip() if vals else default

    cfg.remark = fragment
    cfg.network = first("type", "tcp").lower()
    cfg.security = first("security", "none").lower()
    cfg.encryption = first("encryption", "none")
    cfg.flow = first("flow")
    cfg.sni = first("sni")
    cfg.fp = first("fp")
    cfg.pbk = first("pbk")
    cfg.sid = first("sid")
    cfg.spx = first("spx")
    cfg.ws_path = first("path")
    cfg.ws_host = first("host")
    cfg.grpc_service_name = first("serviceName")
    cfg.header_type = first("headerType", "none")

    return cfg


def fetch_subscription(url_or_path: str) -> list[str]:
    """Fetch raw subscription data and return list of VMess/VLESS/SS links."""
    raw = ""
    if os.path.isfile(url_or_path):
        with open(url_or_path) as f:
            raw = f.read()
    elif url_or_path.startswith(("http://", "https://")):
        req = urllib.request.Request(
            url_or_path,
            headers={"User-Agent": "vless-bench/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    else:
        # Try as file first
        if os.path.exists(url_or_path):
            with open(url_or_path) as f:
                raw = f.read()
        else:
            raise ValueError(f"Not a file or URL: {url_or_path}")

    raw = raw.strip()

    # Try base64 decode (standard subscription format)
    lines = []
    if re.fullmatch(r"[A-Za-z0-9+/=]+", raw) and len(raw) > 50:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", errors="replace")
            lines = [l.strip() for l in decoded.splitlines() if l.strip()]
        except Exception:
            pass

    # If that didn't work, try splitting raw lines
    if not lines:
        lines = [l.strip() for l in raw.splitlines() if l.strip()]

    # If still empty, maybe it's a single-line base64 blob without newlines in decoded
    if not lines:
        try:
            decoded = base64.b64decode(raw).decode("utf-8", errors="replace")
            # May still be one long line, split by newline or by vless://
            lines = re.findall(r"vless://\S+", decoded) or [l.strip() for l in decoded.splitlines() if l.strip()]
        except Exception:
            lines = [raw]

    return lines


def parse_all_configs(lines: list[str], debug: bool = False) -> list[VlessConfig]:
    configs = []
    for line in lines:
        for uri in re.findall(r"vless://\S+", line):
            try:
                cfg = parse_vless_uri(uri)
                if cfg and cfg.uuid and cfg.host and cfg.port:
                    configs.append(cfg)
                elif debug:
                    print(f"  [debug] Skipped (missing fields): {uri}", file=sys.stderr)
            except Exception as e:
                if debug:
                    print(f"  [debug] Parse error: {e}", file=sys.stderr)
                    print(f"  [debug] Raw line: {line[:200]}", file=sys.stderr)
    return configs


# ---------------------------------------------------------------------------
# Build xray JSON config for a single outbound
# ---------------------------------------------------------------------------

def build_xray_json(cfg: VlessConfig, socks_port: int = SOCKS_PORT, http_port: int = HTTP_PORT) -> dict:
    """Generate an xray JSON config that runs one outbound + SOCKS inbound."""
    outbound = {
        "protocol": "vless",
        "settings": {
            "vnext": [{
                "address": cfg.host,
                "port": cfg.port,
                "users": [{
                    "id": cfg.uuid,
                    "encryption": cfg.encryption or "none",
                }]
            }]
        },
        "streamSettings": {
            "network": cfg.network,
        },
        "tag": "proxy",
    }

    # Flow (Vision, etc.)
    if cfg.flow:
        outbound["settings"]["vnext"][0]["users"][0]["flow"] = cfg.flow

    # Stream settings details
    sset = outbound["streamSettings"]

    # Security (tls, xtls, reality)
    if cfg.security in ("tls", "xtls", "reality"):
        sset["security"] = cfg.security

        if cfg.security == "reality":
            reality_settings = {}
            if cfg.sni:
                reality_settings["serverName"] = cfg.sni
            if cfg.fp:
                reality_settings["fingerprint"] = cfg.fp
            if cfg.pbk:
                reality_settings["publicKey"] = cfg.pbk
            if cfg.sid:
                reality_settings["shortId"] = cfg.sid
            if cfg.spx:
                reality_settings["spiderX"] = cfg.spx
            if reality_settings:
                sset["realitySettings"] = reality_settings
        else:
            # TLS or XTLS
            tls_settings = {}
            if cfg.sni:
                tls_settings["serverName"] = cfg.sni
            if cfg.fp:
                tls_settings["fingerprint"] = cfg.fp
            if tls_settings:
                sset["tlsSettings"] = tls_settings
    elif cfg.security == "none":
        sset["security"] = "none"

    # Network-specific settings
    if cfg.network == "ws":
        ws = {}
        if cfg.ws_path:
            ws["path"] = cfg.ws_path
        if cfg.ws_host:
            ws["headers"] = {"Host": cfg.ws_host}
        if ws:
            sset["wsSettings"] = ws

    elif cfg.network == "grpc":
        grpc = {}
        if cfg.grpc_service_name:
            grpc["serviceName"] = cfg.grpc_service_name
        sset["grpcSettings"] = grpc

    elif cfg.network == "tcp":
        if cfg.header_type and cfg.header_type != "none":
            sset["tcpSettings"] = {
                "header": {
                    "type": cfg.header_type
                }
            }

    elif cfg.network == "kcp":
        if cfg.header_type and cfg.header_type != "none":
            sset["kcpSettings"] = {
                "header": {
                    "type": cfg.header_type
                }
            }

    return {
        "log": {
            "loglevel": "warning",
            "access": "none",
        },
        "inbounds": [
            {
                "port": socks_port,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": False,
                },
                "tag": "socks-in",
            },
            {
                "port": http_port,
                "listen": "127.0.0.1",
                "protocol": "http",
                "settings": {},
                "tag": "http-in",
            },
        ],
        "outbounds": [
            outbound,
            {
                "protocol": "freedom",
                "tag": "direct",
            },
        ],
        "routing": {
            "domainStrategy": "AsIs",
            "rules": [
                {
                    "type": "field",
                    "inboundTag": ["socks-in", "http-in"],
                    "outboundTag": "proxy",
                },
            ],
        },
        "dns": {
            "servers": ["https://dns.google/dns-query"],
        },
    }


# ---------------------------------------------------------------------------
# Run a single test
# ---------------------------------------------------------------------------

def port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    """Check if a TCP port is accepting connections."""
    import socket
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except (OSError, socket.error):
        return False


def wait_for_port(host: str, port: int, timeout: float = PROBE_TIMEOUT) -> bool:
    """Wait up to `timeout` seconds for a port to open."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_open(host, port, SOCKET_READY_WAIT):
            return True
        time.sleep(SOCKET_READY_WAIT)
    return False


def measure_latency(
    xray_config: dict, tag: str, latency_target: str = LATENCY_TARGET,
    socks_port: int = SOCKS_PORT,
) -> tuple[Optional[float], Optional[str]]:
    """
    Start xray, measure real HTTP latency through it, then stop xray.
    Returns (latency_seconds, error_string).
    """
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(xray_config, tmp)
    tmp.close()
    config_path = tmp.name

    proc = None
    try:
        xray_bin = os.path.expanduser("~/.local/bin/xray") if "/" not in XRAY_EXEC else XRAY_EXEC
        proc = subprocess.Popen(
            [xray_bin, "run", "-c", config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _track_proc(proc)

        # Wait for SOCKS port to open
        if not wait_for_port("127.0.0.1", socks_port):
            proc.kill()
            proc.wait(timeout=5)
            return None, f"{tag}: xray did not start in {PROBE_TIMEOUT}s (port {socks_port})"

        # Real delay: curl through SOCKS5 to a real HTTPS endpoint
        cmd = [
            "curl", "-x", f"socks5h://127.0.0.1:{socks_port}",
            "-o", "/dev/null",
            "-s", "-w", "%{time_total}",
            "--connect-timeout", str(LATENCY_TIMEOUT - 2),
            "--max-time", str(LATENCY_TIMEOUT),
            latency_target,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=LATENCY_TIMEOUT + 2)

        if result.returncode != 0:
            err = result.stderr.strip() or f"curl exit code {result.returncode}"
            return None, f"{tag}: {err}"

        try:
            latency = float(result.stdout.strip())
        except ValueError:
            return None, f"{tag}: unexpected curl output: {result.stdout.strip()[:100]}"

        return latency, None

    except subprocess.TimeoutExpired:
        return None, f"{tag}: timed out after {LATENCY_TIMEOUT}s"
    except Exception as e:
        return None, f"{tag}: {e}"
    finally:
        if proc:
            try:
                _untrack_proc(proc)
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                pass
        # Clean config file
        try:
            os.unlink(config_path)
        except Exception:
            pass


def measure_speed(
    xray_config: dict, tag: str, speedtest_url: str = SPEEDTEST_URL,
    socks_port: int = SOCKS_PORT,
) -> tuple[Optional[float], Optional[str]]:
    """
    Start xray, download a test file through it, measure throughput.
    Returns (speed_mbps, error_string).
    """
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(xray_config, tmp)
    tmp.close()
    config_path = tmp.name

    proc = None
    try:
        xray_bin = os.path.expanduser("~/.local/bin/xray") if "/" not in XRAY_EXEC else XRAY_EXEC
        proc = subprocess.Popen(
            [xray_bin, "run", "-c", config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _track_proc(proc)

        if not wait_for_port("127.0.0.1", socks_port):
            proc.kill()
            proc.wait(timeout=5)
            return None, f"{tag}: xray did not start"

        # Download through proxy and measure speed
        cmd = [
            "curl", "-x", f"socks5h://127.0.0.1:{socks_port}",
            "-o", "/dev/null",
            "-s", "-w", "%{speed_download}",
            "--connect-timeout", "10",
            "--max-time", str(SPEEDTEST_TIMEOUT),
            speedtest_url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=SPEEDTEST_TIMEOUT + 5)
        if result.returncode != 0:
            err = result.stderr.strip() or f"curl exit code {result.returncode}"
            return None, f"{tag}: {err}"

        try:
            speed_bps = float(result.stdout.strip())  # bytes per second from curl
            speed_mbps = (speed_bps * 8) / 1_000_000   # convert to Mbps
        except ValueError:
            return None, f"{tag}: unexpected curl output: {result.stdout.strip()[:100]}"

        return speed_mbps, None

    except subprocess.TimeoutExpired:
        return None, f"{tag}: speed test timed out"
    except Exception as e:
        return None, f"{tag}: {e}"
    finally:
        if proc:
            try:
                _untrack_proc(proc)
                proc.kill()
                proc.wait(timeout=5)
            except Exception:
                pass
        try:
            os.unlink(config_path)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def banner():
    print("=" * 70)
    print("  VLESS Config Benchmark")
    print("  Real HTTP delay (not TCP ping) + download speed test")
    print("=" * 70)


def print_results(configs: list[VlessConfig], show_speed: bool):
    """Print ranked results table."""
    headers = ["#", "Name", "Server", "Port", "Protocol", "Latency"]
    if show_speed:
        headers.append("Speed")
    headers.append("Status")

    col_widths = [3, 28, 20, 6, 6, 10]
    if show_speed:
        col_widths.append(10)
    col_widths.append(12)

    sep = " | ".join

    def fmt_row(vals):
        padded = []
        for i, v in enumerate(vals):
            w = col_widths[i] if i < len(col_widths) else 0
            padded.append(str(v).ljust(w) if i == 0 else str(v).rjust(w) if i >= 2 else str(v).ljust(w))
        return sep(padded)

    print()
    print(fmt_row(headers))
    print("-" * len(fmt_row(headers)))

    for idx, cfg in enumerate(configs, 1):
        net = cfg.network.upper()
        if cfg.security in ("tls", "xtls", "reality"):
            net += f"+{cfg.security[:2].upper()}"

        if cfg.latency_s is not None:
            lat_str = f"{cfg.latency_s*1000:.0f} ms"
            status = "✓"
        else:
            lat_str = "✗"
            status = cfg.latency_error or "FAIL"

        speed_str = ""
        if show_speed:
            if cfg.speed_mbps is not None:
                speed_str = f"{cfg.speed_mbps:.1f} Mbps"
            elif cfg.speed_error:
                speed_str = f"✗"
            else:
                speed_str = "-"

        row = [
            str(idx),
            cfg.display_name()[:col_widths[1]],
            f"{cfg.host}:{cfg.port}",
            str(cfg.port),
            net,
            lat_str,
        ]
        if show_speed:
            row.append(speed_str)
        row.append(status)
        print(fmt_row(row))

    # Summary
    total = len(configs)
    alive = sum(1 for c in configs if c.latency_s is not None)
    print()
    print(f"  Total: {total}  |  Reachable: {alive}  |  Dead: {total - alive}")
    if show_speed and alive:
        with_speed = sum(1 for c in configs if c.speed_mbps is not None)
        print(f"  Speed-tested: {with_speed}")


def _worker_ports(worker_id: int, base_socks: int = BASE_SOCKS_PORT,
                  base_http: int = BASE_HTTP_PORT) -> tuple[int, int]:
    """Return (socks_port, http_port) for a given worker ID."""
    return base_socks + worker_id * 2, base_http + worker_id * 2


def _latency_worker(cfg: VlessConfig, latency_target: str, worker_id: int,
                    idx: int) -> tuple[int, Optional[float], Optional[str]]:
    """Test latency for one config. Returns (idx, latency_s, error)."""
    socks_port, http_port = _worker_ports(worker_id)
    xray_cfg = build_xray_json(cfg, socks_port=socks_port, http_port=http_port)
    lat, err = measure_latency(xray_cfg, cfg.display_name(),
                               latency_target=latency_target, socks_port=socks_port)
    return idx, lat, err


def _speed_worker(cfg: VlessConfig, speedtest_url: str, worker_id: int,
                  idx: int) -> tuple[int, Optional[float], Optional[str]]:
    """Test speed for one config. Returns (idx, speed_mbps, error)."""
    socks_port, http_port = _worker_ports(worker_id)
    xray_cfg = build_xray_json(cfg, socks_port=socks_port, http_port=http_port)
    speed, err = measure_speed(xray_cfg, cfg.display_name(),
                               speedtest_url=speedtest_url, socks_port=socks_port)
    return idx, speed, err


def main():
    parser = argparse.ArgumentParser(
        description="VLESS Proxy Benchmark — real HTTP delay & speed test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("source", help="Subscription URL or local file with vless:// links")
    parser.add_argument("--speedtest", "-s", action="store_true", help="Run download speed tests on reachable configs")
    parser.add_argument("--max", "-m", type=int, default=0, help="Max configs to test (0 = all)")
    parser.add_argument("--latency-target", default=LATENCY_TARGET, help=f"URL for latency test (default: {LATENCY_TARGET})")
    parser.add_argument("--speedtest-url", default=SPEEDTEST_URL, help=f"URL for speed test download (default: {SPEEDTEST_URL})")
    parser.add_argument("--parallel-latency", "-pl", type=int, default=PARALLEL_LATENCY,
                        help=f"Number of parallel latency tests (default: {PARALLEL_LATENCY})")
    parser.add_argument("--parallel-speed", "-ps", type=int, default=PARALLEL_SPEED,
                        help=f"Number of parallel speed tests (default: {PARALLEL_SPEED})")
    parser.add_argument("--output", "-o", nargs="?", const="-", default=None,
                        help='Output sorted alive configs. Use "-" to print to terminal, '
                             'or a file path to write (default: alive_configs.txt)')
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Print debug info for skipped/invalid configs")

    args = parser.parse_args()

    # Install signal handler for Ctrl+C cleanup
    signal.signal(signal.SIGINT, _sighandler)

    banner()

    # 1. Fetch
    print("\n[1/4] Fetching subscription...")
    try:
        lines = fetch_subscription(args.source)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"  Got {len(lines)} raw line(s)")

    # 2. Parse
    print("\n[2/4] Parsing VLESS configs...")
    configs = parse_all_configs(lines, debug=args.debug)
    if not configs:
        print("  No valid VLESS configs found. Are they vless:// links?")
        sys.exit(1)
    print(f"  Found {len(configs)} VLESS config(s)")

    if args.max and args.max < len(configs):
        print(f"  Limiting to first {args.max}")
        configs = configs[:args.max]

    # 3. Real delay test
    print(f"\n[3/5] Testing real latency (HTTP request through proxy)...")
    max_workers = min(args.parallel_latency, len(configs))
    print(f"  Workers: {max_workers}  |  Target: {LATENCY_TARGET}")
    print(f"  Timeout: {LATENCY_TIMEOUT}s per config")
    print()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for idx, cfg in enumerate(configs):
            worker_id = idx % max_workers
            future = executor.submit(_latency_worker, cfg, args.latency_target, worker_id, idx)
            futures[future] = idx

        for future in concurrent.futures.as_completed(futures):
            idx, lat, err = future.result()
            cfg = configs[idx]
            cfg.latency_s = lat
            cfg.latency_error = err
            name = cfg.display_name()
            if lat is not None:
                print(f"  [{idx+1}/{len(configs)}] {name} → {lat*1000:.0f} ms ✓")
            else:
                print(f"  [{idx+1}/{len(configs)}] {name} → FAIL — {err or 'unknown error'}")

    # Sort: alive by latency, dead at bottom
    alive = [c for c in configs if c.latency_s is not None]
    dead = [c for c in configs if c.latency_s is None]
    alive.sort(key=lambda c: c.latency_s)
    ranked = alive + dead

    # 4. Speed test (optional)
    if args.speedtest and alive:
        print(f"\n[4/5] Speed testing reachable configs...")
        max_workers = min(args.parallel_speed, len(alive))
        print(f"  Workers: {max_workers}  |  Target: {SPEEDTEST_URL}")
        print(f"  Timeout: {SPEEDTEST_TIMEOUT}s per config")
        print()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for idx, cfg in enumerate(alive):
                worker_id = idx % max_workers
                future = executor.submit(_speed_worker, cfg, args.speedtest_url, worker_id, idx)
                futures[future] = idx

            for future in concurrent.futures.as_completed(futures):
                idx, speed, err = future.result()
                cfg = alive[idx]
                cfg.speed_mbps = speed
                cfg.speed_error = err
                name = cfg.display_name()
                if speed is not None:
                    print(f"  [{idx+1}/{len(alive)}] {name} → {speed:.1f} Mbps ✓")
                else:
                    print(f"  [{idx+1}/{len(alive)}] {name} → FAIL — {err or 'unknown error'}")

        # Re-sort with speed info
        alive.sort(key=lambda c: (c.latency_s or 999, -(c.speed_mbps or 0)))
        ranked = alive + dead

    # 5. Output — sorted alive raw configs
    print(f"\n[5/5] Writing sorted alive configs...")

    # Determine output target
    output_target = args.output  # "-" for terminal, path for file, None for default
    if output_target is None:
        output_target = "alive_configs.txt"

    write_count = 0
    try:
        if output_target == "-":
            # Print raw vless:// links to terminal
            print()
            print("--- Sorted alive configs ---")
            for c in alive:
                print(c.link)
            print("--- end ---")
            write_count = len(alive)
        else:
            # Ensure parent directory exists
            outdir = os.path.dirname(output_target)
            if outdir and not os.path.exists(outdir):
                os.makedirs(outdir, exist_ok=True)
            with open(output_target, "w") as f:
                for c in alive:
                    f.write(c.link + "\n")
            write_count = len(alive)
    except Exception as e:
        print(f"  ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Wrote {write_count} alive config(s) to: {output_target}")

    # Also print the summary table to terminal for quick reference
    print_results(ranked, show_speed=args.speedtest)
    print("\n  Done.")


if __name__ == "__main__":
    main()
