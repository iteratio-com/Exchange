#!/usr/bin/env python3
"""Cross-platform MaxDB Checkmk agent plugin."""

import argparse
import configparser
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

QUERIES = {
    "state": [["db_state"]],
    "backup": [["backup_history_list", "-c", "LABEL,ACTION,START,STOP,RC,ERROR", "-I"]],
    "data": [
        [
            "sql_executenice",
            "SELECT",
            "A.USEDSIZE,A.USABLESIZE,S.USED_LOG_PAGES*D.PAGESIZE_IN_KB,S.USED_LOG_PAGES,D.ACTIVE_SESSIONS,D.DATACACHE_HITRATE,S.LOG_PAGES*D.PAGESIZE_IN_KB,S.LOG_PAGES,S.LOG_NOT_SAVED,D.MAXUSERS,D.DATABASEFULL,D.AUTOSAVESTANDBY,D.BADINDEXES,D.LOGFULL,D.BADVOLUMES",
            "FROM",
            "SYSDD.DATASTATISTICS",
            "A,SYSDD.SERVERDB_STATS",
            "S,SYSDD.DBM_STATE",
            "D",
        ]
    ],
}
# Exploratory SQL: availability varies by MaxDB version. Each query is isolated.
# Raw output is intentionally preserved for evaluation before writing Checkmk checks.
EXTRA_QUERIES = {
    "locks": [
        ("lock_statistics", "SELECT * FROM SYSINFO.LOCKSTATISTICS"),
    ],
    "performance": [
        ("command_statistics", "SELECT * FROM SYSINFO.COMMANDSTATISTICS"),
    ],
    "volumes": [
        ("data_statistics", "SELECT * FROM SYSDD.DATASTATISTICS"),
        ("dbm_state", "SELECT * FROM SYSDD.DBM_STATE"),
    ],
    "transactions": [
        ("transactions", "SELECT * FROM SYSINFO.TRANSACTIONS"),
    ],
}
EXTRA_MODULES = set(EXTRA_QUERIES) | {"backup_extended"}
ALL_MODULES = set(QUERIES) | EXTRA_MODULES
NAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
KEY_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
USER_RE = re.compile(r"^[A-Za-z0-9_.@\\-]{1,128}$")


def sanitize_inventory_paths(output):
    """Avoid invalid Windows drive/path tokens in legacy MaxDB inventory data.

    The inventory parser can interpret a Windows path as an inventory tree
    component. Keep the installation identity and version lines, but omit
    absolute installation paths from the state section.
    """
    lines = []
    for line in output.splitlines():
        if line.lstrip().startswith("Installation:"):
            line = re.sub(r"\s+[A-Za-z]:[\\/][^\r\n]*$", "", line)
        lines.append(line)
    return "\n".join(lines)


def clean_text(value):
    # Keep arbitrary dbmcli output as JSON data rather than guessing its column format.
    return value.replace("\x00", "")


def collect_extras(db, cmd, timeout, modules):
    lines = []
    errors = []
    for module, queries in EXTRA_QUERIES.items():
        if module not in modules:
            continue
        records = []
        for label, sql in queries:
            try:
                output = execute(cmd + ["sql_executenice", sql], timeout)
                records.append({"query": label, "status": "ok", "output": clean_text(output)})
            except (OSError, subprocess.TimeoutExpired, RuntimeError, ValueError) as exc:
                detail = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else str(exc)[:300]
                records.append({"query": label, "status": "unsupported_or_failed", "error": detail})
                pass  # Report individual optional query failure in JSON, not agent exit status
        lines.extend(
            [
                f"<<<maxdb_{module}:sep(0)>>>",
                json.dumps({"database": db, "queries": records}, ensure_ascii=False),
            ]
        )
    if "backup_extended" in modules:
        records = []
        for label, query in (
            (
                "backup_history",
                ["backup_history_list", "-c", "LABEL,ACTION,START,STOP,RC,ERROR", "-I"],
            ),
            ("auto_log", ["autolog_show"]),
        ):
            try:
                output = execute(cmd + query, timeout)
                records.append({"query": label, "status": "ok", "output": clean_text(output)})
            except (OSError, subprocess.TimeoutExpired, RuntimeError, ValueError) as exc:
                detail = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else str(exc)[:300]
                records.append({"query": label, "status": "unsupported_or_failed", "error": detail})
                pass  # Optional query failure is visible in section
        lines.extend(
            [
                "<<<maxdb_backup_extended:sep(0)>>>",
                json.dumps({"database": db, "queries": records}, ensure_ascii=False),
            ]
        )
    return lines, errors


