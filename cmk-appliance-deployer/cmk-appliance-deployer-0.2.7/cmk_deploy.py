#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
LOG_DIR = ROOT / "logs"
DEFAULT_MANIFEST = ROOT / "packages" / "manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = load_json(path)
    return data.get("packages", data)


def manifest_entry(manifest: dict[str, Any], path: Path) -> dict[str, Any] | None:
    entry = manifest.get(path.name)
    if isinstance(entry, str):
        return {"sha256": entry}
    if isinstance(entry, dict):
        return entry
    return None


def validate_expected_sha(path: Path, manifest: dict[str, Any], require: bool = True) -> tuple[bool, str]:
    entry = manifest_entry(manifest, path)
    if entry is None:
        if require:
            return False, f"No manifest entry for {path.name}"
        return True, "No manifest entry; manufacturer SHA256 check skipped"
    expected = str(entry.get("sha256", "")).lower().strip()
    if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        return False, f"Invalid SHA256 in manifest for {path.name}"
    actual = sha256_file(path)
    if actual != expected:
        return False, f"SHA256 mismatch for {path.name}: expected={expected} actual={actual}"
    return True, f"SHA256 OK: {actual}"


@dataclass
class Result:
    host: str
    operation: str
    status: str
    started: str
    finished: str
    duration_seconds: float
    site: str | None = None
    exit_code: int | None = None
    message: str = ""
    command: str = ""


