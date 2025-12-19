#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.views.inventory.registry import inventory_displayhints

inventory_displayhints.update(
    {
        ".software.applications.sapmaxdb:": {"title": _("SAP MaxDB")},
        ".software.applications.sapmaxdb.globalsapdbprograms:": {
            "title": _("Global SAP DB Programs"),
            "keyorder": ["name", "version", "validation", "binary"],
        },
        ".software.applications.sapmaxdb.cl_sapdbclients:": {
            "title": _("CL SAPdb clients"),
            "keyorder": ["name", "version", "validation", "binary"],
        },
        ".software.applications.sapmaxdb.sapdbdb:": {
            "title": _("SAPdb DB"),
            "keyorder": ["name", "version", "validation", "binary"],
        },
        ".software.applications.sapmaxdb.globalsapdbprograms:*.name": {"title": _("Package Name")},
        ".software.applications.sapmaxdb.globalsapdbprograms:*.binary": {
            "title": _("Binary Format")
        },
        ".software.applications.sapmaxdb.cl_sapdbclients:*.name": {"title": _("Package Name")},
        ".software.applications.sapmaxdb.cl_sapdbclients:*.binary": {"title": _("Binary Format")},
        ".software.applications.sapmaxdb.sapdbdb:*.name": {"title": _("Package Name")},
        ".software.applications.sapmaxdb.sapdbdb:*.binary": {"title": _("Binary Format")},
    }
)