SECTIONS = {"state": "maxdb_state", "backup": "maxdb_backup:sep(124)", "data": "maxdb_data:sep(61)"}


def read_config(path):
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict) or not isinstance(data.get("databases"), list):
            raise ValueError("maxdb.json requires a databases array")
        for item in data["databases"]:
            if not isinstance(item, dict):
                raise ValueError("Database entries must be objects")
            name = item.get("dbname", "")
            if name and (not isinstance(name, str) or not NAME_RE.fullmatch(name)):
                raise ValueError("Invalid database name")
            modules = item.get("modules", sorted(ALL_MODULES))
            if not isinstance(modules, list) or any(
                not isinstance(m, str) or m not in ALL_MODULES for m in modules
            ):
                raise ValueError("Invalid monitoring module")
            item["modules"] = modules
            timeout = item.get("timeout", 20)
            if type(timeout) is not int or not 1 <= timeout <= 120:
                raise ValueError("Timeout must be between 1 and 120 seconds")
            auth = item.get("auth", {})
            if not isinstance(auth, dict):
                raise ValueError("Authentication must be an object")
            key = item.get("xuser_key") or auth.get("xuser_key")
            if key and (not isinstance(key, str) or not KEY_RE.fullmatch(key)):
                raise ValueError("Invalid XUSER key")
            user = item.get("user") or auth.get("user")
            if user and (not isinstance(user, str) or not USER_RE.fullmatch(user)):
                raise ValueError("Invalid username")
        return data
    old = path.with_suffix(".cfg")
    if not old.exists():
        raise FileNotFoundError(f"No MaxDB configuration: {path} or {old}")
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(old)
    databases = []
    for name in cfg.sections():
        item = dict(cfg.items(name))
        item["dbname"] = "" if name == "lookup" else name
        raw_modules = item.get("modules", "state")
        # Legacy .cfg values are comma-separated or Python-list-looking strings.
        # Parse tokens, never evaluate expressions from a configuration file.
        if raw_modules.strip().startswith("[") and raw_modules.strip().endswith("]"):
            raw_modules = raw_modules.strip()[1:-1]
        modules = [part.strip().strip("\"'").split(":", 1)[0] for part in raw_modules.split(",")]
        if any(module not in ALL_MODULES for module in modules):
            raise ValueError(f"Invalid legacy monitoring modules for {name}")
        item["modules"] = modules
        databases.append(item)
    return {"databases": databases}


def roots():
    configured = os.getenv("MAXDB_ROOT")
    if configured:
        return [Path(configured)]
    if os.name == "nt":
        return [Path(f"{drive}:\\sapdb") for drive in "CDEFG"]
    return [Path("/sapdb")]


def detect_names():
    found = set()
    for root in roots():
        if not root.is_dir():
            continue
        for entry in root.iterdir():
            if entry.is_dir() and re.fullmatch(r"[A-Za-z0-9_]{3}", entry.name):
                found.add(entry.name)
    return sorted(found)


def find_binary(db, name):
    suffix = ".exe" if os.name == "nt" else ""
    candidates = []
    for root in roots():
        candidates.extend(
            (
                root / db / "db" / "pgm" / (name + suffix),
                root / db / "db" / "bin" / (name + suffix),
                root / "programs" / "pgm" / (name + suffix),
                root / "programs" / "bin" / (name + suffix),
            )
        )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    which = shutil.which(name + suffix)
    return Path(which) if which else None


