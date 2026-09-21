# Checkmk Appliance Deployer 0.2.7

Agentloser Deployment-Controller fuer Checkmk Appliances per SSH.

## Neu in 0.2.x

- Hersteller-/Soll-SHA256 ueber `packages/manifest.json`
- lokale SHA256-Pruefung **vor** dem Transfer
- Remote-SHA256-Pruefung **nach** dem Transfer und nochmals vor Installation
- CMA-Installation nach der Logik der Appliance-GUI (`webconf/pages/cmk_versions.py`)
- CFW-Validierung ueber die nativen Appliance-Funktionen aus `webconf.pages.firmware`
- CFW: Signatur-, Archiv- und Pre-Update-Pruefung
- CFW: standardmaessig nur seamless Updates (gleicher Major, gleicher oder naechster Minor)
- CFW: Firmware nach `/ro/firmware.cfw`, Reboot, SSH-Reconnect und Versionspruefung
- OMD Update Syntax fuer Checkmk <2.5 und >=2.5 entsprechend der Appliance-GUI
- `omd umount --kill` und optionales `update-apache-config`

## Voraussetzungen

Controller:

- Python 3.10+
- OpenSSH
- `rsync` empfohlen

Appliance:

- SSH root Zugriff ohne interaktive Passwortabfrage
- Python 3 mit `cma` und `webconf` (normale Checkmk Appliance)
- `sha256sum`
- `omd`

## Konfiguration

```bash
cp config/inventory.example.json config/inventory.json
cp packages/manifest.example.json packages/manifest.json
```

Beispiel `inventory.json`:

```json
{
  "defaults": {
    "ssh_user": "root",
    "ssh_port": 22,
    "connect_timeout": 10,
    "use_rsync": true,
    "ssh_options": [
      "ServerAliveInterval=15",
      "ServerAliveCountMax=4",
      "ControlMaster=auto",
      "ControlPersist=10m",
      "ControlPath=~/.ssh/cmk-deploy-%C"
    ]
  },
  "hosts": {
    "cmkvirt3": {
      "ssh_host": "cmkvirt3",
      "group": "test"
    }
  }
}
```


## Default-Werte und Parallelitaet

Die folgenden Werte gelten in Version 0.2.7, solange sie nicht per CLI oder `inventory.json` ueberschrieben werden.

| Einstellung | Default | Bedeutung |
|---|---:|---|
| `--parallel` | `4` | Maximal vier Hosts gleichzeitig fuer `preflight`, `status` und `stage`. |
| `--bwlimit` | nicht gesetzt | Keine kuenstliche Bandbreitenbegrenzung. Gilt nur fuer `rsync` und wird in KiB/s angegeben; beim `scp`-Fallback wird der Wert nicht angewendet. |
| `ssh_user` | nicht hart codiert | Im Beispiel-Inventar `root`. Fehlt der Wert, verwendet OpenSSH den aktuellen lokalen Benutzer. |
| `ssh_port` | OpenSSH-Default `22` | Im Beispiel-Inventar explizit auf `22` gesetzt. |
| `connect_timeout` | `10` Sekunden | Timeout fuer den Aufbau einer SSH-Verbindung. |
| `use_rsync` | `true` | `rsync` wird verwendet, wenn es auf dem Controller vorhanden ist; sonst faellt der Deployer auf `scp` zurueck. |
| `--remote-dir` | `/var/tmp/cmk-deployment` | Ablageort fuer CMA/CFW auf der Ziel-Appliance. |
| `--reboot-timeout` | `1800` Sekunden | Bei CFW maximal 30 Minuten auf Wiedererreichbarkeit und Versionspruefung warten. |
| Remote Shell Command Timeout | `3600` Sekunden | Interner Default fuer normale Remote-Kommandos. |
| Remote Python Timeout | `7200` Sekunden | Interner Default fuer laengere Appliance-Operationen wie CMA/CFW-Validierung. |
| OMD Update Timeout je Schritt | `7200` Sekunden | Maximal zwei Stunden fuer einen einzelnen Update-Schritt. |
| `--allow-unsigned-cfw` | aus | Unsigned CFW wird standardmaessig abgelehnt. |
| `--dry-run` | aus | Befehle werden standardmaessig wirklich ausgefuehrt. |
| `--debug` | aus | Erweiterte Debug-Ausgabe muss explizit aktiviert werden. |

