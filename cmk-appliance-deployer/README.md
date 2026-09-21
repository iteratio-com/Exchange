# Checkmk Appliance Deployer

**THIS IS CURRENTLY IN TESTING**

## Dokumentation

**Version:** 0.2.7\
**Zweck:** Zentrale Verteilung und Installation von Checkmk-Versionen
und Checkmk-Appliance-Firmware sowie Durchführung von Site-Updates auf
mehreren Checkmk-Appliances.

------------------------------------------------------------------------

## 1. Übersicht

Der **Checkmk Appliance Deployer** ermöglicht die zentrale
Administration mehrerer Checkmk-Appliances von einer
Controller-Appliance aus.

Typische Aufgaben sind:

-   Checkmk-Installationspakete (`.cma`) auf Appliances verteilen
-   Checkmk-Appliance-Firmware (`.cfw`) verteilen und installieren
-   SHA256-Prüfung vor und nach der Übertragung
-   Checkmk-Sites auf eine neue Checkmk-Version aktualisieren
-   installierte Checkmk-Versionen und deren Verwendung anzeigen
-   nicht mehr verwendete Checkmk-Versionen kontrolliert entfernen
-   Status und Ergebnisse der einzelnen Schritte protokollieren
-   langsame Verbindungen mittels `rsync` und optionalem
    Bandbreitenlimit unterstützen

Die Kommunikation zwischen Controller und Ziel-Appliances erfolgt per
SSH.

Beispiel:

``` text
cmkvirt4             Controller
   |
   +--- SSH ---> cmkvirt3
   +--- SSH ---> cmkvirt5
   +--- SSH ---> cmkvirt6
```

------------------------------------------------------------------------

## 2. Voraussetzungen

### 2.1 Controller

Der Deployer wird auf einer zentralen Checkmk-Appliance ausgeführt,
beispielsweise:

``` text
cmkvirt4
```

Benötigt werden insbesondere:

-   Python 3
-   OpenSSH Client
-   `sha256sum`
-   optional `rsync`
-   SSH-Zugriff als `root` auf die Ziel-Appliances
-   ausreichend Speicherplatz für CMA- und CFW-Dateien

Prüfung:

``` bash
python3 --version
ssh -V
sha256sum --version
rsync --version
```

Falls `rsync` nicht vorhanden ist, kann die Übertragung grundsätzlich
über SSH erfolgen. Für langsame oder instabile Verbindungen ist `rsync`
jedoch zu bevorzugen.

### 2.2 Ziel-Appliances

Auf den Zielsystemen werden möglichst keine zusätzlichen Pakete
benötigt.

Vorausgesetzt werden die üblichen Bestandteile der Checkmk-Appliance:

-   SSH-Server
-   Python 3
-   Checkmk/OMD
-   Checkmk-Appliance-Pythonmodule für CMA/CFW-Funktionen
-   `sha256sum`

Der Deployer verwendet für Site-Informationen bewusst die OMD-Kommandos,
insbesondere:

``` bash
omd sites
omd status <SITE>
```

------------------------------------------------------------------------

## 3. SSH-Key für den Deployer erstellen

Für den automatisierten Zugriff empfiehlt sich ein eigener SSH-Key
ausschließlich für den Deployer.

Auf dem Controller als `root`:

``` bash
mkdir -p /root/.ssh
chmod 700 /root/.ssh
```

Anschließend einen Ed25519-Key erzeugen:

``` bash
ssh-keygen -t ed25519 \
  -f /root/.ssh/cmk_deploy \
  -C "cmk-deployer@cmkvirt4"
```

Für einen vollständig automatisierten Betrieb kann der Key ohne
Passphrase erstellt werden. In diesem Fall ist der Schutz des privaten
Keys besonders wichtig.

Die erzeugten Dateien sind:

``` text
/root/.ssh/cmk_deploy
/root/.ssh/cmk_deploy.pub
```

### 3.1 Dateirechte setzen

