#!/usr/bin/env python3

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Literal

import cmk.gui.config as my_config
import cmk.utils.paths as my_paths
import livestatus
import paramiko
import yaml
from cmk.gui.watolib.sites import SiteManagement
from kplus_labels import utils

HOME_PATH = os.environ["OMD_ROOT"]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    filename=f"{HOME_PATH}/var/log/service_label_generator.log",
)


#    _     _           ____  _        _                _    ____ ___
#   | |   (_)_   _____/ ___|| |_ __ _| |_ _   _ ___   / \  |  _ \_ _|
#   | |   | \ \ / / _ \___ \| __/ _` | __| | | / __| / _ \ | |_) | |
#   | |___| |\ V /  __/___) | || (_| | |_| |_| \__ \/ ___ \|  __/| |
#   |_____|_| \_/ \___|____/ \__\__,_|\__|\__,_|___/_/   \_\_|  |___|
#


class LiveStatusApi(object):
    def __init__(self, site=None):
        self.sites = SiteManagement.load_sites()
        self.local_site = my_config.omd_site()
        self.conn = {}
        all_livestatus_url = self.get_all_sites_livestatus_url()
        if site is None:
            self.sites = list(all_livestatus_url)
        elif isinstance(site, str):
            self.sites = [
                site,
            ]
        elif isinstance(site, list):
            self.sites = site
        for s in self.sites:
            if len(all_livestatus_url[s]) == 1:
                self.conn[s] = livestatus.SingleSiteConnection(all_livestatus_url[s][0])
            elif len(all_livestatus_url[s]) == 2:
                live_url = all_livestatus_url[s][0]
                tls = all_livestatus_url[s][1]
                self.conn[s] = livestatus.SingleSiteConnection(socketurl=live_url, tls=tls)

    def get_all_sites_livestatus_url(self) -> dict[str, Any]:
        """Receive all livestatus sites

        Returns:
            Sites: All Sites
        """
        live_sites = {}
        for site in self.sites:
            socket = self.sites[site].get("socket", ())
            if socket[0] == "local":
                live_sites[site] = (f"unix:{my_paths.livestatus_unix_socket}",)
            elif socket[0] == "tcp":
                address = ":".join(str(s) for s in socket[1].get("address", ()))
                tls = True if socket[1].get("tls", ())[0] == "encrypted" else False
                live_sites[site] = (f"tcp:{address}", tls)
        return live_sites

    def execute_call(
        self,
        query: str,
        sites: list[str] | None = None,
        live_type: Literal["query", "command"] = "query",
    ) -> dict[str, Any]:
        if sites is None:
            sites = self.sites
        data = {}
        for site in sites:
            live_func = {
                "query": self.conn[site].query,
                "command": self.conn[site].command,
            }.get(live_type, self.conn[site].query)
            try:
                data[site] = live_func(query)
            except Exception as e:
                logging.error(f"Error during connection to site {site}: {e!r}")
                pass
        return data

    def get_site(self, host_name: str) -> str:
        """Get Site to a Hostname

        Args:
            host_name (str): Host Name

        Returns:
            str: Site Name
        """
        results = self.execute_call(
            query=f"GET hosts\nColumns: name\nFilter: name = {host_name}\n", live_type="query"
        )
        for monitoring_site, live_results in results.items():
            if live_results:
                return monitoring_site
        return None

    def query_host_service_labels(
        self,
        query: str = """GET services\nColumns: host_name description service_plugin_output service_labels\nFilter: description ~~ Interface""",
    ) -> dict[str, Any]:
        """Query Interface Service for Service Labels

        Args:
            query (_type_, optional): _description_. Defaults to
            'GET services\nColumns: host_name description service_plugin_output service_labels\nFilter: description ~~ Interface'.

        Returns:
            dict[str, Any]: dictionary containing labels and Summary Line
        """
        out = {}
        for i, j in self.execute_call(query=query).items():
            for hostname, service, current_output, service_labels in j:
                if service.endswith(" Dom"):
                    continue
                out.setdefault(hostname, {})
                out[hostname].setdefault(service, {})
                out[hostname][service] = {
                    "labels": service_labels,
                    "output": current_output.split(", (")[0][1:-1],
                }
        return out


