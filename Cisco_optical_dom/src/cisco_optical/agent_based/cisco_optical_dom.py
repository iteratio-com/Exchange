from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    OIDEnd,
    Result,
    Service,
    SNMPSection,
    SNMPTree,
    State,
    StringTable,
    all_of,
    check_levels,
    contains,
    exists,
    startswith,
)


@dataclass
class Lane:
    lane: int
    rx_power: float | None = None
    tx_power: float | None = None


@dataclass
class OpticalInterface:
    ifindex: str
    ifname: str = ""
    admin_status: int | None = None
    oper_status: int | None = None
    data_ifname: str | None = None
    data_admin_status: int | None = None
    data_oper_status: int | None = None
    laser_status: int | None = None
    optics_type: str = ""
    rx_low: float | None = None
    tx_low: float | None = None
    rx_high: float | None = None
    tx_high: float | None = None
    port_type: int | None = None
    lanes: dict[int, Lane] = field(default_factory=dict)


Section = dict[str, OpticalInterface]

DEFAULT_DISCOVERY_PARAMETERS = {
    "discover_only_up": True,
}

DEFAULT_CHECK_PARAMETERS = {
    "use_device_thresholds": True,
    "rx_lower": ("no_levels", None),
    "rx_upper": ("no_levels", None),
    "tx_lower": ("no_levels", None),
    "tx_upper": ("no_levels", None),
}


_PHYSICAL_INTERFACE_PREFIXES = (
    "GigabitEthernet",
    "TenGigE",
    "TwentyFiveGigE",
    "FortyGigE",
    "FiftyGigE",
    "HundredGigE",
    "TwoHundredGigE",
    "FourHundredGigE",
    "EightHundredGigE",
)


def _to_int(value: str) -> int | None:
    try:
        return int(value) if value != "" else None
    except (TypeError, ValueError):
        return None


def _scaled(value: str, divisor: float) -> float | None:
    try:
        return float(value) / divisor if value != "" else None
    except (TypeError, ValueError):
        return None


def _find_data_interface(
    optics_ifname: str,
    interface_names: Mapping[str, str],
) -> tuple[str | None, str | None]:
    """Map IOS XR Optics0/0/0/x to its actual traffic interface.

    IOS XR exposes DOM controllers through pseudo interfaces named ``Optics...``.
    Their IF-MIB state can remain up even when the associated Ethernet interface
    is down.  The port path after ``Optics`` is shared with the actual interface,
    e.g. ``Optics0/0/0/0`` -> ``HundredGigE0/0/0/0``.
    """
    if not optics_ifname.startswith("Optics"):
        return None, None

    port_path = optics_ifname[len("Optics") :]
    if not port_path:
        return None, None

    candidates: list[tuple[str, str]] = []
    for ifindex, ifname in interface_names.items():
        if ifname.startswith(_PHYSICAL_INTERFACE_PREFIXES) and ifname.endswith(port_path):
            candidates.append((ifindex, ifname))

    if not candidates:
        return None, None

    # Prefer the longest interface name. This makes the choice deterministic
    # should a platform expose more than one speed-specific representation.
    return max(candidates, key=lambda entry: len(entry[1]))


def parse_cisco_optical_dom(string_table: Sequence[StringTable]) -> Section:
    if len(string_table) != 4:
        return {}

    if_name_table, if_status_table, controller_table, lane_table = string_table

    interface_names = {
        row[0]: row[1] for row in if_name_table if len(row) >= 2 and row[0] and row[1]
    }

    interface_status = {
        row[0]: (_to_int(row[1]), _to_int(row[2]))
        for row in if_status_table
        if len(row) >= 3 and row[0]
    }

    parsed: Section = {}

    for row in controller_table:
        if len(row) < 8:
            continue

        ifindex = row[0]
        if not ifindex:
            continue

        ifname = interface_names.get(ifindex, f"ifIndex {ifindex}")
        admin_status, oper_status = interface_status.get(ifindex, (None, None))

        data_ifindex, data_ifname = _find_data_interface(ifname, interface_names)
        data_admin_status, data_oper_status = (
            interface_status.get(data_ifindex, (None, None))
            if data_ifindex is not None
            else (None, None)
        )

        parsed[ifindex] = OpticalInterface(
            ifindex=ifindex,
            ifname=ifname,
            admin_status=admin_status,
            oper_status=oper_status,
            data_ifname=data_ifname,
            data_admin_status=data_admin_status,
            data_oper_status=data_oper_status,
            laser_status=_to_int(row[1]),
            optics_type=row[2],
            rx_low=_scaled(row[3], 100.0),
            tx_low=_scaled(row[4], 100.0),
            rx_high=_scaled(row[5], 100.0),
            tx_high=_scaled(row[6], 100.0),
            port_type=_to_int(row[7]),
        )

    for row in lane_table:
        if len(row) < 3 or not row[0]:
            continue

        try:
            ifindex, lane_raw = row[0].rsplit(".", 1)
            lane_number = int(lane_raw)
        except (ValueError, AttributeError):
            continue

        interface = parsed.get(ifindex)
        if interface is None:
            continue

        interface.lanes[lane_number] = Lane(
            lane=lane_number,
            rx_power=_scaled(row[1], 100.0),
            tx_power=_scaled(row[2], 100.0),
        )

    return parsed


