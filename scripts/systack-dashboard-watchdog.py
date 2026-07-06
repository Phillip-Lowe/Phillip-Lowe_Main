#!/usr/bin/env python3
"""
Systack Dashboard Watchdog — Auto-start + keep-alive for all 5 dashboards
Runs as a background daemon. Restarts any dashboard that dies.

Usage:
    python3 systack-dashboard-watchdog.py         # Start in foreground
    python3 systack-dashboard-watchdog.py --bg    # Start in background (detached)
    python3 systack-dashboard-watchdog.py --kill    # Stop all dashboards + watchdog
    python3 systack-dashboard-watchdog.py --status  # Show what's running

Dashboards managed:
    Port 8765 — Fleet Dashboard        (Systack/tools/dashboard/web_dashboard.py)
    Port 8766 — Invoice Dashboard      (Systack/tools/invoice-parser/invoice_dashboard_api.py)
    Port 8768 — SAOS Customer Dashboard (Systack/content/saos/saos-data/customer-dashboard/api.py)
    Port 8770 — Command Center         (systack-command-center/api.py)
    Port 8772 — Booking Dashboard      (systack-booking-dashboard/api.py)

Auto-restart: immediate on crash, with max 5 restarts in 60s before backing off.
Health check: HTTP GET to each dashboard's /health or /api/status every 30s.
Log: ~/.openclaw/workspaces/sol/scripts/dashboard-watchdog.log
PID file: /tmp/systack-dashboard-watchdog.pid
"""

import subprocess
import time
import os
import sys
import signal
import argparse
import socket
import json
from datetime import datetime
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────────────

WORKSPACE = Path.home() / ".openclaw" / "workspaces" / "sol"
LOG_FILE = WORKSPACE / "scripts" / "dashboard-watchdog.log"
PID_FILE = Path("/tmp/systack-dashboard-watchdog.pid")
STATE_FILE = Path("/tmp/systack-dashboard-state.json")

# Dashboard definitions: name -> {port, script_path, health_path, type}
DASHBOARDS = {
    "fleet": {
        "port": 8765,
        "script": WORKSPACE / "Systack" / "tools" / "dashboard" / "web_dashboard.py",
        "health_path": "/api/status",
        "type": "http",
        "env": {},
    },
    "invoice": {
        "port": 8766,
        "script": WORKSPACE / "Systack" / "tools" / "invoice-parser" / "invoice_dashboard_api.py",
        "health_path": "/api/health",
        "type": "http",
        "env": {},
    },
    "saos": {
        "port": 8768,
        "script": WORKSPACE / "Systack" / "content" / "saos" / "saos-data" / "customer-dashboard" / "api.py",
        "health_path": "/api/health",
        "type": "flask",
        "env": {},
    },
    "command-center": {
        "port": 8770,
        "script": WORKSPACE / "systack-command-center" / "api.py",
        "health_path": "/api/fleet/status",
        "type": "flask",
        "env": {},
    },
    "booking": {
        "port": 8772,
        "script": WORKSPACE / "systack-booking-dashboard" / "api.py",
        "health_path": "/api/health",
        "type": "flask",
        "env": {},
    },
}

CHECK_INTERVAL = 30       # seconds between health checks
RESTART_DELAY = 2          # seconds before restart after crash
MAX_RESTARTS_WINDOW = 60   # seconds
MAX_RESTARTS = 5           # max restarts within window before backoff
BACKOFF_DURATION = 300     # seconds to wait after max restarts hit

# ── LOGGING ─────────────────────────────────────────────────────────

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def log_startup():
    log("=" * 60)
    log("Systack Dashboard Watchdog starting")
    log(f"Workspace: {WORKSPACE}")
    log(f"Log file:  {LOG_FILE}")
    log(f"PID file:  {PID_FILE}")
    log(f"Monitoring {len(DASHBOARDS)} dashboards")
    for name, cfg in DASHBOARDS.items():
        log(f"  [{name}] port={cfg['port']} → {cfg['script']}")
    log("=" * 60)

# ── PROCESS MANAGEMENT ─────────────────────────────────────────────

