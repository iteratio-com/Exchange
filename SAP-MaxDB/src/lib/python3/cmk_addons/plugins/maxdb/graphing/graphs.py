#!/usr/bin/env python3


from cmk.graphing.v1 import Title, graphs, metrics, perfometers

UNIT_TIME = metrics.Unit(metrics.TimeNotation())
UNIT_PERCENTAGE = metrics.Unit(metrics.DecimalNotation("%"))
UNIT_BYTES = metrics.Unit(metrics.IECNotation("B"))
UNIT_COUNT = metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0))

metric_datacache_hitrate = metrics.Metric(
    name="datacache_hitrate",
    title=Title("Datacache Hitrate"),
    unit=UNIT_PERCENTAGE,
    color=metrics.Color.GREEN,
)
metric_session_usage = metrics.Metric(
    name="session_usage",
    title=Title("Session Usage"),
    unit=UNIT_PERCENTAGE,
    color=metrics.Color.GREEN,
)
metric_last_data_job = metrics.Metric(
    name="last_data_job",
    title=Title("Last Data Backup Job"),
    unit=UNIT_TIME,
    color=metrics.Color.BROWN,
)

metric_last_log_job = metrics.Metric(
    name="last_log_job",
    title=Title("Last Log Backup Job"),
    unit=UNIT_TIME,
    color=metrics.Color.PURPLE,
)
metric_database_usage_perc = metrics.Metric(
    name="database_usage_perc",
    title=Title("Database Usage"),
    unit=UNIT_PERCENTAGE,
    color=metrics.Color.GREEN,
)
metric_usable_size_bytes = metrics.Metric(
    name="usable_size_bytes",
    title=Title("Total Size"),
    unit=UNIT_BYTES,
    color=metrics.Color.GREEN,
)
metric_used_size_bytes = metrics.Metric(
    name="used_size_bytes",
    title=Title("Used Size"),
    unit=UNIT_BYTES,
    color=metrics.Color.BLUE,
)
graph_maxdbdatabaseusagebytes = graphs.Graph(
    name="maxdbdatabaseusagebytes",
    title=Title("Database Usage"),
    simple_lines=["used_size_bytes", "usable_size_bytes"],
)

#####

metric_used_log_pages_perc = metrics.Metric(
    name="used_log_pages_perc",
    title=Title("Log Pages Usage"),
    unit=UNIT_PERCENTAGE,
    color=metrics.Color.GREEN,
)
metric_used_log_pages_bytes = metrics.Metric(
    name="used_log_pages_bytes",
    title=Title("Used Log Pages"),
    unit=UNIT_BYTES,
    color=metrics.Color.ORANGE,
)
metric_log_pages_bytes = metrics.Metric(
    name="log_pages_bytes",
    title=Title("Total Aviable LOG Pages"),
    unit=UNIT_BYTES,
    color=metrics.Color.GREEN,
)
metric_used_log_pages = metrics.Metric(
    name="used_log_pages",
    title=Title("Used Log Pages"),
    unit=UNIT_COUNT,
    color=metrics.Color.BLUE,
)
metric_log_pages = metrics.Metric(
    name="log_pages",
    title=Title("Total Aviable Log Pages"),
    unit=UNIT_COUNT,
    color=metrics.Color.GREEN,
)

####
graph_maxdblogbytes = graphs.Graph(
    name="maxdblogbytes",
    title=Title("Log Pages (Size)"),
    simple_lines=["used_log_pages_bytes", "log_pages_bytes"],
)
graph_maxdblogpages = graphs.Graph(
    name="maxdblogpages",
    title=Title("Log Pages (Pages)"),
    simple_lines=["used_log_pages", "log_pages"],
)
### perfometer
perfometer_used_log_pages_perc = perfometers.Perfometer(
    name="used_log_pages_perc",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(100),
    ),
    segments=["used_log_pages_perc"],
)

perfometer_database_usage_perc = perfometers.Perfometer(
    name="database_usage_perc",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(100),
    ),
    segments=["database_usage_perc"],
)
perfometer_database_usage_perc = perfometers.Perfometer(
    name="database_usage_perc",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(100),
    ),
    segments=["database_usage_perc"],
)
perfometer_datacache_hitrate = perfometers.Perfometer(
    name="datacache_hitrate",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(100),
    ),
    segments=["datacache_hitrate"],
)

perfometer_session_usage = perfometers.Perfometer(
    name="session_usage",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(100),
    ),
    segments=["session_usage"],
)

# MaxDB extended monitoring
UNIT_RATE = metrics.Unit(metrics.DecimalNotation("/s"))

