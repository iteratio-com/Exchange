from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    Metric,
    Unit,
)

# ------------------------------------------------------------
# Units
# ------------------------------------------------------------

unit_per_second = Unit(DecimalNotation("/s"))
unit_count = Unit(DecimalNotation(""))


# ------------------------------------------------------------
# SQL Execution Metrics
# ------------------------------------------------------------

metric_maxdb_sql_executes_per_sec = Metric(
    name="maxdb_sql_executes_per_sec",
    title=Title("SQL Executions"),
    unit=unit_per_second,
    color=Color.BLUE,
)

metric_maxdb_sql_prepares_per_sec = Metric(
    name="maxdb_sql_prepares_per_sec",
    title=Title("SQL Prepares"),
    unit=unit_per_second,
    color=Color.GREEN,
)

metric_maxdb_sql_fetches_per_sec = Metric(
    name="maxdb_sql_fetches_per_sec",
    title=Title("SQL Fetches"),
    unit=unit_per_second,
    color=Color.CYAN,
)


# ------------------------------------------------------------
# SQL Row Metrics
# ------------------------------------------------------------

metric_maxdb_sql_rows_read_per_sec = Metric(
    name="maxdb_sql_rows_read_per_sec",
    title=Title("SQL Rows Read"),
    unit=unit_per_second,
    color=Color.BLUE,
)

metric_maxdb_sql_rows_qualified_per_sec = Metric(
    name="maxdb_sql_rows_qualified_per_sec",
    title=Title("SQL Rows Qualified"),
    unit=unit_per_second,
    color=Color.GREEN,
)


# ------------------------------------------------------------
# SQL I/O Metrics
# ------------------------------------------------------------

metric_maxdb_sql_physical_reads_per_sec = Metric(
    name="maxdb_sql_physical_reads_per_sec",
    title=Title("SQL Physical Reads"),
    unit=unit_per_second,
    color=Color.RED,
)

metric_maxdb_sql_virtual_reads_per_sec = Metric(
    name="maxdb_sql_virtual_reads_per_sec",
    title=Title("SQL Virtual Reads"),
    unit=unit_per_second,
    color=Color.BLUE,
)


# ------------------------------------------------------------
# SQL Wait Metrics
# ------------------------------------------------------------

metric_maxdb_sql_waits_per_sec = Metric(
    name="maxdb_sql_waits_per_sec",
    title=Title("SQL Wait Events"),
    unit=unit_per_second,
    color=Color.ORANGE,
)


# ------------------------------------------------------------
# SQL Execution Time Metrics
# ------------------------------------------------------------

metric_maxdb_sql_avgexecutetime = Metric(
    name="maxdb_sql_avgexecutetime",
    title=Title("Average SQL Execution Time"),
    unit=unit_count,
    color=Color.BLUE,
)

metric_maxdb_sql_maxexecutetime = Metric(
    name="maxdb_sql_maxexecutetime",
    title=Title("Maximum SQL Execution Time"),
    unit=unit_count,
    color=Color.RED,
)

metric_maxdb_sql_currentexecutecount = Metric(
    name="maxdb_sql_currentexecutecount",
    title=Title("Currently Executing SQL Statements"),
    unit=unit_count,
    color=Color.GREEN,
)


# ============================================================
# Combined Graphs
# ============================================================

# 1. SQL Execution Activity

graph_maxdb_sql_activity = Graph(
    name="maxdb_sql_activity",
    title=Title("MaxDB SQL Activity"),
    simple_lines=[
        "maxdb_sql_executes_per_sec",
        "maxdb_sql_prepares_per_sec",
        "maxdb_sql_fetches_per_sec",
    ],
)


# 2. SQL Row Processing

graph_maxdb_sql_rows = Graph(
    name="maxdb_sql_rows",
    title=Title("MaxDB SQL Row Processing"),
    simple_lines=[
        "maxdb_sql_rows_read_per_sec",
        "maxdb_sql_rows_qualified_per_sec",
    ],
)


# 3. SQL I/O Activity

graph_maxdb_sql_io = Graph(
    name="maxdb_sql_io",
    title=Title("MaxDB SQL I/O Activity"),
    simple_lines=[
        "maxdb_sql_physical_reads_per_sec",
        "maxdb_sql_virtual_reads_per_sec",
    ],
)


# 4. SQL Execution Times

graph_maxdb_sql_execution_times = Graph(
    name="maxdb_sql_execution_times",
    title=Title("MaxDB SQL Execution Times"),
    simple_lines=[
        "maxdb_sql_avgexecutetime",
        "maxdb_sql_maxexecutetime",
    ],
)


# 5. SQL Wait Events

graph_maxdb_sql_waits = Graph(
    name="maxdb_sql_waits",
    title=Title("MaxDB SQL Wait Events"),
    simple_lines=[
        "maxdb_sql_waits_per_sec",
    ],
)


# 6. Currently Executing SQL Statements

graph_maxdb_sql_current = Graph(
    name="maxdb_sql_current",
    title=Title("MaxDB Currently Executing SQL Statements"),
    simple_lines=[
        "maxdb_sql_currentexecutecount",
    ],
)
