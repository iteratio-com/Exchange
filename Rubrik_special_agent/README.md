# Rubrik REST API Special Agent

## Download

Current version: **1.5.7** — [rubrik_agent-1.5.7.mkp](rubrik_agent-1.5.7.mkp).

## Function

**IMPORTANT: Migration to RSC**

Since version 1.5.0, the agent uses Rubrik Security Cloud (RSC) GraphQL exclusively. Because of this architectural change, **existing rules for the legacy integration must be recreated**.

The agent provides the following services:

* Cluster System Status
* Compliance 24 Hours (cluster-side)
* Disk
* Node Hardware Health
* Node Status (node-side)
* Bandwidth
* Storage Runway
* Event Logwatch

Monitor a single cluster by name or UUID, or select **SaaS** in the special agent rule to monitor all clusters visible to the service account.

Node data is provided via piggyback. In SaaS mode, cluster hosts are also provided via piggyback. **Dynamic Host Configuration** is recommended to create these hosts automatically.

### Event Logwatch

Event Logwatch is reported on the querying host rather than via piggyback.

Event state is stored separately for each querying host and cluster UUID, including when switching clusters in SaaS mode.

At least one of the following event filters must be configured:

* Severity
* Activity types
* Activity status
* Object type

Without a filter, Event Logwatch is disabled, even if the section is selected in the rule. This is intended to reduce the risk of lockouts caused by unfiltered event requests.

Filter values can be identified by inspecting requests from the Rubrik SaaS Events page using the browser developer tools.

### Storage Runway

The configurable Storage section reports the estimated remaining capacity in days. Missing runway values result in **UNKNOWN** rather than being interpreted as zero days.

### Node Hardware Health

The **Rubrik Node Hardware Health** ruleset provides exceptions for selected hardware health policies. An unhealthy policy can be ignored or mapped to **OK**, **WARN**, or **CRIT**. Healthy policies remain **OK**; unconfigured unhealthy policies remain **CRIT**.

The worst evaluated state determines the service state. Original findings remain visible in the service details, including ignored or mapped policies. If all returned policies are ignored, the service reports **OK** with an explicit summary. If no policies are returned, the service reports **UNKNOWN**.

### Connection settings

The request timeout is configurable. SSL certificate verification is enabled by default and can be explicitly disabled in the special agent rule.

## Discovered labels

* Cluster hosts: `rubrikDevice:cluster`
* Node hosts: `rubrikDevice:node`

## Checkmk version compatibility

**Compatibility:** Checkmk 2.3–2.5. Successfully tested with Checkmk 2.5.0.

Earlier packages:

* Checkmk 2.1.0: `rubrik_agent-0.9.3.mkp` (deprecated)
* Checkmk 2.2.0: `rubrik_agent-1.2.3.mkp`
* Checkmk 2.3.0 and 2.4.0 with instance-based CDM: `rubrik_agent-1.4.3.mkp`
* Checkmk 2.3.0 and 2.4.0 with cloud-based RSC: `rubrik_agent-1.5.7.mkp`

## Thanks!

Thanks to my colleague Mathias for his helpful suggestions and support in keeping the code clean.

Thanks to **Leon Buhleier** ([Leon.Buhleier@sva.de](mailto:Leon.Buhleier@sva.de)) for contributing the metric translation fix for correct scaling of Rubrik Disk graphs.

Thanks to **Sebastian Häger** ([Sebastian.Haeger@sva.de](mailto:Sebastian.Haeger@sva.de)) for contributing version 1.5.3: Event Logwatch with filters, configurable request timeout, and SaaS-wide cluster monitoring with cluster piggyback hosts.

## Changelog

* 0.1.0 Initial version
* 0.2.0 Special agent operational
* 0.3.0 Added additional API endpoints
* 0.3.1 Added further API endpoints
* 0.4.0 Added piggyback output
* 0.4.5 Added System Status check
* 0.5.0 Added hardware health monitoring for partitions and FRUs
* 0.6.0 Added Disk check
* 0.6.1 Cleaned up default values
* 0.7.0 Added Node Status and Compliance Report checks
* 0.8.0 Normalized naming
* 0.9.0 Added filesystem levels
* 0.9.2 Updated description
* 0.9.3 Fixed import
* 0.9.5 Added type annotations by mgo
* 0.9.6 Added Checkmk 2.2.0 compatibility
* 0.9.7 Adjusted hardware health parsing
* 0.9.8 Added snapshot thresholds
* 0.9.9 Added metrics for the Compliance Report service
* 1.0.0 Applied minor patches
* 1.1.0 Consolidated special agent endpoint requests
* 1.1.1 Fixed node disk status parser
* 1.1.2 Added check man pages
* 1.2.0 Added service selection options
* 1.2.1 Ensured tokens are deleted after execution
* 1.2.2 Added handling for tokens that are already in use
* 1.2.3 Added special agent errors to the Check_MK service output
* 1.3.0 Temporarily ignored SSD life-left output in Node Hardware Health
* 1.4.0 Ported to Checkmk 2.4.0
* 1.4.1 Added a migration function for existing rulesets
* 1.4.2 Refactored and cleaned up the code
* 1.4.3 Set the minimum required Checkmk version to 2.3.0b1
* 1.4.3-p1 Fixed Rubrik Disk graph scaling with filesystem metric translation, contributed by Leon Buhleier (Leon.Buhleier@sva.de)
* 1.5.0 Switched the Rubrik special agent to RSC GraphQL-only mode, added mandatory cluster selection by cluster name or UUID, added secure password-store secret resolution, ensured RSC session tokens are deleted after use, enabled SSL certificate verification by default with explicit opt-out support, fixed degraded disk mapping for raidStatus values NONE and OPTIMAL, improved Node Hardware Health policy details, and fixed singleton section parsing for duplicate piggyback sources.
* 1.5.1 Added Rubrik Bandwidth check
* 1.5.2 Fixed the section list in the special agent rule
* 1.5.3 Added Event Logwatch with filters, configurable request timeout, and SaaS-wide cluster monitoring with cluster piggyback hosts, contributed by Sebastian Häger (Sebastian.Haeger@sva.de)
* 1.5.4 Code optimization and bug fixes
* 1.5.5 Fixed bandwidth query, restored Storage section selection with UNKNOWN handling for missing runway data, and hardened event handling with required filters and temporary state storage.
* 1.5.6 Added selectable hardware health policy exceptions (Ignore/OK/WARN/CRIT), preserved monitoring of other components, and clarified Event Logwatch filter requirements.
* 1.5.7 Fixed Event Logwatch state isolation by querying host and cluster UUID, including SaaS cluster switching.