snmp_section_cisco_optical_dom = SNMPSection(
    name="cisco_optical_dom",
    detect=all_of(
        startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.9.1.3"),
        contains(".1.3.6.1.2.1.1.1.0", "(8000)"),
        exists(".1.3.6.1.4.1.9.9.828.1.1.1.0"),
        exists(".1.3.6.1.4.1.9.9.828.1.1.2.1.*"),
    ),
    fetch=[
        # IF-MIB::ifName
        SNMPTree(
            base=".1.3.6.1.2.1.31.1.1.1",
            oids=[OIDEnd(), "1"],
        ),
        # IF-MIB::ifAdminStatus / ifOperStatus
        SNMPTree(
            base=".1.3.6.1.2.1.2.2.1",
            oids=[OIDEnd(), "7", "8"],
        ),
        # CISCO-OPTICAL-MIB::coiOpticalControllerTable
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.828.1.1.2.1",
            oids=[
                OIDEnd(),
                "2",
                "6",
                "7",
                "8",
                "9",
                "10",
                "13",
            ],
        ),
        # CISCO-OPTICAL-MIB::coiOpticalControllerPerLaneTable
        # Only RX and TX power are fetched; laser bias is intentionally omitted.
        SNMPTree(
            base=".1.3.6.1.4.1.9.9.828.1.1.3.1",
            oids=[OIDEnd(), "2", "3"],
        ),
    ],
    parse_function=parse_cisco_optical_dom,
)


def _data_interface_is_up(interface: OpticalInterface) -> bool:
    """Return True only if the associated traffic interface is admin/oper up."""
    if interface.data_ifname is None:
        return False
    return interface.data_admin_status == 1 and interface.data_oper_status == 1


def discover_cisco_optical_dom(
    params: Mapping[str, object],
    section: Section,
) -> DiscoveryResult:
    discover_only_up = bool(params.get("discover_only_up", True))

    for interface in section.values():
        if not interface.optics_type or not interface.lanes:
            continue

        if interface.optics_type.endswith(" CU"):
            # Skip copper optics, which do not have DOM metrics.
            continue

        if discover_only_up and not _data_interface_is_up(interface):
            continue

        yield Service(item=interface.ifname)


def _configured(levels: object) -> bool:
    return isinstance(levels, tuple) and len(levels) == 2 and levels[0] != "no_levels"


def _effective_levels(
    configured: object,
    device_threshold: float | None,
    *,
    use_device_thresholds: bool,
) -> object:
    if _configured(configured):
        return configured

    if use_device_thresholds and device_threshold is not None:
        # The device exposes alarm boundaries only: WARN and CRIT coincide.
        return ("fixed", (device_threshold, device_threshold))

    return ("no_levels", None)


def _interface_status_text(status: int | None) -> str:
    return {
        1: "UP",
        2: "DOWN",
        3: "TESTING",
    }.get(status, "UNKNOWN")