### Welche Befehle laufen parallel?

Aktuell ist die Parallelisierung bewusst auf risikoarme Operationen beschraenkt:

```text
preflight     parallel, Default: 4 Hosts
status        parallel, Default: 4 Hosts
stage         parallel, Default: 4 Hosts
install-cma   sequenziell
install-cfw   sequenziell
omd-update    sequenziell
```

Beispiel mit vier parallelen Transfers:

```bash
./cmk_deploy.py --parallel 4 stage \
  --file packages/my-checkmk.cma
```

Bei einer langsamen WAN-Anbindung sollte beachtet werden, dass `--bwlimit` **pro Transfer** gilt. Beispiel:

```bash
./cmk_deploy.py --parallel 2 stage \
  --file packages/my-checkmk.cma \
  --bwlimit 500
```

Damit koennen zwei Transfers gleichzeitig laufen, jeweils mit maximal 500 KiB/s. Die theoretische Gesamtlast liegt damit bei bis zu etwa 1000 KiB/s plus Protokoll-Overhead.

Wenn keine Parallelitaet gewuenscht ist:

```bash
./cmk_deploy.py --parallel 1 stage \
  --file packages/my-checkmk.cma \
  --bwlimit 500
```

### Standard SSH Optionen

Das Beispiel-Inventar verwendet zusaetzlich:

```text
ServerAliveInterval=15
ServerAliveCountMax=4
ControlMaster=auto
ControlPersist=10m
ControlPath=~/.ssh/cmk-deploy-%C
```

Damit werden bestehende SSH-Verbindungen wiederverwendet. Bei einer unterbrochenen Verbindung helfen die Keepalive-Werte dabei, einen Ausfall zu erkennen.


### Gruppen und Sites zentral in `inventory.json`

`group` ist ein frei waehlbares Label fuer die Host-Auswahl. Es veraendert nichts auf der Checkmk-Appliance. Typische Werte sind z. B. `test`, `production`, `berlin` oder `customer-a`.

Beispiel:

```json
{
  "hosts": {
    "cmkvirt3": {
      "ssh_host": "cmkvirt3",
      "group": "test",
      "sites": ["mysite", "testsite"]
    },
    "cmkvirt5": {
      "ssh_host": "cmkvirt5",
      "group": "production",
      "sites": ["prod"]
    }
  }
}
```

Damit kann z. B. nur die Test-Gruppe angesprochen werden:

```bash
./cmk_deploy.py stage --group test --file packages/my-checkmk.cma
```

Die Site-Namen koennen ebenfalls direkt je Host in `inventory.json` stehen. Bei `omd-update` ist `--site` deshalb optional. Ohne `--site` verwendet der Deployer die fuer den jeweiligen Host unter `sites` konfigurierten Sites:

```bash
./cmk_deploy.py omd-update --group test --version 2.5.0p1.cce
```

Fuer `cmkvirt3` wuerden in diesem Beispiel automatisch `mysite` und `testsite` aktualisiert. Ein explizites `--site` ueberschreibt die Site-Liste fuer den aktuellen Aufruf:

```bash
./cmk_deploy.py omd-update --host cmkvirt3 --site mysite --version 2.5.0p1.cce
```

So reicht fuer die Zieldefinition eine zentrale Datei: `config/inventory.json`.

### Host-Auswahl

Wird weder `--host` noch `--group` angegeben, werden alle Hosts aus `config/inventory.json` ausgewaehlt.

Einzelner Host:

```bash
./cmk_deploy.py preflight --host cmkvirt3
```

Mehrere einzelne Hosts:

```bash
./cmk_deploy.py preflight \
  --host cmkvirt3 \
  --host cmkvirt4
```

Gruppe:

```bash
./cmk_deploy.py preflight --group test
```

Alle Hosts:

```bash
./cmk_deploy.py preflight
```

## SHA256 Manifest

Der Dateiname im Manifest muss exakt dem Paketnamen entsprechen:

```json
{
  "packages": {
    "my-checkmk.cma": {
      "type": "cma",
      "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    },
    "my-firmware.cfw": {
      "type": "cfw",
      "sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
    }
  }
}
```

Der Sollwert sollte vom offiziellen Checkmk Download stammen.

