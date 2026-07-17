# Rubrik REST API Special Agent

## Function

**IMPORTANT: Migration from CSM to RSC**
The agent has been transitioned from the legacy CSM to the RSC GraphQL-only mode. Because of this architectural change, **existing rules must be recreated**.

The agent connects via GraphQL to the Rubrik Service Cloud (RSC) and creates piggyback data for nodes, including the following services:
* Cluster System Status
* Compliance 24 Hours (cluster-side)
* Disk
* Node Hardware Health
* Node Status (node-side)
* Bandwidth

It is highly recommended to use the **Dynamic Host Configuration** to automatically create the nodes as hosts.

## Discovered labels

* Host label for cluster hosts -> `rubrikDevice:cluster`
* Host label for nodes -> `rubrikDevice:node`

## Checkmk version compatibility

* The (deprecated) version for 2.1.0 is `rubrik_agent-0.9.3.mkp`.
* Current version for 2.2.0 is `rubrik_agent-1.2.3.mkp`.
* Current version for 2.3.0 and 2.4.0 using instance based CDM is `rubrik_agent-1.4.3.mkp`.
* Current version for 2.3.0 and 2.4.0 using cloud based RSC is `rubrik_agent-1.5.2.mkp`.

## Thanks!

Thanks to my colleague Mathias for supporting me by giving hints and and treating me to keep my code clean!

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
* 1.4.3-p1 Added graphing/rubrik.py for filesystem metric df_translation.
* 1.5.0 Switched the Rubrik special agent to RSC GraphQL-only mode, added mandatory cluster selection by cluster name or UUID, added secure password-store secret resolution, ensured RSC session tokens are deleted after use, enabled SSL certificate verification by default with explicit opt-out support, fixed degraded disk mapping for raidStatus values None and OPTIMAL, improved Node Hardware Health policy details, and fixed singleton section parsing for duplicate piggyback sources.
* 1.5.1 Added Rubrik Bandwidth check
* 1.5.2 Fixed the section list in the special agent rule