``` bash
chmod 700 /root/.ssh
chmod 600 /root/.ssh/cmk_deploy
chmod 644 /root/.ssh/cmk_deploy.pub
```

Kontrolle:

``` bash
ls -la /root/.ssh/
```

Der private Schlüssel darf ausschließlich für `root` lesbar sein.

------------------------------------------------------------------------

## 4. Public Key auf Ziel-Appliances installieren

Der öffentliche Schlüssel muss auf jede Ziel-Appliance übertragen
werden.

Beispiel:

``` bash
ssh-copy-id \
  -i /root/.ssh/cmk_deploy.pub \
  root@cmkvirt6
```

Alternativ kann der Inhalt von:

``` bash
cat /root/.ssh/cmk_deploy.pub
```

manuell in folgende Datei auf der Ziel-Appliance eingetragen werden:

``` text
/root/.ssh/authorized_keys
```

Empfohlene Rechte auf der Ziel-Appliance:

``` bash
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
```

### 4.1 Zugriff optional auf den Controller beschränken

Wenn die IP-Adresse des Controllers fest ist, kann der Key in
`authorized_keys` zusätzlich eingeschränkt werden.

Beispiel:

``` text
from="192.0.2.10" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... cmk-deployer@cmkvirt4
```

Dabei muss `192.0.2.10` durch die tatsächliche Adresse des Controllers
ersetzt werden.

Dadurch kann dieser SSH-Key nur von der angegebenen Quelladresse
verwendet werden.

------------------------------------------------------------------------

## 5. SSH-Konfiguration

Damit der Deployer den separaten Key automatisch verwendet, kann auf dem
Controller `/root/.ssh/config` verwendet werden.

Beispiel:

``` text
Host cmkvirt3 cmkvirt5 cmkvirt6
    User root
    IdentityFile /root/.ssh/cmk_deploy
    IdentitiesOnly yes
```

Rechte:

``` bash
chmod 600 /root/.ssh/config
```

Anschließend den Zugriff testen:

``` bash
ssh root@cmkvirt6 hostname
```

Erwartet wird beispielsweise:

``` text
cmkvirt6
```

Der Zugriff sollte ohne Passwortabfrage funktionieren.

Zusätzlich empfiehlt sich:

``` bash
ssh root@cmkvirt6 'omd sites'
```

------------------------------------------------------------------------

## 6. Deployer installieren

Archiv auf dem Controller entpacken, beispielsweise:

``` bash
cd /omd
unzip cmk-appliance-deployer-0.2.7.zip
```

oder:

``` bash
tar xzf cmk-appliance-deployer-0.2.7.tar.gz
```

Anschließend:

``` bash
cd /omd/cmk-appliance-deployer
chmod +x cmk_deploy.py
```

Syntax prüfen:

``` bash
python3 -m py_compile cmk_deploy.py
```

CLI testen:

``` bash
./cmk_deploy.py --help
```

------------------------------------------------------------------------

## 7. Verzeichnisstruktur

Eine typische Struktur sieht folgendermaßen aus:

``` text
cmk-appliance-deployer/
├── cmk_deploy.py
├── README.md
├── CHANGELOG.md
├── config/
│   └── inventory.json
├── packages/
│   ├── manifest.json
│   ├── check-mk-enterprise-2.4.0p36.cma
│   └── cma-1.7.22.cfw
└── reports/
```

Die eigentlichen Installationsdateien werden unter:

``` text
packages/
```

abgelegt.

------------------------------------------------------------------------

## 8. Inventory konfigurieren

Die Appliances werden zentral in:

``` text
config/inventory.json
```

definiert.

Beispiel:

``` json
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
      "group": "test",
      "sites": [
        "test3"
      ]
    },
    "cmkvirt5": {
      "ssh_host": "cmkvirt5",
      "group": "production",
      "sites": [
        "prod"
      ]
    },
    "cmkvirt6": {
      "ssh_host": "cmkvirt6",
      "group": "test",
      "sites": [
        "test6"
      ]
    }
  }
}
```

### Gruppen

