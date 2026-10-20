# SAP MaxDB Plugin

Checks the following things: General Status, Log/Database Utilization, Sessions, Backup Status

**Checkmk 2.2** please use mkp version >1.4 mkp version


Version 1.5.1 for testing with checkmk Support >2.3

New in Version 1.8.x

The original SAP MaxDB monitoring agent has been significantly improved and extended.

* Cross-platform support: The agent supports both Linux and Windows systems.
* Additional monitoring capabilities: New checks for database locks, performance, volumes, transactions, and data and log backups.
* Improved data collection: Structured JSON output for the new monitoring sections and enhanced processing of database information.
* Performance optimization: Parallel monitoring of multiple databases using multithreading and configurable timeouts.
* Improved configuration: Support for JSON configuration files that can be automatically generated and deployed through the Checkmk Agent Bakery.
* Flexible authentication: Support for both XUSER authentication and username/password authentication.
* Enhanced security: Configuration parameter validation, secure execution of external commands without shell access, and improved error handling.
* Extended monitoring: Additional metrics, graphs, and individually configurable warning and critical thresholds.
* Backward compatibility: Existing monitoring functionality and legacy configuration files remain supported.

System Requirements

Python 3.6 or newer must be installed on the monitored systems.

Python is required to execute the MaxDB agent plugin. The agent uses only modules from the Python standard library, so no additional Python packages are required.

Compatibility with older Python versions has been improved by removing modern type annotations.

Note: The code is designed to support Python 3.6 and newer, but compatibility has not yet been fully verified across all target platforms.