Nur lokale Pruefung:

```bash
./cmk_deploy.py check-package --file packages/my-checkmk.cma
```

## Preflight

```bash
./cmk_deploy.py preflight --host cmkvirt3
```

## Langsames / fortsetzbares Staging

500 KiB/s:

```bash
./cmk_deploy.py stage \
  --host cmkvirt3 \
  --file packages/my-checkmk.cma \
  --bwlimit 500
```

Ablauf:

1. Soll-SHA aus Manifest lesen
2. lokale Datei hashen
3. bei Abweichung sofort abbrechen
4. per rsync uebertragen
5. SHA256 auf der Appliance pruefen

## CMA installieren

Die Datei muss vorher staged sein.

```bash
./cmk_deploy.py install-cma \
  --host cmkvirt3 \
  --file packages/my-checkmk.cma
```

Vor der Installation wird die Remote-Datei erneut gegen die Manifest-SHA geprueft.

Die CMA-Logik entspricht der Appliance-GUI:

- Dateiname / Plattform pruefen
- Archivgroesse und Struktur pruefen
- Commercial Edition pruefen
- `cma.info` pruefen
- `MIN_VERSION` gegen Appliance Firmware pruefen
- nach `/omd/versions` entpacken
- `/omd/versions/default` setzen
- `<version>/lib/cma/post-install` ausfuehren

## OMD Site Update

```bash
./cmk_deploy.py omd-update \
  --host cmkvirt3 \
  --site mysite \
  --version 2.5.0p1.cce
```

Fuer Checkmk >= 2.5:

```text
omd -V VERSION update --pre-flight=abort --skeleton=install \
    --confirm-version --confirm-edition SITE
```

Fuer aeltere Versionen:

```text
omd -f -V VERSION update --conflict=install SITE
```

Vorher werden `omd stop` und `omd umount --kill` ausgefuehrt. Anschliessend wird, falls von der Zielversion unterstuetzt, `update-apache-config` aufgerufen und die Site wieder gestartet.

## CFW Firmware installieren

**Vorher Backup und Wartungsfenster sicherstellen.** Alle Sites muessen gestoppt sein.

```bash
./cmk_deploy.py install-cfw \
  --host cmkvirt3 \
  --file packages/my-firmware.cfw
```

Der Controller:

1. prueft die Manifest-SHA lokal
2. prueft die staged Datei remote
3. verwendet die Appliance-eigenen Firmware-Prueffunktionen
4. prueft Archivstruktur und interne Hashes
5. prueft die Firmware-Signatur
6. fuehrt das Pre-Update-Script aus
7. akzeptiert automatisch nur seamless Updates
8. legt die validierte Firmware als `/ro/firmware.cfw` ab
9. rebootet die Appliance
10. wartet auf SSH
11. prueft `cma.version()` gegen die Zielversion

Unsigned Firmware wird standardmaessig abgelehnt. Fuer bewusst verwendete Developer-Builds existiert:

```bash
--allow-unsigned-cfw
```

Das sollte nicht fuer regulaere Produktions-Firmware verwendet werden.

## Dry Run

Globale Optionen muessen vor dem Unterkommando stehen:

```bash
./cmk_deploy.py --dry-run --debug omd-update \
  --host cmkvirt3 --site mysite --version 2.5.0p1.cce
```

## Reports

Jeder Lauf schreibt:

```text
reports/report-YYYYMMDD-HHMMSS.json
reports/latest.json
```

## Empfohlener Ablauf

```text
check-package
    -> preflight
    -> stage
    -> install-cma
    -> omd-update
```

Firmware separat:

```text
check-package
    -> preflight
    -> Sites stoppen
    -> stage
    -> install-cfw
    -> Reboot / automatische Verifikation
```

## Output / Debugging (0.2.1)

Every remote operation is prefixed with the inventory host, for example:

```text
[local] SHA256 OK: 9797...
[cmkvirt3] START verify_remote_sha256
[cmkvirt3] OK    verify_remote_sha256 (0.12s)
[cmkvirt3]   /var/tmp/cmk-deployment/check-mk-...cma: OK
[cmkvirt3] START install_cma
[cmkvirt3]   CMA: validating filename ...
[cmkvirt3]   CMA: package version=2.3.0p50.cee, firmware=..., minimum firmware=...
[cmkvirt3]   CMA: extracting ... to /omd/versions
[cmkvirt3]   CMA: running lib/cma/post-install
```