`group` ist eine frei verwendbare Gruppierung.

Beispiele:

``` text
test
production
development
location-a
location-b
```

Damit können Aktionen auf eine Gruppe begrenzt werden:

``` bash
./cmk_deploy.py status --group test
```

### Sites

Die zu einer Appliance gehörenden Checkmk-Sites können im Inventory
hinterlegt werden:

``` json
"sites": [
  "test6"
]
```

Diese Information kann insbesondere bei OMD-Updates verwendet werden.

------------------------------------------------------------------------

## 9. Pakete und SHA256-Manifest

CMA- und CFW-Dateien werden im Verzeichnis:

``` text
packages/
```

abgelegt.

Beispiel:

``` text
packages/cma-1.7.22.cfw
```

Die erwarteten SHA256-Prüfsummen werden in:

``` text
packages/manifest.json
```

hinterlegt.

Beispiel:

``` json
{
  "packages": {
    "cma-1.7.22.cfw": {
      "type": "cfw",
      "sha256": "e3c8fb9127f4efc36e16222b68d1dab772755653ea19714d5dc2597d2e6f23d4"
    }
  }
}
```

Prüfsumme einer Datei ermitteln:

``` bash
sha256sum packages/cma-1.7.22.cfw
```

Der Deployer prüft die Datei zweimal:

1.  lokal vor der Übertragung
2.  auf der Ziel-Appliance nach der Übertragung

Dadurch wird verhindert, dass eine beschädigte oder falsche Datei
installiert wird.

------------------------------------------------------------------------

## 10. Paket lokal prüfen

Vor einer Verteilung kann das Paket geprüft werden:

``` bash
./cmk_deploy.py check-package \
  --file packages/cma-1.7.22.cfw
```

Bei erfolgreicher Prüfung wird die SHA256-Prüfsumme bestätigt.

------------------------------------------------------------------------

## 11. Preflight und Status

Vor größeren Aktionen empfiehlt sich ein Preflight.

Beispiel:

``` bash
./cmk_deploy.py preflight
```

Nur eine Appliance:

``` bash
./cmk_deploy.py preflight --host cmkvirt6
```

Eine Gruppe:

``` bash
./cmk_deploy.py preflight --group test
```

Zusätzlich kann der Status abgefragt werden:

``` bash
./cmk_deploy.py status
```

------------------------------------------------------------------------

## 12. Pakete verteilen

Beispiel für ein CFW-Paket:

``` bash
./cmk_deploy.py stage \
  --file packages/cma-1.7.22.cfw
```

Nur auf eine Appliance:

``` bash
./cmk_deploy.py stage \
  --host cmkvirt6 \
  --file packages/cma-1.7.22.cfw
```

Die Datei wird auf der Ziel-Appliance standardmäßig unter:

``` text
/var/tmp/cmk-deployment/
```

abgelegt.

Danach erfolgt die Remote-SHA256-Prüfung.

------------------------------------------------------------------------

## 13. Langsame Verbindungen und Bandbreitenlimit

Für langsam angebundene Appliances kann die Übertragung mit `rsync`
erfolgen.

Ein Bandbreitenlimit kann über `--bwlimit` gesetzt werden.

Beispiel:

``` bash
./cmk_deploy.py stage \
  --host cmkvirt6 \
  --file packages/cma-1.7.22.cfw \
  --bwlimit 500
```

Das Limit gilt pro `rsync`-Übertragung.

Der Vorteil von `rsync` besteht insbesondere darin, dass bei einer
unterbrochenen Übertragung nicht zwingend die komplette Datei erneut
übertragen werden muss.

------------------------------------------------------------------------

## 14. Checkmk-Version installieren -- CMA

Zunächst die CMA-Datei verteilen:

``` bash
./cmk_deploy.py stage \
  --file packages/check-mk-enterprise-2.4.0p36.cma
```

Anschließend installieren:

``` bash
./cmk_deploy.py install-cma \
  --file packages/check-mk-enterprise-2.4.0p36.cma
```

Nur auf einer Appliance:

``` bash
./cmk_deploy.py install-cma \
  --host cmkvirt6 \
  --file packages/check-mk-enterprise-2.4.0p36.cma
```

Der Deployer orientiert sich hierbei an der Installationslogik der
Checkmk-Appliance.

Nach erfolgreicher Installation kann die Versionsübersicht ausgegeben
werden.

------------------------------------------------------------------------

## 15. Installierte Checkmk-Versionen anzeigen

Mit:

``` bash
./cmk_deploy.py versions
```

werden die installierten Checkmk-Versionen und deren Verwendung
angezeigt.

Nur eine Appliance:

``` bash
./cmk_deploy.py versions --host cmkvirt6
```

Beispielausgabe:

``` text
[cmkvirt6] Installed Checkmk versions:
[cmkvirt6]   2.3.0p50.cee             sites: test6
[cmkvirt6]   2.4.0p36.cee             sites: -
[cmkvirt6]   2.5.0p12.pro (default)   sites: -

[cmkvirt6] Sites:
[cmkvirt6]   test6 -> 2.3.0p50.cee
```

Damit lässt sich schnell erkennen:

-   welche Checkmk-Versionen installiert sind
-   welche Version Standard ist
-   welche Site welche Version verwendet
-   welche Version möglicherweise nicht mehr benötigt wird

------------------------------------------------------------------------

## 16. Checkmk-Site aktualisieren

Der Deployer unterstützt OMD-Site-Updates.

Für ältere Checkmk-Versionen wird sinngemäß die ältere Update-Syntax
verwendet:

``` bash
omd -f -V <VERSION> update --conflict=install <SITE>
```

Für Checkmk 2.5 und neuer wird die neue Update-Syntax verwendet:

``` bash
omd -V <VERSION> update \
  --pre-flight=abort \
  --skeleton=install \
  --confirm-version \
  --confirm-edition \
  <SITE>
```

Vor dem eigentlichen Update wird die Site kontrolliert gestoppt bzw.
ausgehängt.

Die Site-Zuordnung kann aus dem Inventory verwendet oder über die CLI
gezielt überschrieben werden.

Vor einem produktiven Site-Update sollte immer ein aktuelles Backup
vorhanden sein.

------------------------------------------------------------------------

## 17. Appliance-Firmware installieren -- CFW

### 17.1 Firmware verteilen

Zuerst die Firmware auf die Appliance übertragen:

``` bash
./cmk_deploy.py stage \
  --host cmkvirt6 \
  --file packages/cma-1.7.22.cfw
```

### 17.2 Firmware installieren

Anschließend:

``` bash
./cmk_deploy.py install-cfw \
  --host cmkvirt6 \
  --file packages/cma-1.7.22.cfw
```

Bei mehreren Appliances:

``` bash
./cmk_deploy.py install-cfw \
  --file packages/cma-1.7.22.cfw
```

Firmware-Installationen erfolgen bewusst **sequenziell**.

------------------------------------------------------------------------

## 18. Site-Behandlung beim Firmware-Update

Vor einem Firmware-Update müssen die Checkmk-Sites der Appliance
gestoppt sein.

Der Deployer verwendet dafür:

``` bash
omd sites
```

und prüft den Zustand der gefundenen Sites.

Beispielsweise:

``` text
[cmkvirt6] Running sites: test6
```

Anschließend erfolgt eine interaktive Rückfrage:

``` text
[cmkvirt6] Firmware update requires stopped sites.
[cmkvirt6] Stop these sites and continue with the firmware update? [y/N]:
```

Bei Bestätigung werden die laufenden Sites gestoppt.

Der grundsätzliche Ablauf ist:

``` text
Site-Zustand ermitteln
        |
        v
laufende Sites merken
        |
        v
Benutzer bestätigen lassen
        |
        v
Sites stoppen
        |
        v
CFW validieren
        |
        v
Firmware aktivieren
        |
        v
Appliance rebooten
        |
        v
auf SSH warten
        |
        v
Firmware-Version prüfen
        |
        v
vorher laufende Sites wieder starten
```