running_procs = {}  # name -> subprocess.Popen
restart_counts = {}  # name -> [timestamps]
last_health = {}     # name -> {ok: bool, status: int, checked: ts}

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def read_pid():
    try:
        with open(PID_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return None

def save_state():
    state = {
        "pid": os.getpid(),
        "started": datetime.now().isoformat(),
        "dashboards": {
            name: {
                "pid": proc.pid if proc and proc.poll() is None else None,
                "running": proc is not None and proc.poll() is None,
                "last_health": last_health.get(name),
            }
            for name, proc in running_procs.items()
        }
    }
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

def is_port_open(port, host="127.0.0.1", timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def check_health(name, cfg):
    """Check if dashboard is responding."""
    if not is_port_open(cfg["port"]):
        return {"ok": False, "status": None, "error": "Port not open", "checked": datetime.now().isoformat()}
    
    # For HTTP dashboards, do a quick GET
    try:
        import urllib.request
        url = f"http://127.0.0.1:{cfg['port']}{cfg['health_path']}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "Systack-Watchdog/1.0")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {
                "ok": 200 <= resp.status < 400,
                "status": resp.status,
                "error": None,
                "checked": datetime.now().isoformat(),
            }
    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "error": str(e),
            "checked": datetime.now().isoformat(),
        }

def start_dashboard(name, cfg):
    """Start a single dashboard process."""
    script = cfg["script"]
    if not script.exists():
        log(f"[ERROR] [{name}] Script not found: {script}")
        return None
    
    env = os.environ.copy()
    env.update(cfg.get("env", {}))
    
    # Ensure workspace env vars are loaded
    for key in ["SYSTACK_ADMIN_PIN", "PGHOST", "PGPORT", "PGDATABASE", "PGUSER"]:
        if key in os.environ:
            env[key] = os.environ[key]
    
    cmd = [sys.executable, str(script), "--port", str(cfg["port"])]
    if cfg["type"] == "http":
        # HTTP servers take positional arg
        cmd = [sys.executable, str(script), str(cfg["port"])]
    
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(script.parent),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            # Detach from terminal so Ctrl+C in shell doesn't kill children
            start_new_session=True,
        )
        log(f"[START] [{name}] PID {proc.pid} on port {cfg['port']} ({script.name})")
        return proc
    except Exception as e:
        log(f"[ERROR] [{name}] Failed to start: {e}")
        return None

def stop_dashboard(name):
    """Kill a dashboard process."""
    proc = running_procs.get(name)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
            log(f"[STOP] [{name}] PID {proc.pid} terminated")
        except subprocess.TimeoutExpired:
            proc.kill()
            log(f"[KILL] [{name}] PID {proc.pid} killed")
        except Exception as e:
            log(f"[ERROR] [{name}] stopping: {e}")
    running_procs[name] = None

def restart_dashboard(name, cfg):
    """Restart a dashboard, with rate limiting."""
    now = time.time()
    restarts = restart_counts.get(name, [])
    restarts = [t for t in restarts if now - t < MAX_RESTARTS_WINDOW]
    restart_counts[name] = restarts
    
    if len(restarts) >= MAX_RESTARTS:
        log(f"[BACKOFF] [{name}] {MAX_RESTARTS} restarts in {MAX_RESTARTS_WINDOW}s — waiting {BACKOFF_DURATION}s")
        time.sleep(BACKOFF_DURATION)
        restart_counts[name] = []
    
    stop_dashboard(name)
    time.sleep(RESTART_DELAY)
    proc = start_dashboard(name, cfg)
    if proc:
        running_procs[name] = proc
        restart_counts[name].append(time.time())
    return proc

# ── MAIN LOOP ──────────────────────────────────────────────────────

keep_running = True

def signal_handler(signum, frame):
    global keep_running
    log(f"[SIGNAL] Received {signum} — shutting down gracefully...")
    keep_running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def run_watchdog():
    global running_procs
    
    log_startup()
    write_pid()
    
    # Start all dashboards
    for name, cfg in DASHBOARDS.items():
        proc = start_dashboard(name, cfg)
        running_procs[name] = proc
        time.sleep(1)  # Stagger starts to avoid port conflicts
    
    log("All dashboards launched. Entering health-check loop...")
    
    loop_count = 0
    while keep_running:
        time.sleep(CHECK_INTERVAL)
        loop_count += 1
        
        for name, cfg in DASHBOARDS.items():
            proc = running_procs.get(name)
            
            # Check if process is alive
            proc_alive = proc is not None and proc.poll() is None
            
            # Check port + HTTP health
            health = check_health(name, cfg)
            last_health[name] = health
            
            status_emoji = "✅" if health["ok"] else "❌"
            status_msg = f"HTTP {health['status']}" if health["status"] else health.get("error", "unknown")
            
            if not proc_alive:
                log(f"[CRASH] [{name}] Process dead — restarting ({status_msg})")
                restart_dashboard(name, cfg)
            elif not health["ok"]:
                log(f"[UNHEALTHY] [{name}] Not responding — restarting ({status_msg})")
                restart_dashboard(name, cfg)
            elif loop_count % 10 == 0:  # Log healthy status every 5 min
                log(f"[HEALTH] [{name}] {status_emoji} {status_msg}")
        
        save_state()
    
    # Shutdown
    log("[SHUTDOWN] Stopping all dashboards...")
    for name in DASHBOARDS:
        stop_dashboard(name)
    
    try:
        PID_FILE.unlink()
        STATE_FILE.unlink()
    except Exception:
        pass
    
    log("[SHUTDOWN] Watchdog stopped. Goodbye.")