class Runner:
    def __init__(self, inventory: dict[str, Any], dry_run: bool = False, debug: bool = False):
        self.inventory = inventory
        self.dry_run = dry_run
        self.debug = debug
        REPORT_DIR.mkdir(exist_ok=True)
        LOG_DIR.mkdir(exist_ok=True)

    def host_cfg(self, host: str) -> dict[str, Any]:
        cfg = dict(self.inventory.get("defaults", {}))
        cfg.update(self.inventory["hosts"][host])
        return cfg

    def ssh_base(self, host: str) -> list[str]:
        cfg = self.host_cfg(host)
        target = cfg.get("ssh_host", host)
        user = cfg.get("ssh_user")
        if user:
            target = f"{user}@{target}"
        cmd = ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={cfg.get('connect_timeout', 10)}"]
        if cfg.get("ssh_port"):
            cmd += ["-p", str(cfg["ssh_port"])]
        if cfg.get("identity_file"):
            cmd += ["-i", os.path.expanduser(cfg["identity_file"])]
        for opt in cfg.get("ssh_options", []):
            cmd += ["-o", str(opt)]
        cmd.append(target)
        return cmd

    def log(self, host: str, message: str) -> None:
        print(f"[{host}] {message}", flush=True)

    def remote(
        self,
        host: str,
        command: str,
        timeout: int = 3600,
        debug_command: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        cmd = self.ssh_base(host) + [command]
        if self.debug or self.dry_run:
            shown = debug_command or shlex.join(cmd)
            self.log(host, f"DEBUG: {shown}")
        if self.dry_run:
            return subprocess.CompletedProcess(cmd, 0, "DRY-RUN\n", "")
        return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)

    def remote_python(self, host: str, script: str, timeout: int = 7200) -> subprocess.CompletedProcess[str]:
        return self.remote(
            host,
            f"python3 -c {shlex.quote(script)}",
            timeout=timeout,
            debug_command="ssh ... python3 <remote appliance logic>",
        )

    def result_for(self, host: str, operation: str, fn, site: str | None = None) -> Result:
        started_dt = datetime.now(timezone.utc)
        target = f" site={site}" if site else ""
        self.log(host, f"START {operation}{target}")
        try:
            rc, msg, command = fn()
            status = "SUCCESS" if rc == 0 else "FAILED"
        except Exception as exc:
            rc, msg, command, status = None, str(exc), "", "FAILED"
        finished_dt = datetime.now(timezone.utc)
        duration = round((finished_dt - started_dt).total_seconds(), 2)
        if status == "SUCCESS":
            self.log(host, f"OK    {operation} ({duration:.2f}s)")
        else:
            self.log(host, f"FAILED {operation} rc={rc} ({duration:.2f}s)")
        if msg and (self.debug or status != "SUCCESS" or operation in {"verify_remote_sha256", "install_cma", "validate_cfw", "verify_cfw_after_reboot", "version_inventory", "version_inventory_after_cma", "cleanup_versions"}):
            for line in msg.splitlines():
                self.log(host, f"  {line}")
        return Result(
            host=host,
            site=site,
            operation=operation,
            status=status,
            started=started_dt.isoformat(),
            finished=finished_dt.isoformat(),
            duration_seconds=duration,
            exit_code=rc,
            message=msg,
            command=command,
        )

    def _simple_remote(self, host: str, command: str, timeout: int = 3600):
        cp = self.remote(host, command, timeout)
        return cp.returncode, (cp.stdout + cp.stderr).strip(), command

    def preflight_host(self, host: str) -> list[Result]:
        checks = [
            ("ssh", "true"),
            ("tools", "command -v python3 && command -v sha256sum && command -v omd"),
            ("disk", "df -Pk /var/tmp /omd /ro 2>/dev/null || true"),
            ("appliance", "python3 -c 'import cma; print(cma.version())'"),
            ("omd", "omd version || true; omd sites || true"),
        ]
        return [self.result_for(host, f"preflight_{n}", lambda c=c: self._simple_remote(host, c)) for n, c in checks]

    def stage_host(self, host: str, local_file: Path, remote_dir: str, bwlimit: int | None) -> Result:
        cfg = self.host_cfg(host)
        remote_file = f"{remote_dir.rstrip('/')}/{local_file.name}"

        def do_stage():
            mkdir_cmd = f"mkdir -p {shlex.quote(remote_dir)}"
            cp = self.remote(host, mkdir_cmd)
            if cp.returncode != 0:
                return cp.returncode, (cp.stdout + cp.stderr).strip(), mkdir_cmd
            target = cfg.get("ssh_host", host)
            if cfg.get("ssh_user"):
                target = f"{cfg['ssh_user']}@{target}"
            if shutil.which("rsync") and cfg.get("use_rsync", True):
                ssh_parts = ["ssh", "-o", "BatchMode=yes"]
                if cfg.get("ssh_port"):
                    ssh_parts += ["-p", str(cfg["ssh_port"])]
                if cfg.get("identity_file"):
                    ssh_parts += ["-i", os.path.expanduser(cfg["identity_file"])]
                for opt in cfg.get("ssh_options", []):
                    ssh_parts += ["-o", str(opt)]
                rsync = ["rsync", "--partial", "--append-verify", "--info=progress2"]
                if bwlimit:
                    rsync += [f"--bwlimit={bwlimit}"]
                rsync += ["-e", shlex.join(ssh_parts), str(local_file), f"{target}:{remote_file}"]
                if self.debug or self.dry_run:
                    self.log(host, f"DEBUG: {shlex.join(rsync)}")
                if self.dry_run:
                    return 0, f"Would stage {local_file} -> {host}:{remote_file}", shlex.join(rsync)
                rp = subprocess.run(rsync, text=True, capture_output=True)
                return rp.returncode, (rp.stdout + rp.stderr).strip(), shlex.join(rsync)
            scp = ["scp"]
            if cfg.get("ssh_port"):
                scp += ["-P", str(cfg["ssh_port"])]
            if cfg.get("identity_file"):
                scp += ["-i", os.path.expanduser(cfg["identity_file"])]
            scp += [str(local_file), f"{target}:{remote_file}"]
            if self.dry_run:
                return 0, f"Would stage {local_file} -> {host}:{remote_file}", shlex.join(scp)
            sp = subprocess.run(scp, text=True, capture_output=True)
            return sp.returncode, (sp.stdout + sp.stderr).strip(), shlex.join(scp)

        return self.result_for(host, "stage", do_stage)

    def verify_remote_sha(self, host: str, remote_file: str, expected_sha: str) -> Result:
        command = f"printf '%s  %s\\n' {shlex.quote(expected_sha)} {shlex.quote(remote_file)} | sha256sum -c -"
        return self.result_for(host, "verify_remote_sha256", lambda: self._simple_remote(host, command))

    def inventory_sites(self, host: str) -> Result:
        command = "omd sites 2>/dev/null || true"
        return self.result_for(host, "site_inventory", lambda: self._simple_remote(host, command))

    def install_cma(self, host: str, remote_file: str) -> Result:
        # Mirrors the appliance GUI flow, with fallbacks for older cma module APIs.
        script = f'''import os, re, shutil, subprocess, tarfile
import cma

path={remote_file!r}
filename=os.path.basename(path)

def phase(text):
    print("CMA:", text, flush=True)

def installed_versions():
    if hasattr(cma, "omd_versions"):
        try:
            return [str(v) for v in cma.omd_versions()]
        except Exception:
            pass
    try:
        return [n for n in os.listdir("/omd/versions") if n != "default" and os.path.isdir(os.path.join("/omd/versions", n))]
    except OSError:
        return []

def is_compatible(v):
    if hasattr(cma, "is_compatible_version"):
        try:
            return bool(cma.is_compatible_version(v))
        except Exception:
            return None
    return None

def set_default(v):
    if hasattr(cma, "set_default_version"):
        cma.set_default_version(v)
        return
    link="/omd/versions/default"
    try:
        if os.path.lexists(link): os.unlink(link)
        os.symlink(v, link)
    except OSError as exc:
        raise SystemExit("Could not set default Checkmk version: %s" % exc)

def post_install(v):
    if hasattr(cma, "execute_post_install"):
        cma.execute_post_install(v)
        return
    script=os.path.join("/omd/versions", v, "lib/cma/post-install")
    if not os.path.isfile(script):
        raise SystemExit("Missing post-install script: "+script)
    subprocess.check_call([script], cwd=os.path.join("/omd/versions", v))

phase("validating filename %s" % filename)
if ".." in filename or "/" in filename or not filename.endswith(".cma"):
    raise SystemExit("Invalid CMA filename")
if "x86_64" not in filename:
    raise SystemExit("CMA is not x86_64")

os_version = cma.os_version() if hasattr(cma, "os_version") else None
if os_version:
    if not re.match(r".+-%s-x86_64\\ ?(\\([0-9]+\\))?\\.cma" % re.escape(str(os_version)), filename):
        label = cma.os_version_label() if hasattr(cma, "os_version_label") else str(os_version)
        raise SystemExit("CMA does not match appliance platform %s (expected package suffix -%s-x86_64.cma)" % (label, os_version))
else:
    phase("WARNING: old cma module has no os_version(); platform filename check skipped")

phase("opening and validating archive")
with open(path,"rb") as fo:
    tf=tarfile.open(fileobj=fo)
    members=tf.getmembers()
    paths=[m.name for m in members]
    if len(paths) < 1000:
        raise SystemExit("CMA archive too small/truncated")
    version=paths[0].split("/",1)[0]
    if not re.match(r"^[1-9][0-9]*\\.[-0-9a-z.]+$", version):
        raise SystemExit("Invalid CMA version root: "+version)
    for member in members:
        normalized=os.path.normpath(member.name)
        if os.path.isabs(member.name) or normalized == ".." or normalized.startswith("../"):
            raise SystemExit("Unsafe path in CMA archive: "+member.name)
        if normalized != version and not normalized.startswith(version+"/"):
            raise SystemExit("Archive contains path outside version root: "+member.name)
    existing=installed_versions()
    compat=is_compatible(version) if version in existing else None
    if version in existing and compat is not False:
        raise SystemExit("Version already installed: "+version)
    if version+"/lib/cmc/icmpsender" not in paths:
        raise SystemExit("Not a commercial Checkmk edition")
    info_path=version+"/cma.info"
    if info_path not in paths:
        raise SystemExit("Missing cma.info")
    info={{}}
    f=tf.extractfile(info_path)
    if f is None:
        raise SystemExit("Could not read cma.info")
    for line in f.read().decode("utf-8").splitlines():
        parts=line.strip().split("=",1)
        if len(parts)==2:
            info[parts[0]]=parts[1]
    if "MIN_VERSION" not in info:
        raise SystemExit("cma.info has no MIN_VERSION")
    current_fw=cma.version()
    cur=list(map(int,current_fw.split(".")[:3]))
    req=list(map(int,info["MIN_VERSION"].split(".")[:3]))
    phase("package version=%s, firmware=%s, minimum firmware=%s" % (version, current_fw, info["MIN_VERSION"]))
    if tuple(req) > tuple(cur):
        raise SystemExit("CMA requires firmware %s, current %s" % (info["MIN_VERSION"], current_fw))
    if version in existing and compat is False:
        phase("removing incompatible existing version %s" % version)
        shutil.rmtree("/omd/versions/"+version)
    phase("extracting %s to /omd/versions" % version)
    tf.extractall("/omd/versions")

phase("setting default version to %s" % version)
set_default(version)
phase("running lib/cma/post-install")
post_install(version)
phase("installed successfully: %s" % version)
'''
        def run():
            cp = self.remote_python(host, script, 7200)
            return cp.returncode, (cp.stdout + cp.stderr).strip(), "python3 <CMA appliance install logic>"
        return self.result_for(host, "install_cma", run)

    def version_inventory(self, host: str, operation: str = "version_inventory") -> Result:
        script = r'''import os

def installed_versions():
    base = "/omd/versions"
    try:
        versions = [n for n in os.listdir(base) if n != "default" and os.path.isdir(os.path.join(base, n))]
    except OSError:
        versions = []
    return sorted(versions)

def default_version():
    try:
        return os.path.basename(os.readlink("/omd/versions/default").rstrip("/"))
    except OSError:
        return "-"

def site_versions():
    base = "/omd/sites"
    out = []
    try:
        sites = sorted(os.listdir(base))
    except OSError:
        sites = []
    for site in sites:
        path = os.path.join(base, site)
        if not os.path.isdir(path):
            continue
        try:
            target = os.readlink(os.path.join(path, "version"))
            version = os.path.basename(target.rstrip("/"))
        except OSError:
            version = "?"
        out.append((site, version))
    return out

versions = installed_versions()
default = default_version()
by_version = {v: [] for v in versions}
unknown = []
for site, version in site_versions():
    if version in by_version:
        by_version[version].append(site)
    else:
        unknown.append((site, version))

print("Installed Checkmk versions:")
for version in versions:
    suffix = " (default)" if version == default else ""
    sites = ", ".join(by_version.get(version, [])) or "-"
    print("  %-24s%s  sites: %s" % (version, suffix, sites))
if not versions:
    print("  -")
print("Sites:")
for version in versions:
    for site in by_version.get(version, []):
        print("  %-24s -> %s" % (site, version))
for site, version in unknown:
    print("  %-24s -> %s" % (site, version))
'''
        def run():
            cp = self.remote_python(host, script, 120)
            return cp.returncode, (cp.stdout + cp.stderr).strip(), "python3 <Checkmk version inventory>"
        return self.result_for(host, operation, run)

    def cleanup_versions(self, host: str, remove_versions: list[str] | None, all_unused: bool, keep_latest: int, execute: bool) -> Result:
        script = f'''import os, shutil

requested={remove_versions!r}
all_unused={all_unused!r}
keep_latest={keep_latest!r}
execute={execute!r}

base_versions="/omd/versions"
base_sites="/omd/sites"

def versions():
    try:
        return sorted([n for n in os.listdir(base_versions) if n != "default" and os.path.isdir(os.path.join(base_versions,n))])
    except OSError:
        return []

def default_version():
    try:
        return os.path.basename(os.readlink(os.path.join(base_versions,"default")).rstrip("/"))
    except OSError:
        return None

def site_map():
    out={{}}
    try:
        sites=sorted(os.listdir(base_sites))
    except OSError:
        sites=[]
    for site in sites:
        p=os.path.join(base_sites,site)
        if not os.path.isdir(p):
            continue
        try:
            v=os.path.basename(os.readlink(os.path.join(p,"version")).rstrip("/"))
        except OSError:
            continue
        out.setdefault(v,[]).append(site)
    return out

installed=versions()
used=site_map()
default=default_version()
unused=[v for v in installed if not used.get(v)]

if requested:
    candidates=[]
    for v in requested:
        if v not in installed:
            print("SKIP %s: not installed" % v)
            continue
        candidates.append(v)
elif all_unused:
    protected=set(installed[-max(0,keep_latest):]) if keep_latest else set()
    candidates=[v for v in unused if v not in protected]
else:
    candidates=[]

print("Installed versions: %s" % (", ".join(installed) or "-"))
print("Default version: %s" % (default or "-"))
for v in installed:
    print("  %-24s sites: %s" % (v, ", ".join(used.get(v,[])) or "-"))

if not requested and not all_unused:
    print("Unused versions: %s" % (", ".join(unused) or "-"))
    print("Preview only. Use --remove VERSION or --all-unused --execute to delete.")
    raise SystemExit(0)

failed=False
removed=[]
for v in candidates:
    sites=used.get(v,[])
    if sites:
        print("BLOCKED %s: still used by site(s): %s" % (v, ", ".join(sites)))
        failed=True
        continue
    if not execute:
        print("WOULD REMOVE %s" % v)
        continue
    print("REMOVING %s" % v)
    shutil.rmtree(os.path.join(base_versions,v))
    removed.append(v)

if execute and default in removed:
    remaining=versions()
    link=os.path.join(base_versions,"default")
    try:
        if os.path.lexists(link): os.unlink(link)
    except OSError:
        pass
    if remaining:
        os.symlink(remaining[-1],link)
        print("Default version changed to %s" % remaining[-1])
    else:
        print("No versions remain; default link removed")

if failed:
    raise SystemExit(2)
'''
        def run():
            cp = self.remote_python(host, script, 3600)
            return cp.returncode, (cp.stdout + cp.stderr).strip(), "python3 <safe Checkmk version cleanup>"
        return self.result_for(host, "cleanup_versions", run)

    def cfw_running_sites(self, host: str) -> tuple[Result, list[str]]:
        if self.dry_run:
            result = Result(host, "cfw_site_state", "SUCCESS", now_iso(), now_iso(), 0, exit_code=0, message="DRY-RUN: running site state not queried")
            self.log(host, "DRY-RUN: running site state not queried")
            return result, []

        captured: list[str] = []

        def run():
            # Use the appliance/OMD CLI as source of truth.  Do not depend on
            # webconf.sites here: older appliance versions may block in that
            # helper while resolving the site state.
            cp_sites = self.remote(host, "omd sites", timeout=30)
            raw = (cp_sites.stdout + cp_sites.stderr).strip()
            if cp_sites.returncode != 0:
                return cp_sites.returncode, raw, "omd sites"

            names: list[str] = []
            for line in cp_sites.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                # Skip the header/separator printed by `omd sites`.
                upper = stripped.upper()
                if upper.startswith("SITE") or set(stripped) <= {"-", " ", "\t"}:
                    continue
                name = stripped.split()[0]
                if name and name not in names:
                    names.append(name)

            for site in names:
                qsite = shlex.quote(site)
                cp_status = self.remote(host, f"omd status {qsite}", timeout=30)
                # `omd status <site>` returns 0 when the site's processes are
                # up.  Non-zero means it is not a running site for the CFW
                # stop/restore workflow.
                if cp_status.returncode == 0:
                    captured.append(site)

            pretty = "Running sites: " + (", ".join(captured) if captured else "none")
            return 0, pretty, "omd sites + omd status <site>"

        result = self.result_for(host, "cfw_site_state", run)
        return result, captured

    def cfw_stop_sites(self, host: str, sites: list[str]) -> list[Result]:
        out: list[Result] = []
        for site in sites:
            qsite = shlex.quote(site)
            r = self.result_for(host, "cfw_stop_site", lambda c=f"omd stop {qsite}": self._simple_remote(host, c, 1800), site=site)
            out.append(r)
            if r.status != "SUCCESS":
                break
            r = self.result_for(host, "cfw_umount_site", lambda c=f"omd umount --kill {qsite}": self._simple_remote(host, c, 600), site=site)
            out.append(r)
            if r.status != "SUCCESS":
                break
        return out

    def cfw_restore_sites(self, host: str, sites: list[str]) -> list[Result]:
        out: list[Result] = []
        for site in sites:
            qsite = shlex.quote(site)
            r = self.result_for(host, "cfw_restore_site", lambda c=f"omd start {qsite}": self._simple_remote(host, c, 1800), site=site)
            out.append(r)
        return out

    def _cfw_prepare_script(self, remote_file: str, allow_unsigned: bool) -> str:
        # Keep the embedded remote script as a plain template.  In particular,
        # do not build it as an f-string: the script itself contains Python
        # braces/set literals which would otherwise be parsed by the controller.
        script = r'''import os, shutil, subprocess, tempfile
from pathlib import Path
import cma
from webconf.pages import firmware as fw
import logging
fw.logger.setLevel(logging.ERROR)
source=__REMOTE_FILE__
allow_unsigned=__ALLOW_UNSIGNED__
# Confirm site state through OMD CLI, not webconf.sites.
cp_sites=subprocess.run(["omd","sites"], capture_output=True, text=True, timeout=30)
if cp_sites.returncode != 0:
    raise SystemExit("Could not query sites with omd sites: "+(cp_sites.stderr or cp_sites.stdout))
running=[]
for line in cp_sites.stdout.splitlines():
    stripped=line.strip()
    if not stripped or stripped.upper().startswith("SITE") or set(stripped) <= {"-"," ","\t"}:
        continue
    site=stripped.split()[0]
    st=subprocess.run(["omd","status",site], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    if st.returncode == 0:
        running.append(site)
if running:
    raise SystemExit("All sites must be stopped before firmware update: "+", ".join(running))
os.makedirs("/fw_update", exist_ok=True)
if not os.path.ismount("/fw_update"):
    if not cma.execute(["mount","-t","tmpfs","tmpfs","/fw_update","-o","size=70%"]):
        raise SystemExit("Could not mount /fw_update tmpfs")
tmp="/fw_update/deployer-upload.cfw"
shutil.copy2(source,tmp)
with open(tmp,"rb") as fo:
    fw.upload_firmware(os.path.basename(source),fo)
with open(fw.tmp_fw_path,"rb") as fo:
    info=fw.firmware_info(fo)
cur=list(map(int,cma.version().split(".")))
new=list(map(int,info["VERSION"].split(".")))
# Re-check signature, as the GUI does before approval.
with tempfile.TemporaryDirectory() as td:
    with open(fw.tmp_fw_path,"rb") as firmware_file:
        sig=fw.check_firmware_signature(firmware_file,Path(td),gnupghome=None)
if sig is fw.SignatureResult.INVALID:
    raise SystemExit("Firmware signature invalid")
if sig is fw.SignatureResult.MISSING and not allow_unsigned:
    raise SystemExit("Firmware is unsigned; use --allow-unsigned-cfw only for a deliberately trusted developer build")
# GUI-compatible pre-update script.
result,stdout,stderr=fw.check_firmware_preupdate_script(new)
if stdout:
    print(stdout)
if stderr:
    print(stderr)
if result is False:
    raise SystemExit("Firmware pre-update check failed")
# Automate only seamless updates: same major, same minor or next minor.
if new[0] != cur[0] or new[1]-cur[1] not in (0,1):
    raise SystemExit("Non-seamless firmware transition %s -> %s is not automated" % (cma.version(),info["VERSION"]))
print("Firmware validated:",cma.version(),"->",info["VERSION"])
print("TARGET_VERSION="+info["VERSION"])
'''
        return (
            script.replace("__REMOTE_FILE__", repr(remote_file))
            .replace("__ALLOW_UNSIGNED__", repr(allow_unsigned))
        )

    def validate_cfw(self, host: str, remote_file: str, allow_unsigned: bool) -> Result:
        script = self._cfw_prepare_script(remote_file, allow_unsigned)
        def run():
            cp = self.remote_python(host, script, 7200)
            return cp.returncode, (cp.stdout + cp.stderr).strip(), "python3 <CFW appliance validation logic>"
        return self.result_for(host, "validate_cfw", run)

    def activate_cfw(self, host: str) -> Result:
        script = '''import os, shutil, subprocess, time\nimport cma\nfrom webconf.pages import firmware as fw\nif not os.path.exists(fw.tmp_fw_path): raise SystemExit("No validated pending firmware")\ncma.remount_ro(rw=True)\ntry:\n    shutil.move(fw.tmp_fw_path,"/ro/firmware.cfw")\n    os.sync()\nfinally:\n    cma.remount_ro(rw=False)\nprint("Firmware staged to /ro/firmware.cfw; rebooting")\nsubprocess.Popen(["reboot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)\n'''
        def run():
            cp = self.remote_python(host, script, 120)
            # Connection loss during reboot can surface as 255; success is verified by reconnect below.
            msg = (cp.stdout + cp.stderr).strip()
            rc = 0 if cp.returncode in (0, 255) else cp.returncode
            return rc, msg, "python3 <move firmware to /ro + reboot>"
        return self.result_for(host, "activate_cfw_reboot", run)

    def wait_for_reconnect(self, host: str, expected_version: str | None, timeout: int = 1800) -> Result:
        def run():
            if self.dry_run:
                return 0, "Would wait for appliance reboot and verify firmware version", "reconnect"
            deadline = time.time() + timeout
            # Give reboot a moment to begin, then wait until SSH and cma are available again.
            time.sleep(5)
            last = ""
            while time.time() < deadline:
                try:
                    cp = self.remote(host, "python3 -c 'import cma; print(cma.version())'", timeout=20)
                    if cp.returncode == 0:
                        version = cp.stdout.strip()
                        if expected_version and version != expected_version:
                            last = f"SSH is back but firmware is {version}, expected {expected_version}"
                        else:
                            return 0, f"Appliance reachable; firmware={version}", "reconnect/version check"
                    else:
                        last = (cp.stdout + cp.stderr).strip()
                except Exception as exc:
                    last = str(exc)
                time.sleep(10)
            return 1, f"Timed out waiting for appliance: {last}", "reconnect/version check"
        return self.result_for(host, "verify_cfw_after_reboot", run)

    def omd_update(self, host: str, site: str, target_version: str) -> list[Result]:
        # The OMD update syntax depends only on the target Checkmk version.
        # Parse it locally so this also works on older appliance firmware whose
        # cma module does not provide CheckmkVersion/parse_check_mk_version.
        qsite, qver = shlex.quote(site), shlex.quote(target_version)
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)", target_version)
        if not match:
            return [Result(
                host,
                "omd_version_parse",
                "FAILED",
                now_iso(),
                now_iso(),
                0,
                site=site,
                exit_code=1,
                message=f"Could not parse target Checkmk version: {target_version}",
            )]
        target_tuple = tuple(int(part) for part in match.groups())
        syntax = "new" if target_tuple >= (2, 5, 0) else "old"
        if self.debug:
            print(f"[{host}] OMD: target={target_version} -> syntax={syntax}")
        commands: list[tuple[str, str]] = [
            ("omd_stop", f"omd stop {qsite}"),
            ("omd_umount", f"omd umount --kill {qsite}"),
        ]
        if syntax == "new":
            update = f"omd -V {qver} update --pre-flight=abort --skeleton=install --confirm-version --confirm-edition {qsite}"
        else:
            update = f"omd -f -V {qver} update --conflict=install {qsite}"
        commands.append(("omd_update", update))
        # update-apache-config is conditional, exactly as in webconf/sites.py.
        commands.append(("omd_apache", f"omd -V {qver} help | grep -q 'update-apache-config' && omd -V {qver} update-apache-config {qsite} || true"))
        commands.append(("omd_start", f"omd start {qsite}"))
        commands.append(("omd_verify", f"omd version {qsite} && omd status {qsite}"))
        out: list[Result] = []
        for op, cmd in commands:
            r = self.result_for(host, op, lambda c=cmd: self._simple_remote(host, c, 7200), site=site)
            out.append(r)
            if r.status != "SUCCESS":
                break
        return out


