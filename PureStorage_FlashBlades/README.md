# PureStorage FlashBlade Monitoring for Checkmk

The **PureStorage FlashBlade Monitoring** package extends Checkmk with comprehensive monitoring capabilities for **Pure Storage FlashBlade** appliances.

Using the official **Pure Storage REST API**, the package collects health, capacity, hardware, and alert information and integrates seamlessly into the native Checkmk monitoring environment.

It includes a dedicated **Special Agent**, automatic service discovery, configurable rulesets, and native Checkmk agent-based checks, making it easy to deploy and operate in both small and large environments.

---

## Features

- Native Checkmk Special Agent
- Official Pure Storage REST API integration
- Automatic service discovery
- Native Checkmk ruleset integration
- Checkmk Password Store support
- Efficient API communication
- Multiple FlashBlade systems can be monitored

---

## Monitored Components

The package currently monitors:

- FlashBlade Array Health
- Blades
- Drives
- Hardware Components
- Buckets
- Filesystem Capacity
- Active Alerts
- SSL Certificates

---

## Requirements

- Checkmk **2.3** or newer
- Pure Storage FlashBlade
- REST API enabled
- Read-only API Token (recommended)

