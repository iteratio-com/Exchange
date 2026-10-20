Cisco Optical DOM

Overview

This Checkmk extension provides optical transceiver monitoring for Cisco IOS XR Software (8000) devices using the CISCO-OPTICAL-MIB.

The extension was built and tested with Checkmk 2.4 on Cisco 8000 Series devices.

Features

* Monitoring of optical RX and TX power levels
* Performance metrics and graphing for RX/TX optical power
* Configurable warning and critical thresholds through Checkmk rules
* Support for device-provided optical alarm thresholds
* Physical-interface-aware service discovery
* Per-lane optical monitoring and status information
* Automatic exclusion of copper interfaces
* Integrated Checkmk check documentation

Requirements

* Checkmk 2.3 or later
* Cisco IOS XR devices supporting CISCO-OPTICAL-MIB
* SNMP access enabled and configured

Installation

Install the MKP using the Checkmk Extension Packages interface or the command line:

mkp add cisco_optical_dom-1.3.7.mkp
mkp enable cisco_optical_dom 1.3.7

After installation, perform a service discovery on the Cisco devices.


Changelog

Version 1.3.7

* Removed copper interfaces from optical monitoring.

Notes

This extension has been developed and validated specifically for Checkmk 2.4 and Cisco 8000 Series devices.

Compatibility with other Cisco platforms or Checkmk versions has not been verified.
