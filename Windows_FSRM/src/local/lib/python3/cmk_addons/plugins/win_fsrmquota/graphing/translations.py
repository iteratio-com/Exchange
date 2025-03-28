#!/usr/bin/env python3


from cmk.graphing.v1 import translations


translation_win_fsrmquota = translations.Translation(
    name="win_fsrmquota",
    check_commands=[
        translations.PassiveCheck("win_fsrmquota"),
    ],
    translations={
        "fs_free": translations.ScaleBy(1048576),
        "fs_size": translations.ScaleBy(1048576),
        "fs_used": translations.ScaleBy(1048576),
        "growth": translations.RenameToAndScaleBy(
            "fs_growth",
            12.136296296296296,
        ),
        "overprovisioned": translations.ScaleBy(1048576),
        "reserved": translations.ScaleBy(1048576),
        "trend": translations.RenameToAndScaleBy(
            "fs_trend",
            12.136296296296296,
        ),
        "trend_hoursleft": translations.ScaleBy(3600),
        "uncommitted": translations.ScaleBy(1048576),
        "~(?!inodes_used|fs_size|growth|trend|reserved|fs_free|fs_provisioning|uncommitted|overprovisioned|dedup_rate|file_count|fs_used_percent).*$": translations.RenameToAndScaleBy(
            "fs_used",
            1048576,
        ),
    },
)