### Wichtig

Der ursprüngliche Zustand wird berücksichtigt.

Beispiel vor dem Update:

``` text
prod        running
test        stopped
monitoring  running
```

Nach dem Firmware-Update werden nur:

``` text
prod
monitoring
```

wieder gestartet.

`test` bleibt gestoppt.

------------------------------------------------------------------------

## 19. Firmware-Update ohne Rückfrage

Für einen bewusst unbeaufsichtigten Lauf kann `--yes` verwendet werden:

``` bash
./cmk_deploy.py install-cfw \
  --file packages/cma-1.7.22.cfw \
  --yes
```

Damit wird die interaktive Bestätigung übersprungen.

Die Appliances werden trotzdem weiterhin nacheinander aktualisiert.

Für produktive Firmware-Updates ist der interaktive Modus vorzuziehen.

------------------------------------------------------------------------

## 20. Verhalten nach dem Firmware-Reboot

Nach Aktivierung der Firmware startet die Appliance neu.

Der Deployer wartet anschließend darauf, dass:

1.  SSH wieder erreichbar ist
2.  die Appliance antwortet
3.  die erwartete Firmware-Version aktiv ist

Der Standardzeitraum für einen Firmware-Reboot ist großzügig bemessen,
da Appliance-Updates mehrere Minuten benötigen können.

Erst danach werden zuvor laufende Sites wieder gestartet.

------------------------------------------------------------------------

## 21. Alte Checkmk-Versionen aufräumen

Nicht mehr verwendete Checkmk-Versionen können über `cleanup-versions`
geprüft werden.

Zunächst nur anzeigen:

``` bash
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6
```

Eine bestimmte Version auswählen:

``` bash
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6 \
  --remove 2.3.0p29.cee
```

Die tatsächliche Löschung erfolgt erst mit:

``` bash
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6 \
  --remove 2.3.0p29.cee \
  --execute
```

### Sicherheitsprüfung

Eine Version darf nicht entfernt werden, solange eine Site sie
verwendet.

Vor einer Bereinigung empfiehlt sich:

``` bash
./cmk_deploy.py versions --host cmkvirt6
```

Damit kann die Site-/Versionszuordnung nochmals kontrolliert werden.

Es empfiehlt sich außerdem, mindestens eine geeignete vorherige
Checkmk-Version für einen möglichen Rollback aufzubewahren.

------------------------------------------------------------------------

## 22. Parallelität

Nicht alle Operationen werden parallel ausgeführt.

Für ungefährliche bzw. lesende/verteilende Aktionen können mehrere
Appliances gleichzeitig bearbeitet werden, beispielsweise:

-   Preflight
-   Status
-   Stage

Der Standardwert für die Parallelität beträgt:

``` text
4
```

Kritische Aktionen werden dagegen bewusst sequenziell durchgeführt,
insbesondere:

-   CMA-Installation
-   CFW-Installation
-   OMD-Site-Update

Dadurch ist bei Updates immer eindeutig erkennbar, welche Appliance
gerade bearbeitet wird.

------------------------------------------------------------------------

## 23. Reports

Für ausgeführte Aktionen werden Reports im Verzeichnis:

``` text
reports/
```

erstellt.

Beispiel:

``` text
reports/report-20260921-135753.json
```

Eine Ergebnisübersicht sieht beispielsweise so aus:

``` text
Result
================================================================================================
Host                 Site            Operation                    Status       RC
------------------------------------------------------------------------------------------------
cmkvirt6             -               verify_remote_sha256         SUCCESS       0
cmkvirt6             -               validate_cfw                 SUCCESS       0
------------------------------------------------------------------------------------------------
Successful steps: 2   Failed steps: 0
```

Die Reports eignen sich insbesondere zur späteren Nachvollziehbarkeit
von Deployment- und Updatevorgängen.

------------------------------------------------------------------------

## 24. Typischer CMA-Workflow