#    _____                 _   _
#   |  ___|   _ _ __   ___| |_(_) ___  _ __  ___
#   | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
#   |  _|| |_| | | | | (__| |_| | (_) | | | \__ \
#   |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
#


def get_config_yaml(config_file: str) -> dict[str, Any] | None:
    """Read Config YAML File

    Args:
        config_file (str): Config path

    Returns:
        dict[str, Any] | None: Config Dictionary
    """

    class Loader(yaml.SafeLoader):
        def __init__(self, stream):
            self._root = os.path.split(stream.name)[0]
            # Loader, self
            super().__init__(stream)

        def include(self, node):
            filename = os.path.join(self._root, self.construct_scalar(node))
            with open(filename, "r") as f:
                return yaml.load(f, Loader)

    Loader.add_constructor("!include", Loader.include)

    config_file_path = Path(config_file)
    if config_file_path.is_file():
        logging.info(f"Reading File: {config_file}")
        with open(config_file, "r") as f:
            return yaml.load(f, Loader=Loader)
    else:
        logging.error(f"File: {config_file} is not available")
        return None


def write_tmp_file(labels: dict[str, Any]):
    """Write Tmp Json files for Label pickup

    Args:
        labels (dict[str, Any]): Labels Dict
    """

    logging.debug(f"Writing Json file to {utils.SERVICE_LABELS_JSON_FILE}")
    logging.debug(f"And writing Json file to {utils.SERVICE_LABELS_JSON_FILE_BKP}")
    with open(utils.SERVICE_LABELS_JSON_FILE, "w") as f:
        f.write(json.dumps(labels))
    with open(utils.SERVICE_LABELS_JSON_FILE_BKP, "w") as f:
        f.write(json.dumps(labels))
    # with open("/tmp/interface.json", "w") as f:
    #     f.write(json.dumps(labels))


def distribute_file(
    CONFIG_FILE_STR: str = utils.SERVICE_LABELS_JSON_FILE,
    CONFIG_FILE_BACKUP: str = utils.SERVICE_LABELS_JSON_FILE_BKP,
):
    external_sites = {}
    master_site = ""
    for site, site_infos in SiteManagement.load_sites().items():
        socket = site_infos.get("socket", [])
        if socket[0] == "tcp":
            external_sites[site] = socket[1].get("address", ())
        if socket[0] == "local":
            master_site = site
    if external_sites:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        for external_site, site_ip in external_sites.items():
            logging.debug(
                f"Copy File {CONFIG_FILE_STR} to {external_site}@{site_ip[0]}:22 -> {CONFIG_FILE_STR.replace(master_site, external_site)}"
                f"AND  File {CONFIG_FILE_BACKUP} to {external_site}@{site_ip[0]}:22 -> {CONFIG_FILE_BACKUP.replace(master_site, external_site)}"
            )
            try:
                client.connect(hostname=site_ip[0], port=22, username=external_site, timeout=5)
                sftp_cli = client.open_sftp()
                sftp_cli.put(
                    localpath=CONFIG_FILE_STR,
                    remotepath=CONFIG_FILE_STR.replace(master_site, external_site),
                )
                sftp_cli.put(
                    localpath=CONFIG_FILE_BACKUP,
                    remotepath=CONFIG_FILE_BACKUP.replace(master_site, external_site),
                )
                sftp_cli.close()
                client.close()
            except Exception as e:
                logging.error(f"Failed to copy the file: {CONFIG_FILE_STR} or {CONFIG_FILE_BACKUP}")
                logging.error(f"Failed to copy the file: Error: {e!r}")


