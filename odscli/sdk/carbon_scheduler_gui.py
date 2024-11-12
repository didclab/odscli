from rich.columns import Columns
from rich.table import Table
from rich.panel import Panel
from rich.console import Console


def buildMainCarbonTable(data, console:Console):
    terminal_width = console.width

    # Estimate width per subtable (you can adjust this based on actual subtable width)
    subtable_width_estimate = 50  # Approximate width per subtable

    # Calculate the number of columns per row based on terminal width
    columns_per_row = max(1, terminal_width // subtable_width_estimate)

    # Create the main table (one row of subtables)
    main_table = Table(title="Carbon Intensity Report by Job", show_lines=True)

    # Add columns to the main table based on the calculated columns per row
    for i in range(columns_per_row):
        main_table.add_column(f"Subtable {i + 1}", style="white")

    # Populate the main table with subtables in each row
    row = []
    for idx, job in enumerate(data):
        # Build the subtable (TraceRoute table)
        trace_route_table = buildTraceRouteTable(
            job["transferNodeName"],
            job["jobUuid"],
            job["timeMeasuredAt"],
            job["traceRouteCarbon"]
        )

        # Convert the trace_route_table to a Panel
        trace_route_panel = Panel(trace_route_table, border_style="bold blue", title="Carbon Trace Route")

        # Add the rendered panel (subtable) to the row
        row.append(trace_route_panel)

        # Once we've filled the row (columns_per_row), add it to the main table and reset the row for the next batch
        if (idx + 1) % columns_per_row == 0 or (idx + 1) == len(data):
            # Create columns layout from the current row of panels
            columns_layout = Columns(row)
            console.print(columns_layout)
            row = []


def buildTraceRouteTable(transferNodeName, jobUuid, timeMeasuredAt, trace_route_data):
    # Create a nested table for trace route details
    title = f"Transfer Node: {transferNodeName} - Job Uuid: {jobUuid} - Measured At: {timeMeasuredAt}"
    trace_route_table = Table(title=title, show_header=True, header_style="bold blue")
    trace_route_table.add_column("Index", justify="right", style="cyan")
    trace_route_table.add_column("IP", style="cyan")
    trace_route_table.add_column("Carbon Intensity", justify="right", style="green")
    trace_route_table.add_column("Latitude", justify="right")
    trace_route_table.add_column("Longitude", justify="right")

    # Populate nested table with each hop
    for idx, hop in enumerate(trace_route_data, start=1):
        trace_route_table.add_row(
            str(idx),
            hop["ip"],
            str(hop["carbonIntensity"]),
            str(hop["lat"]),
            str(hop["lon"])
        )
    return trace_route_table
