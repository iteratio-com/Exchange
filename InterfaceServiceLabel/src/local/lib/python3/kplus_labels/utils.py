#!/usr/bin/env python3

from cmk.utils.paths import tmp_dir, var_dir
from typing import Any
from pathlib import Path
import json

SERVICE_LABELS_JSON_FILE = f"{tmp_dir}/interface_labels.json"
SERVICE_LABELS_JSON_FILE_BKP = f"{var_dir}/interface_labels.json"


def load_json_file(
    file_name: str = SERVICE_LABELS_JSON_FILE, file_name_bkp: str = SERVICE_LABELS_JSON_FILE_BKP
) -> dict[str, Any]:
    if Path(file_name).exists():
        # Normal WAY
        try:
            with open(file_name, "r") as f:
                data = f.read()
            data = json.loads(data)
        except Exception:
            data = {}
    elif Path(file_name_bkp).exists():
        # NO TMP FILE ANY MORE, COPY FILE
        try:
            with open(file_name_bkp, "r") as f:
                data = f.read()
            data = json.loads(data)
            with open(file_name, "w") as f:
                f.write(json.dump(data))
        except Exception:
            data = {}
    else:
        data = {}
    return data


def get_additional_external_labels(
    host_name: str, item_name: str, service_prefix: str = "Interface "
) -> dict[str, str]:
    """Get Additional External Labels

    Args:
        host_name (str): Host Name
        item_name (str): Item which is looking for
        service_prefix (str, optional): Prefix of Service. Defaults to "Interface ".

    Returns:
        dict[str, str]: Dictionary of Labels
    """
    json_data = load_json_file(file_name=SERVICE_LABELS_JSON_FILE)
    return json_data.get(host_name, {}).get(f"{service_prefix}{item_name}", {})