Ein vollständiger Ablauf für eine neue Checkmk-Version kann
beispielsweise so aussehen:

### 1. Datei ablegen

``` bash
cp check-mk-enterprise-2.5.0p12.cma packages/
```

### 2. SHA256 ermitteln

``` bash
sha256sum packages/check-mk-enterprise-2.5.0p12.cma
```

### 3. SHA256 in `manifest.json` eintragen

``` json
{
  "packages": {
    "check-mk-enterprise-2.5.0p12.cma": {
      "type": "cma",
      "sha256": "<SHA256>"
    }
  }
}
```

### 4. Paket prüfen

``` bash
./cmk_deploy.py check-package \
  --file packages/check-mk-enterprise-2.5.0p12.cma
```

### 5. Paket verteilen

``` bash
./cmk_deploy.py stage \
  --file packages/check-mk-enterprise-2.5.0p12.cma
```

### 6. CMA installieren

``` bash
./cmk_deploy.py install-cma \
  --file packages/check-mk-enterprise-2.5.0p12.cma
```

### 7. Versionszustand kontrollieren

``` bash
./cmk_deploy.py versions
```

### 8. Sites aktualisieren

Anschließend können die vorgesehenen Sites kontrolliert auf die neue
Version aktualisiert werden.

------------------------------------------------------------------------

## 25. Typischer CFW-Workflow

### 1. Firmware ablegen

``` bash
cp cma-1.7.22.cfw packages/
```

### 2. SHA256 prüfen

``` bash
sha256sum packages/cma-1.7.22.cfw
```

### 3. Manifest aktualisieren

``` json
{
  "packages": {
    "cma-1.7.22.cfw": {
      "type": "cfw",
      "sha256": "e3c8fb9127f4efc36e16222b68d1dab772755653ea19714d5dc2597d2e6f23d4"
    }
  }
}
```

### 4. Paket verteilen

``` bash
./cmk_deploy.py stage \
  --file packages/cma-1.7.22.cfw
```

### 5. Firmware installieren

``` bash
./cmk_deploy.py install-cfw \
  --file packages/cma-1.7.22.cfw
```

Bei jeder Appliance werden die laufenden Sites angezeigt und das Stoppen
wird bestätigt.

------------------------------------------------------------------------

## 26. Troubleshooting

### SSH-Verbindung funktioniert nicht

Direkt testen:

``` bash
ssh root@cmkvirt6 hostname
```

Mit dem dedizierten Key:

``` bash
ssh \
  -i /root/.ssh/cmk_deploy \
  -o IdentitiesOnly=yes \
  root@cmkvirt6 \
  hostname
```

### Connection refused

Beispiel:

``` text
ssh: connect to host 192.168.178.106 port 22: Connection refused
```

Das bedeutet, dass die Netzwerkverbindung zum Host grundsätzlich
zustande kommt, aber auf Port 22 aktuell kein SSH-Dienst erreichbar ist.

Mögliche Ursachen:

-   Appliance startet gerade neu
-   SSH-Dienst läuft nicht
-   Firewall-Regel
-   falsche Adresse oder falscher Port

### Connection timed out

Beispiel:

``` text
ssh: connect to host ... port 22: Connection timed out
```

Typische Ursachen:

-   Routing
-   Firewall
-   Appliance nicht erreichbar
-   falsche IP-Adresse
-   Zielsystem ausgeschaltet

### SHA256 stimmt nicht

Lokal prüfen:

``` bash
sha256sum packages/<DATEI>
```

Remote prüfen:

``` bash
ssh root@cmkvirt6 \
  'sha256sum /var/tmp/cmk-deployment/<DATEI>'
```

Beide Werte müssen mit dem Wert aus `packages/manifest.json`
übereinstimmen.

### Firmware-Update meldet laufende Sites

Prüfen:

``` bash
ssh root@cmkvirt6 'omd sites'
```

und beispielsweise:

``` bash
ssh root@cmkvirt6 'omd status test6'
```

Im normalen interaktiven CFW-Workflow übernimmt der Deployer das
kontrollierte Stoppen.