def check_cisco_optical_dom(
    item: str,
    params: Mapping[str, object],
    section: Section,
) -> CheckResult:
    interface = next(
        (entry for entry in section.values() if entry.ifname == item),
        None,
    )
    if interface is None:
        return

    yield Result(state=State.OK, summary=f"Optics: {interface.optics_type}")

    if interface.data_ifname is not None:
        yield Result(
            state=State.OK,
            notice=(
                f"Related interface: {interface.data_ifname}, "
                f"admin {_interface_status_text(interface.data_admin_status)}, "
                f"oper {_interface_status_text(interface.data_oper_status)}"
            ),
        )

        # The traffic interface is the authoritative state. If it is down, do
        # not raise DOM/laser alarms for a transceiver that is intentionally not
        # carrying traffic. The normal interface check covers this condition.
        if not _data_interface_is_up(interface):
            yield Result(
                state=State.OK,
                summary=f"Related interface {interface.data_ifname} is down, DOM evaluation skipped",
            )
            return
    else:
        yield Result(
            state=State.WARN,
            notice="No related traffic interface could be determined",
        )

    if interface.laser_status == 1:
        yield Result(state=State.OK, summary="Laser: up")
    elif interface.laser_status == 2:
        yield Result(state=State.CRIT, summary="Laser: down")
    elif interface.laser_status is not None:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Laser: state {interface.laser_status}",
        )

    use_device_thresholds = bool(params.get("use_device_thresholds", True))

    # Always expose the thresholds reported by CISCO-OPTICAL-MIB in the
    # service details. This makes it visible whether a transceiver/router
    # actually provides device thresholds independently of Checkmk rules.
    if interface.rx_low is None and interface.rx_high is None:
        yield Result(
            state=State.OK,
            notice="Device RX thresholds: not provided by device",
        )
    else:
        rx_parts: list[str] = []
        if interface.rx_low is not None:
            rx_parts.append(f"low {interface.rx_low:.2f} dBm")
        else:
            rx_parts.append("low not provided")
        if interface.rx_high is not None:
            rx_parts.append(f"high {interface.rx_high:.2f} dBm")
        else:
            rx_parts.append("high not provided")
        yield Result(
            state=State.OK,
            notice="Device RX thresholds: " + ", ".join(rx_parts),
        )

    if interface.tx_low is None and interface.tx_high is None:
        yield Result(
            state=State.OK,
            notice="Device TX thresholds: not provided by device",
        )
    else:
        tx_parts: list[str] = []
        if interface.tx_low is not None:
            tx_parts.append(f"low {interface.tx_low:.2f} dBm")
        else:
            tx_parts.append("low not provided")
        if interface.tx_high is not None:
            tx_parts.append(f"high {interface.tx_high:.2f} dBm")
        else:
            tx_parts.append("high not provided")
        yield Result(
            state=State.OK,
            notice="Device TX thresholds: " + ", ".join(tx_parts),
        )

    yield Result(
        state=State.OK,
        notice=(
            "Device alarm thresholds used for WARN and CRIT (identical boundaries) unless overridden by Checkmk rules"
            if use_device_thresholds
            else "Device thresholds are displayed but disabled for evaluation"
        ),
    )

    rx_lower = _effective_levels(
        params.get("rx_lower", ("no_levels", None)),
        interface.rx_low,
        use_device_thresholds=use_device_thresholds,
    )
    rx_upper = _effective_levels(
        params.get("rx_upper", ("no_levels", None)),
        interface.rx_high,
        use_device_thresholds=use_device_thresholds,
    )
    tx_lower = _effective_levels(
        params.get("tx_lower", ("no_levels", None)),
        interface.tx_low,
        use_device_thresholds=use_device_thresholds,
    )
    tx_upper = _effective_levels(
        params.get("tx_upper", ("no_levels", None)),
        interface.tx_high,
        use_device_thresholds=use_device_thresholds,
    )

    for lane_number in sorted(interface.lanes):
        lane = interface.lanes[lane_number]

        # Keep threshold evaluation and metrics, but move their verbose output
        # to the service details. The summary gets one compact line per lane.
        if lane.rx_power is not None:
            yield from check_levels(
                lane.rx_power,
                levels_lower=rx_lower,
                levels_upper=rx_upper,
                metric_name=f"cisco_optical_rx_power_lane_{lane_number}",
                label=f"Lane {lane_number} RX",
                render_func=lambda value: f"{value:.2f} dBm",
            )

        if lane.tx_power is not None:
            yield from check_levels(
                lane.tx_power,
                levels_lower=tx_lower,
                levels_upper=tx_upper,
                metric_name=f"cisco_optical_tx_power_lane_{lane_number}",
                label=f"Lane {lane_number} TX",
                render_func=lambda value: f"{value:.2f} dBm",
            )


check_plugin_cisco_optical_dom = CheckPlugin(
    name="cisco_optical_dom",
    service_name="Cisco Optical DOM %s",
    discovery_function=discover_cisco_optical_dom,
    discovery_default_parameters=DEFAULT_DISCOVERY_PARAMETERS,
    discovery_ruleset_name="cisco_optical_dom_discovery",
    check_function=check_cisco_optical_dom,
    check_default_parameters=DEFAULT_CHECK_PARAMETERS,
    check_ruleset_name="cisco_optical_dom",
)