def execute(args, timeout):
    result = subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False
    )
    output = result.stdout.decode("utf-8", errors="replace").strip()
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"exit {result.returncode}: {message[:300]}")
    return output


def parse_dbmcli_fields(output):
    """Convert dbmcli KEY=VALUE output into JSON-native types safely."""
    values = {}
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, raw = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            continue
        value = raw.strip().strip("\"'")
        if re.fullmatch(r"[+-]?\d+", value):
            values[key] = int(value)
        elif re.fullmatch(r"[+-]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?", value):
            values[key] = float(value)
        else:
            values[key] = value
    return values


def collect(db, item):
    errors = []
    lines = []
    binary = find_binary(db, "dbmcli")
    if binary is None:
        return db, lines, [f"{db}: dbmcli not found"]
    key = item.get("xuser_key") or item.get("auth", {}).get("xuser_key")
    if key:
        cmd = [str(binary), "-U", str(key), "-d", db]
    else:
        auth = item.get("auth", {})
        user = auth.get("user", item.get("user"))
        password = auth.get("password", item.get("password"))
        if not user or password is None:
            return db, lines, [f"{db}: no authentication configured"]
        cmd = [str(binary), "-d", db, "-u", f"{user},{password}"]
    timeout = int(item.get("timeout", 20))
    modules = [str(x).split(":")[0] for x in item.get("modules", sorted(ALL_MODULES))]
    for module in QUERIES:
        if module not in modules:
            continue
        for query in QUERIES[module]:
            try:
                result = execute(cmd + query, timeout)
                if module == "data":
                    # One JSON document per database; retain section name for existing checks.
                    payload = {"database": db, "values": parse_dbmcli_fields(result)}
                    lines.extend(
                        ["<<<maxdb_data:sep(0)>>>", json.dumps(payload, ensure_ascii=False)]
                    )
                else:
                    lines.extend([f"<<<{SECTIONS[module]}>>>", f"[[{db}]]", result])
                if module == "state":
                    reg = find_binary(db, "sdbregview")
                    if reg:
                        lines.append(sanitize_inventory_paths(execute([str(reg), "-l"], timeout)))
            except (OSError, subprocess.TimeoutExpired, RuntimeError, ValueError) as exc:
                errors.append(
                    f"{db}/{module}: {type(exc).__name__}: {str(exc)[:250] if not isinstance(exc, subprocess.TimeoutExpired) else 'timeout'}"
                )
    extra_lines, extra_errors = collect_extras(db, cmd, timeout, modules)
    lines.extend(extra_lines)
    errors.extend(extra_errors)
    return db, lines, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            os.environ.get(
                "MK_CONFDIR",
                str(
                    Path(os.environ.get("PROGRAMDATA", "C:/ProgramData"))
                    / "checkmk"
                    / "agent"
                    / "config"
                    if os.name == "nt"
                    else "/etc/check_mk"
                ),
            )
        )
        / "maxdb.json",
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--extra",
        action="store_true",
        help="Enable exploratory sections for all configured databases",
    )
    args = parser.parse_args()
    try:
        config = read_config(args.config)
        entries = {}
        for item in config["databases"]:
            name = str(item.get("dbname") or "").strip()
            if name and name.lower() != "lookup":
                entries[name] = item
            else:
                for detected in detect_names():
                    entries.setdefault(detected, item)
        if not entries:
            print("MaxDB: no databases configured or detected", file=sys.stderr)
            return 2
        if args.extra:
            for item in entries.values():
                item["modules"] = list(
                    dict.fromkeys(
                        [str(x).split(":")[0] for x in item.get("modules", ["state"])]
                        + sorted(EXTRA_MODULES)
                    )
                )
        with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 16))) as pool:
            results = list(pool.map(lambda pair: collect(*pair), sorted(entries.items())))
        failed = False
        for _, lines, errors in results:
            if lines:
                print("\n".join(lines))
            for error in errors:
                print("MaxDB: " + error, file=sys.stderr)
                failed = True
        return 2 if failed else 0
    except (OSError, ValueError, json.JSONDecodeError, configparser.Error) as exc:
        print(f"MaxDB: configuration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