### Syntax des Deployers prüfen

Nach Änderungen am Skript:

``` bash
python3 -m py_compile cmk_deploy.py
```

Zusätzlich:

``` bash
./cmk_deploy.py --help
./cmk_deploy.py install-cfw --help
```

------------------------------------------------------------------------

## 27. Sicherheitsempfehlungen

Für den Betrieb sollten mindestens folgende Punkte berücksichtigt
werden:

-   eigener SSH-Key ausschließlich für den Deployer
-   Ed25519 als Schlüsseltyp
-   private Keys ausschließlich für `root` lesbar
-   Zugriff nach Möglichkeit über `from=` in `authorized_keys` auf den
    Controller begrenzen
-   Controller besonders schützen, da von dort Root-Zugriff auf mehrere
    Appliances möglich ist
-   keine privaten SSH-Keys im Deployer-Verzeichnis oder Git-Repository
    speichern
-   CMA-/CFW-Dateien vor Installation mittels SHA256 prüfen
-   Firmware-Updates interaktiv durchführen
-   vor Checkmk-Site-Updates aktuelle Backups erstellen
-   Reports nach Änderungen kontrollieren
-   alte Checkmk-Versionen erst entfernen, wenn keine Site sie mehr
    verwendet

------------------------------------------------------------------------

## 28. Empfohlene Rechte auf dem Controller

Beispiel:

``` bash
chown -R root:root /omd/cmk-appliance-deployer
```

Für den SSH-Bereich:

``` bash
chmod 700 /root/.ssh
chmod 600 /root/.ssh/cmk_deploy
chmod 644 /root/.ssh/cmk_deploy.pub
chmod 600 /root/.ssh/config
```

Das Deployment-Verzeichnis sollte nicht für unprivilegierte Benutzer
beschreibbar sein, da dort Pakete und Konfigurationen liegen, die
anschließend mit Root-Rechten auf andere Appliances übertragen bzw.
installiert werden.

------------------------------------------------------------------------

## 29. Kurzreferenz

``` bash
# Hilfe
./cmk_deploy.py --help

# Preflight
./cmk_deploy.py preflight

# Status
./cmk_deploy.py status

# Paket prüfen
./cmk_deploy.py check-package --file packages/<DATEI>

# Paket verteilen
./cmk_deploy.py stage --file packages/<DATEI>

# Paket nur auf einen Host verteilen
./cmk_deploy.py stage --host cmkvirt6 --file packages/<DATEI>

# Langsame Verbindung
./cmk_deploy.py stage --host cmkvirt6 --file packages/<DATEI> --bwlimit 500

# CMA installieren
./cmk_deploy.py install-cma --file packages/<DATEI>.cma

# CFW installieren
./cmk_deploy.py install-cfw --file packages/<DATEI>.cfw

# CFW unbeaufsichtigt
./cmk_deploy.py install-cfw --file packages/<DATEI>.cfw --yes

# Versionen und Site-Zuordnung
./cmk_deploy.py versions

# Cleanup-Vorschau
./cmk_deploy.py cleanup-versions --host cmkvirt6

# Version tatsächlich entfernen
./cmk_deploy.py cleanup-versions \
  --host cmkvirt6 \
  --remove <VERSION> \
  --execute
```

------------------------------------------------------------------------

## 30. Betriebsempfehlung

Für produktive Änderungen empfiehlt sich grundsätzlich folgende
Reihenfolge:

``` text
Preflight
   ↓
Paket lokal prüfen
   ↓
Stage
   ↓
Remote SHA256 prüfen
   ↓
eine Test-Appliance aktualisieren
   ↓
Ergebnis und Report kontrollieren
   ↓
weitere Appliances sequenziell aktualisieren
   ↓
Versions-/Site-Zuordnung kontrollieren
   ↓
erst danach gegebenenfalls alte Versionen bereinigen
```

Dadurch bleiben die einzelnen Schritte nachvollziehbar und Fehler können
früh erkannt werden.