# ── CLI COMMANDS ───────────────────────────────────────────────────

def do_background():
    """Daemonize and run in background."""
    import os
    # Double-fork daemon
    pid = os.fork()
    if pid > 0:
        # Parent exits
        time.sleep(1)
        # Confirm child started
        child_pid = read_pid()
        if child_pid:
            print(f"🚀 Watchdog daemon started (PID {child_pid})")
            print(f"   Log: {LOG_FILE}")
            print(f"   Status: python3 {__file__} --status")
            print(f"   Stop:   python3 {__file__} --kill")
        else:
            print("⚠️  Daemon may not have started. Check log.")
        sys.exit(0)
    
    os.setsid()  # New session
    
    pid = os.fork()
    if pid > 0:
        sys.exit(0)  # Second parent exits
    
    # Redirect stdin/stdout/stderr
    sys.stdout.flush()
    sys.stderr.flush()
    with open("/dev/null", "r") as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(LOG_FILE, "a") as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())
    
    run_watchdog()

def do_kill():
    """Kill watchdog + all dashboards."""
    pid = read_pid()
    if not pid:
        print("No watchdog PID found. Checking for orphaned dashboard processes...")
    else:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to watchdog (PID {pid})")
        except ProcessLookupError:
            print(f"Watchdog PID {pid} not running")
        except PermissionError:
            print(f"Permission denied to kill PID {pid}")
    
    # Also kill by port
    killed = 0
    for name, cfg in DASHBOARDS.items():
        try:
            result = subprocess.run(
                ["lsof", "-t", "-i", f":{cfg['port']}"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split("\n"):
                if line.strip().isdigit():
                    try:
                        os.kill(int(line.strip()), signal.SIGTERM)
                        killed += 1
                    except Exception:
                        pass
        except Exception:
            pass
    
    if killed:
        print(f"Killed {killed} orphaned dashboard process(es)")
    
    # Cleanup files
    for f in [PID_FILE, STATE_FILE]:
        try:
            f.unlink()
        except Exception:
            pass
    
    print("All dashboards stopped.")

def do_status():
    """Show current status of all dashboards."""
    pid = read_pid()
    if pid:
        try:
            os.kill(pid, 0)  # Signal 0 checks if process exists
            print(f"🟢 Watchdog running (PID {pid})")
        except OSError:
            print(f"🟡 Watchdog PID file stale ({pid})")
    else:
        print("🔴 Watchdog not running")
    
    print()
    print(f"{'Dashboard':<20} {'Port':<6} {'Process':<10} {'Health':<20}")
    print("-" * 60)
    
    for name, cfg in DASHBOARDS.items():
        port = cfg["port"]
        
        # Check process
        proc_running = False
        proc_pid = None
        try:
            result = subprocess.run(
                ["lsof", "-t", "-i", f":{port}"],
                capture_output=True, text=True, timeout=5
            )
            pids = [p for p in result.stdout.strip().split("\n") if p.strip().isdigit()]
            if pids:
                proc_running = True
                proc_pid = pids[0]
        except Exception:
            pass
        
        # Check health
        health = check_health(name, cfg)
        health_str = f"HTTP {health['status']}" if health["status"] else health.get("error", "no response")
        
        proc_str = f"PID {proc_pid}" if proc_running else "dead"
        emoji = "✅" if health["ok"] else "❌"
        
        print(f"{name:<20} {port:<6} {proc_str:<10} {emoji} {health_str}")
    
    # Show recent log tail
    print()
    try:
        with open(LOG_FILE) as f:
            lines = f.readlines()
            if lines:
                print("Recent log entries:")
                for line in lines[-5:]:
                    print("  ", line.strip())
    except Exception:
        pass

# ── ENTRYPOINT ───────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Systack Dashboard Watchdog")
    parser.add_argument("--bg", action="store_true", help="Run as background daemon")
    parser.add_argument("--kill", action="store_true", help="Stop all dashboards + watchdog")
    parser.add_argument("--status", action="store_true", help="Show status of all dashboards")
    args = parser.parse_args()
    
    if args.kill:
        do_kill()
    elif args.status:
        do_status()
    elif args.bg:
        do_background()
    else:
        run_watchdog()