def select_hosts(inv: dict[str, Any], args) -> list[str]:
    hosts = list(inv["hosts"].keys())
    if getattr(args, "host", None):
        wanted = set(args.host)
        hosts = [h for h in hosts if h in wanted]
    if getattr(args, "group", None):
        hosts = [h for h in hosts if inv["hosts"][h].get("group") == args.group]
    return hosts


def write_report(results: list[Result]) -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = REPORT_DIR / f"report-{ts}.json"
    text = json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")
    (REPORT_DIR / "latest.json").write_text(text, encoding="utf-8")
    return path


def print_summary(results: list[Result]) -> None:
    print("\nResult")
    print("=" * 96)
    print(f"{'Host':20} {'Site':15} {'Operation':28} {'Status':10} {'RC':>4}")
    print("-" * 96)
    for r in results:
        print(f"{r.host:20} {(r.site or '-'):15} {r.operation:28} {r.status:10} {str(r.exit_code):>4}")
    print("-" * 96)
    print(f"Successful steps: {sum(r.status == 'SUCCESS' for r in results)}   Failed steps: {sum(r.status != 'SUCCESS' for r in results)}")


def main() -> int:
    p = argparse.ArgumentParser(description="SSH based Checkmk appliance deployment controller")
    p.add_argument("--inventory", default=str(ROOT / "config" / "inventory.json"))
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Package manifest with expected SHA256 values")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--parallel", type=int, default=4)
    sub = p.add_subparsers(dest="cmd", required=True)

    def targets(sp):
        sp.add_argument("--host", action="append")
        sp.add_argument("--group")

    for name in ("preflight", "status", "versions"):
        sp = sub.add_parser(name); targets(sp)

    sp = sub.add_parser("cleanup-versions"); targets(sp)
    sp.add_argument("--remove", action="append", help="Installed Checkmk version to remove; may be repeated")
    sp.add_argument("--all-unused", action="store_true", help="Select all unused versions for cleanup")
    sp.add_argument("--keep-latest", type=int, default=2, help="With --all-unused, keep the newest N installed versions (default: 2)")
    sp.add_argument("--execute", action="store_true", help="Actually delete versions; without this option cleanup is preview-only")

    sp = sub.add_parser("check-package")
    sp.add_argument("--file", required=True)

    sp = sub.add_parser("stage"); targets(sp)
    sp.add_argument("--file", required=True)
    sp.add_argument("--remote-dir", default="/var/tmp/cmk-deployment")
    sp.add_argument("--bwlimit", type=int, help="rsync bandwidth limit in KiB/s")
    sp.add_argument("--no-require-manifest", action="store_true")

    sp = sub.add_parser("install-cma"); targets(sp)
    sp.add_argument("--file", required=True)
    sp.add_argument("--remote-dir", default="/var/tmp/cmk-deployment")

    sp = sub.add_parser("install-cfw"); targets(sp)
    sp.add_argument("--file", required=True)
    sp.add_argument("--remote-dir", default="/var/tmp/cmk-deployment")
    sp.add_argument("--allow-unsigned-cfw", action="store_true")
    sp.add_argument("--reboot-timeout", type=int, default=1800)
    sp.add_argument("--yes", action="store_true", help="Stop running sites and continue without prompting for each appliance")

    sp = sub.add_parser("omd-update"); targets(sp)
    sp.add_argument("--site", action="append", help="Site name; if omitted, use sites configured for the host in inventory.json")
    sp.add_argument("--version", required=True)

    args = p.parse_args()
    inv = load_json(Path(args.inventory)) if args.cmd != "check-package" else {"hosts": {}}
    manifest = load_manifest(Path(args.manifest))

    if args.cmd == "check-package":
        local = Path(args.file).resolve()
        if not local.is_file():
            print(f"File not found: {local}", file=sys.stderr); return 2
        ok, msg = validate_expected_sha(local, manifest, require=True)
        print(f"[local] {msg}")
        return 0 if ok else 1

    runner = Runner(inv, args.dry_run, args.debug)
    hosts = select_hosts(inv, args)
    if not hosts:
        print("No hosts selected", file=sys.stderr); return 2
    results: list[Result] = []

    if args.cmd in {"preflight", "status", "versions"}:
        with ThreadPoolExecutor(max_workers=args.parallel) as ex:
            if args.cmd == "preflight":
                fn = runner.preflight_host
            elif args.cmd == "status":
                fn = lambda x: [runner.inventory_sites(x)]
            else:
                fn = lambda x: [runner.version_inventory(x)]
            futs = {ex.submit(fn, h): h for h in hosts}
            for fut in as_completed(futs): results.extend(fut.result())

    elif args.cmd == "cleanup-versions":
        for h in hosts:
            results.append(runner.cleanup_versions(h, args.remove, args.all_unused, args.keep_latest, args.execute))

    elif args.cmd == "stage":
        local = Path(args.file).resolve()
        if not local.is_file(): print(f"File not found: {local}", file=sys.stderr); return 2
        ok, msg = validate_expected_sha(local, manifest, require=not args.no_require_manifest)
        print(f"[local] {msg}")
        if not ok: return 1
        expected = sha256_file(local)
        with ThreadPoolExecutor(max_workers=args.parallel) as ex:
            futs = {ex.submit(runner.stage_host, h, local, args.remote_dir, args.bwlimit): h for h in hosts}
            for fut in as_completed(futs):
                r = fut.result(); results.append(r)
                if r.status == "SUCCESS":
                    remote_file = f"{args.remote_dir.rstrip('/')}/{local.name}"
                    results.append(runner.verify_remote_sha(r.host, remote_file, expected))

    elif args.cmd in {"install-cma", "install-cfw"}:
        local = Path(args.file).resolve()
        if not local.is_file(): print(f"File not found: {local}", file=sys.stderr); return 2
        ok, msg = validate_expected_sha(local, manifest, require=True)
        print(f"[local] {msg}")
        if not ok: return 1
        expected = sha256_file(local)
        entry = manifest_entry(manifest, local) or {}
        declared_type = entry.get("type")
        wanted_type = "cma" if args.cmd == "install-cma" else "cfw"
        if declared_type and declared_type != wanted_type:
            print(f"Manifest type mismatch: {declared_type} != {wanted_type}", file=sys.stderr); return 1
        remote_file = f"{args.remote_dir.rstrip('/')}/{local.name}"
        for h in hosts:
            vr = runner.verify_remote_sha(h, remote_file, expected); results.append(vr)
            if vr.status != "SUCCESS": continue
            if args.cmd == "install-cma":
                ins = runner.install_cma(h, remote_file)
                results.append(ins)
                if ins.status == "SUCCESS":
                    results.append(runner.version_inventory(h, "version_inventory_after_cma"))
            else:
                state_result, running_sites = runner.cfw_running_sites(h)
                results.append(state_result)
                if state_result.status != "SUCCESS":
                    continue

                if running_sites:
                    print(f"\n[{h}] Firmware update requires stopped sites.")
                    print(f"[{h}] Running sites: {', '.join(running_sites)}")
                    if args.dry_run:
                        print(f"[{h}] DRY-RUN: would stop these sites, perform the firmware update, and start only these sites again afterwards.")
                    elif not args.yes:
                        try:
                            answer = input(f"[{h}] Stop these sites and continue with the firmware update? [y/N]: ").strip().lower()
                        except EOFError:
                            answer = ""
                        if answer not in {"y", "yes", "j", "ja"}:
                            results.append(Result(h, "cfw_confirmation", "FAILED", now_iso(), now_iso(), 0, exit_code=2, message="Firmware update skipped by user"))
                            continue
                    stop_results = runner.cfw_stop_sites(h, running_sites)
                    results.extend(stop_results)
                    if any(r.status != "SUCCESS" for r in stop_results):
                        results.extend(runner.cfw_restore_sites(h, running_sites))
                        continue

                val = runner.validate_cfw(h, remote_file, args.allow_unsigned_cfw); results.append(val)
                if val.status != "SUCCESS":
                    if running_sites:
                        results.extend(runner.cfw_restore_sites(h, running_sites))
                    continue
                target = None
                for line in val.message.splitlines():
                    if line.startswith("TARGET_VERSION="): target = line.split("=",1)[1].strip()
                act = runner.activate_cfw(h); results.append(act)
                if act.status != "SUCCESS":
                    if running_sites:
                        results.extend(runner.cfw_restore_sites(h, running_sites))
                    continue
                verify = runner.wait_for_reconnect(h, target, args.reboot_timeout)
                results.append(verify)
                if verify.status == "SUCCESS" and running_sites:
                    results.extend(runner.cfw_restore_sites(h, running_sites))

    elif args.cmd == "omd-update":
        for h in hosts:
            sites = args.site if args.site else inv["hosts"][h].get("sites", [])
            if not sites:
                results.append(Result(h, "omd_update_config", "FAILED", now_iso(), now_iso(), 0, exit_code=2, message="No sites configured for host; define hosts.<name>.sites in inventory.json or use --site"))
                continue
            for site in sites:
                site_results = runner.omd_update(h, site, args.version)
                results.extend(site_results)
                if site_results and site_results[-1].status != "SUCCESS": break

    report = write_report(results)
    print_summary(results)
    print(f"\nReport: {report}")
    return 1 if any(r.status != "SUCCESS" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