metric_maxdb_sql_executes_per_sec = metrics.Metric(name="maxdb_sql_executes_per_sec", title=Title("SQL executions"), unit=UNIT_RATE, color=metrics.Color.BLUE)
metric_maxdb_sql_prepares_per_sec = metrics.Metric(name="maxdb_sql_prepares_per_sec", title=Title("SQL prepares"), unit=UNIT_RATE, color=metrics.Color.GREEN)
metric_maxdb_sql_rows_read_per_sec = metrics.Metric(name="maxdb_sql_rows_read_per_sec", title=Title("SQL rows read"), unit=UNIT_RATE, color=metrics.Color.ORANGE)
metric_maxdb_sql_rows_qualified_per_sec = metrics.Metric(name="maxdb_sql_rows_qualified_per_sec", title=Title("SQL rows qualified"), unit=UNIT_RATE, color=metrics.Color.PURPLE)
metric_maxdb_sql_physical_reads_per_sec = metrics.Metric(name="maxdb_sql_physical_reads_per_sec", title=Title("SQL physical reads"), unit=UNIT_RATE, color=metrics.Color.BROWN)
metric_maxdb_sql_virtual_reads_per_sec = metrics.Metric(name="maxdb_sql_virtual_reads_per_sec", title=Title("SQL virtual reads"), unit=UNIT_RATE, color=metrics.Color.BLUE)
metric_maxdb_sql_waits_per_sec = metrics.Metric(name="maxdb_sql_waits_per_sec", title=Title("SQL waits"), unit=UNIT_RATE, color=metrics.Color.GREEN)
metric_maxdb_sql_fetches_per_sec = metrics.Metric(name="maxdb_sql_fetches_per_sec", title=Title("SQL fetches"), unit=UNIT_RATE, color=metrics.Color.ORANGE)
metric_maxdb_data_used_bytes = metrics.Metric(name="maxdb_data_used_bytes", title=Title("Data used"), unit=UNIT_BYTES, color=metrics.Color.PURPLE)
metric_maxdb_data_total_bytes = metrics.Metric(name="maxdb_data_total_bytes", title=Title("Data total"), unit=UNIT_BYTES, color=metrics.Color.BROWN)
metric_maxdb_transaction_age_seconds = metrics.Metric(name="maxdb_transaction_age_seconds", title=Title("Transaction age"), unit=UNIT_TIME, color=metrics.Color.BLUE)
metric_maxdb_backup_dat_age = metrics.Metric(name="maxdb_backup_dat_age", title=Title("Data backup age"), unit=UNIT_TIME, color=metrics.Color.GREEN)
metric_maxdb_backup_log_age = metrics.Metric(name="maxdb_backup_log_age", title=Title("Log backup age"), unit=UNIT_TIME, color=metrics.Color.ORANGE)
metric_maxdb_backup_dat_duration = metrics.Metric(name="maxdb_backup_dat_duration", title=Title("Data backup duration"), unit=UNIT_TIME, color=metrics.Color.PURPLE)
metric_maxdb_backup_log_duration = metrics.Metric(name="maxdb_backup_log_duration", title=Title("Log backup duration"), unit=UNIT_TIME, color=metrics.Color.BROWN)
metric_maxdb_usedentrycountpercentage = metrics.Metric(name="maxdb_usedentrycountpercentage", title=Title("Lock usage"), unit=UNIT_PERCENTAGE, color=metrics.Color.BLUE)
metric_maxdb_requestorcount = metrics.Metric(name="maxdb_requestorcount", title=Title("Waiting lock requests"), unit=UNIT_COUNT, color=metrics.Color.GREEN)
graph_maxdb_sql_activity = graphs.Graph(name="maxdb_sql_activity", title=Title("SQL activity"), simple_lines=['maxdb_sql_executes_per_sec', 'maxdb_sql_prepares_per_sec', 'maxdb_sql_fetches_per_sec'])
graph_maxdb_sql_reads = graphs.Graph(name="maxdb_sql_reads", title=Title("SQL reads"), simple_lines=['maxdb_sql_physical_reads_per_sec', 'maxdb_sql_virtual_reads_per_sec'])
graph_maxdb_data_capacity = graphs.Graph(name="maxdb_data_capacity", title=Title("MaxDB data capacity"), simple_lines=['maxdb_data_used_bytes', 'maxdb_data_total_bytes'])
graph_maxdb_backup_age = graphs.Graph(name="maxdb_backup_age", title=Title("MaxDB backup age"), simple_lines=['maxdb_backup_dat_age', 'maxdb_backup_log_age'])
perfometer_maxdb_usedentrycountpercentage = perfometers.Perfometer(name="maxdb_usedentrycountpercentage", focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(100)), segments=["maxdb_usedentrycountpercentage"])
perfometer_maxdb_transaction_age_seconds = perfometers.Perfometer(name="maxdb_transaction_age_seconds", focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(3600)), segments=["maxdb_transaction_age_seconds"])
perfometer_maxdb_data_used_bytes = perfometers.Perfometer(name="maxdb_data_used_bytes", focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(100000000000)), segments=["maxdb_data_used_bytes"])

