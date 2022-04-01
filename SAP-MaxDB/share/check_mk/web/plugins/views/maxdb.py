#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.plugins.views import (
    inventory_displayhints,)
from cmk.gui.plugins.views.inventory import (
    declare_invtable_view,
    render_inv_dicttable,
)
from cmk.gui.i18n import _

inventory_displayhints.update({
    ".software.applications.SAP-MaxDB:": {
        "title": _("SAP MaxDB")
    },
    ".software.applications.SAP-MaxDB.Globalsapdbprograms:": {
        "title": _("Global Sapdb Programs"),
        "render": render_inv_dicttable,
        "view": "sapmaxdb_of_host_general",
        "keyorder": ["name", "version", "validation", "binary"]
    },
    ".software.applications.SAP-MaxDB.CL_sapdbclients:": {
        "title": _("CL Sapdb clients"),
        "render": render_inv_dicttable,
        "view": "sapmaxdb_of_host_cl_clients",
        "keyorder": ["name", "version", "validation", "binary"]
    },
    ".software.applications.SAP-MaxDB.sapdbdb:": {
        "title": _("Sapdb DB"),
        "render": render_inv_dicttable,
        "view": "sapmaxdb_of_host_sapdbdb",
        "keyorder": ["name", "version", "validation", "binary"]
    },
    ".software.applications.SAP-MaxDB.Globalsapdbprograms:*.name": {
        "title": _("Package Name")
    },
    ".software.applications.SAP-MaxDB.Globalsapdbprograms:*.binary": {
        "title": _("Binary Format")
    },
    ".software.applications.SAP-MaxDB.CL_sapdbclients:*.name": {
        "title": _("Package Name")
    },
    ".software.applications.SAP-MaxDB.CL_sapdbclients:*.binary": {
        "title": _("Binary Format")
    },
    ".software.applications.SAP-MaxDB.sapdbdb:*.name": {
        "title": _("Package Name")
    },
    ".software.applications.SAP-MaxDB.sapdbdb:*.binary": {
        "title": _("Binary Format")
    },
})

declare_invtable_view("sapmaxdbgeneral", ".software.applications.SAP-MaxDB.Globalsapdbprograms:",
                      _("MaxDB Global Programs"), _("MaxDB Global Programs"))
declare_invtable_view("sapmaxdbclclients", ".software.applications.SAP-MaxDB.CL_sapdbclients:",
                      _("MaxDB CL Clients"), _("MaxDB CL Clients"))
declare_invtable_view("sapmaxdbsapdbdb", ".software.applications.SAP-MaxDB.sapdbdb:",
                      _("MaxDB SAPDB DB"), _("MaxDB SAPDB DB"))