`--debug` no longer prints the complete inline remote Python program. Remote failures are printed immediately, including stdout/stderr. The CMA installer also contains compatibility fallbacks for older appliance `cma` modules.

### Compatibility with older appliance firmware

`omd-update` determines the command syntax from the target Checkmk version on the controller itself. It does not require `CheckmkVersion` or `parse_check_mk_version()` from the remote appliance's `cma` Python module. This allows old appliances to be upgraded to newer Checkmk releases.

The syntax selection is:

- target `< 2.5.0`: `omd -f -V VERSION update --conflict=install SITE`
- target `>= 2.5.0`: `omd -V VERSION update --pre-flight=abort --skeleton=install --confirm-version --confirm-edition SITE`


## Checkmk-Versionen und Site-Zuordnung anzeigen

Mit `versions` zeigt der Deployer pro Appliance die installierten Checkmk-Versionen, die Default-Version und die von Sites verwendeten Versionen:

```bash
./cmk_deploy.py versions --host cmkvirt6
```

Beispiel:

```text
[cmkvirt6] Installed Checkmk versions:
[cmkvirt6]   2.3.0p50.cee             sites: test6
[cmkvirt6]   2.4.0p36.cee             sites: -
[cmkvirt6]   2.5.0p12.pro (default)    sites: -
[cmkvirt6] Sites:
[cmkvirt6]   test6                     -> 2.3.0p50.cee
```

Nach einer erfolgreichen CMA-Installation wird diese Uebersicht automatisch ausgegeben.

## Alte Checkmk-Versionen sicher aufraeumen

Ohne `--execute` ist `cleanup-versions` immer nur eine Vorschau:

```bash
./cmk_deploy.py cleanup-versions --host cmkvirt6
```

Eine konkrete unbenutzte Version vormerken:

```bash
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6 \
  --remove 2.3.0p29.cee
```

Erst mit `--execute` wird geloescht:

```bash
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6 \
  --remove 2.3.0p29.cee \
  --execute
```

Alle unbenutzten Versionen entfernen, aber die zwei neuesten installierten Versionen behalten:

```bash
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6 \
  --all-unused \
  --keep-latest 2 \
  --execute
```

Eine Version, die noch von einer Site verwendet wird, wird immer blockiert und nicht geloescht.

## Interaktives CFW-Update

`install-cfw` laeuft bewusst sequenziell. Vor jeder Appliance wird geprueft, welche Sites aktuell laufen. Sind Sites aktiv, erscheint standardmaessig eine Rueckfrage:

```text
[cmkvirt6] Firmware update requires stopped sites.
[cmkvirt6] Running sites: test6
[cmkvirt6] Stop these sites and continue with the firmware update? [y/N]:
```

Bei `y`/`yes`/`j`/`ja` merkt sich der Deployer genau diese laufenden Sites, stoppt und unmountet sie, validiert/installiert die Firmware, wartet auf den Reboot und startet danach nur die Sites wieder, die vorher liefen. Bereits vorher gestoppte Sites bleiben gestoppt.

Beispiel:

```bash
./cmk_deploy.py install-cfw \
  --host cmkvirt6 \
  --file packages/cma-1.7.22.cfw
```

Fuer einen bewusst unbeaufsichtigten Lauf kann die Rueckfrage mit `--yes` uebersprungen werden:

```bash
./cmk_deploy.py install-cfw \
  --file packages/cma-1.7.22.cfw \
  --yes
```

`--yes` aendert nicht die Reihenfolge: CFW-Updates werden weiterhin Appliance fuer Appliance ausgefuehrt, nicht parallel.

### CFW: Site-Erkennung

Beim Firmware-Update verwendet der Deployer bewusst die OMD-CLI als Quelle der Sites:

```bash
omd sites
```

Fuer jede dort gelistete Site wird anschliessend der Laufzustand mit `omd status <site>` ermittelt. Die Python-Funktion `webconf.sites.not_stopped_sites()` wird nicht verwendet, damit der Workflow auch auf aelteren Appliance-Versionen nicht an GUI-internen Abhaengigkeiten haengt.
