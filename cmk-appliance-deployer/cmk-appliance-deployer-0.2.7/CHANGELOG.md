# Changelog

## 0.2.7

- Fix: `cmk_deploy.py` ist wieder syntaktisch gueltig; der in 0.2.6 eingefuehrte f-string-Fehler im eingebetteten CFW-Remote-Skript wurde entfernt.
- Das CFW-Remote-Skript wird nun als Plain-String-Template erzeugt, damit Python-Set-Literale und Backslashes nicht vom Controller-f-string interpretiert werden.
- `cfw_site_state` und die CFW-Validierung verwenden weiterhin `omd sites` / `omd status <site>` statt `webconf.sites`.
- Geprueft mit `python3 -m py_compile`, `--help`, `install-cfw --help`, `versions --help`, `cleanup-versions --help` sowie separatem Compile-Test des erzeugten Remote-CFW-Skripts.

## 0.2.2

- Default fuer `--parallel` von 2 auf 4 erhoeht.
- Sites koennen pro Host zentral in `config/inventory.json` definiert werden.
- `omd-update --site` ist optional; ohne Angabe werden die konfigurierten Host-Sites verwendet.
- Dokumentation fuer `group` und zentrale Site-Konfiguration erweitert.

## 0.2.0

- expected SHA256 manifest for CMA/CFW packages
- local and remote SHA256 verification
- CMA installation aligned with Checkmk Appliance webconf logic
- CFW validation using native appliance firmware helpers
- signed firmware required by default
- firmware pre-update script execution
- seamless firmware transition guard
- reboot/reconnect/firmware-version verification
- Checkmk 2.5-specific OMD update arguments from appliance GUI
- `omd umount --kill` and `update-apache-config` handling

## 0.2.1 documentation refresh

- README auf Version 0.2.1 aktualisiert
- Default-Werte dokumentiert
- Parallelitaetsverhalten der Unterkommandos dokumentiert
- `--bwlimit` als Limit pro rsync-Transfer erklaert
- Host-/Gruppenauswahl beschrieben
- interne Standard-Timeouts dokumentiert

## 0.2.3

- Fix `omd-update` on older Checkmk appliances where `cma.CheckmkVersion` is not available.
- Target Checkmk versions are now parsed locally by the deployment controller.
- `omd-update` no longer depends on `cma.parse_check_mk_version()` or `cma.CheckmkVersion` on the remote appliance.
- With `--debug`, the selected OMD update syntax is shown per host.

## 0.2.4

- `versions` command added to show installed Checkmk versions, default version, and site-to-version mapping.
- `cleanup-versions` added with preview mode, used-version protection, and optional removal of unused versions.
- CMA installation now prints the version inventory after a successful install.
- CFW validation output reduced by suppressing noisy appliance firmware logger output.

## 0.2.6

- Interactive CFW safety prompt per appliance when running sites are detected.
- The deployer records which sites were running, stops and unmounts them before firmware validation, and starts only those sites again after a successful reboot/version check.
- `install-cfw --yes` allows explicitly unattended CFW updates without the per-appliance confirmation prompt.
- A declined prompt skips that appliance without touching its sites.
- Existing `versions` and safe `cleanup-versions` functionality documented in the README.

## 0.2.4

- `versions` command added to show installed Checkmk versions, default version, and site-to-version mapping.
- `cleanup-versions` added with preview mode, used-version protection, and optional removal of unused versions.
- CMA installation now prints the version inventory after a successful install.
- CFW validation output reduced by suppressing noisy appliance firmware logger output.

## 0.2.6

- Interactive CFW safety prompt per appliance when running sites are detected.
- The deployer records which sites were running, stops and unmounts them before firmware validation, and starts only those sites again after a successful reboot/version check.
- `install-cfw --yes` allows explicitly unattended CFW updates without the per-appliance confirmation prompt.
- A declined prompt skips that appliance without touching its sites.
- Existing `versions` and safe `cleanup-versions` functionality documented in the README.

## 0.2.6

- CFW Site-State-Erkennung nutzt jetzt `omd sites` als Quelle der vorhandenen Sites.
- Laufzustand wird nur fuer die von `omd sites` gelieferten Sites mit `omd status <site>` geprueft.
- Keine Abhaengigkeit mehr von `webconf.sites.not_stopped_sites()` im CFW-Workflow.
- Kurze 30-Sekunden-Timeouts fuer `omd sites` und einzelne Statusabfragen verhindern langes Haengen.