def parse_arguments(argv=None) -> argparse.Namespace:
    """Argument Parser

    Args:
        argv (sysArgv, optional): Arguments from script. Defaults to None.

    Returns:
        argparse.Namespace: Args Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug", action="store_true", help="Enable Debug-Level in logging")
    parser.add_argument(
        "--yaml_file",
        type=str,
        default=f"{HOME_PATH}/local/bin/service_label_config.yaml",
        help=f"Read the config File, defaults to: {HOME_PATH}/local/bin/service_label_config.yaml",
    )

    parser.add_argument("-v", action="store_true", help="Enable verbose output")
    return parser.parse_args(argv)


def read_and_compair_lables(lq_data: dict[str, Any], config: dict[str, Any]):
    if not config or not config.get("pattern"):
        logging.error("No Search Pattern Found, exiting")
        sys.exit(2)

    mk_file_sorted = {}
    for host, interface_infos in lq_data.items():
        for interface_name, interface_data in interface_infos.items():
            service_description = interface_data.get("output", "")
            logging.debug(f"{host}: {interface_name}: {service_description}")

            if not service_description:
                continue

            interface_labels = {}

            for pattern, settings in config.get("pattern", {}).items():
                pattern = re.compile(pattern=pattern)
                match = re.match(pattern=pattern, string=service_description)
                if not match:
                    logging.debug(
                        f"Pattern: {pattern!r} -> DOES NOT MATCH -> {service_description}"
                    )
                    continue
                if match.group(1).lower() in settings.get("ignore_values", []):
                    logging.debug(
                        f"Skipping, since {match.group(1)} is in {settings.get('ignore_values',[])}"
                    )
                    continue

                interface_labels = {}
                interface_labels.update(settings.get("static_labels", {}))

                for key, value in settings.get("custom_keys", {}).items():
                    found_string = re.sub(pattern=pattern, repl=value, string=service_description)
                    interface_labels.update({key: found_string})

            logging.debug(f"Current found (new) Labels: {interface_labels!r}")
            current_interface_labels = mk_file_sorted.get(host, {}).get(interface_name, {})
            logging.debug(f"Current Interface Labels: {current_interface_labels!r}")

            # Add
            if  interface_labels:
                logging.debug("should add entries")
                # if interface_data.get("labels", {}):
                #     for key, value in interface_data.get("labels", {}).items():
                #         if l_v := interface_labels.get(key):
                #             logging.debug(f"Label: {key} already in lq-data, skip adding")
                #             if l_v != value:
                #                 logging.error(
                #                     f"YAML should set: {key}:{l_v} but it is already set to {key}:{value}, skipping"
                #                 )
                #             try:
                #                 del interface_labels[key]
                #             except Exception as e:
                #                 logging.debug(f"Got Exception: {e!r}, passing still")
                #                 pass

                mk_file_sorted.setdefault(host, {})
                mk_file_sorted[host].setdefault(interface_name, {})
                mk_file_sorted[host][interface_name].update(interface_labels)

                continue

            # # Remove
            # if current_interface_labels and not interface_labels:
            #     logging.debug("should delete labels")
            #     try:
            #         del mk_file_sorted[host][interface_name]
            #     except Exception as e:
            #         logging.debug(f"Got Exception: {e!r}, passing still")
            #         pass

            # # Now Compare
            # if current_interface_labels and interface_labels:
            #     logging.debug("compare labels")
            #     if current_interface_labels != interface_labels:
            #         tmp = {}
            #         for key, value in interface_labels.items():
            #             if (c_v := current_interface_labels.get(key)) and c_v != value:

            #                 mk_file_sorted[host][interface_name].update({key: value})
            #             if (
            #                 cmk_label := interface_data.get("labels", {}).get(key)
            #             ) and cmk_label != value:
            #                 logging.error(
            #                     f"{host}: {interface_name} has already a differend value for {key}: current {cmk_label} should be {value}"
            #                 )
            #             if not (cmk_label := interface_data.get("labels", {}).get(key)):
            #                 mk_file_sorted[host][interface_name].update({key: value})
    write_tmp_file(mk_file_sorted)
    distribute_file()
    return 0


#          __  __           _
#         |  \/  |   __ _  (_)  _ __
#         | |\/| |  / _` | | | | '_ \
#         | |  | | | (_| | | | | | | |
#         |_|  |_|  \__,_| |_| |_| |_|
#


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)

    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.debug(f"Args: {args}")
    if args.v:
        s = logging.StreamHandler()
        logger.addHandler(s)
    lq = LiveStatusApi()
    livestatus_data = lq.query_host_service_labels()
    if not livestatus_data:
        logging.error("No livestatus informations, exiting")
        return 2

    config = get_config_yaml(config_file=args.yaml_file)
    return read_and_compair_lables(lq_data=livestatus_data, config=config)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
