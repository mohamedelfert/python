from app.reports.charts.charts import prepare_chart


def generate_chart_report(data, chart):
    # Dictionary to map chart types to chart parameters
    switch = {
        "calls": ("doughnut", "Calls", "Total Logged Outbound & Inbound Calls"),
        "meetings": ("doughnut", "Meetings", "Total Logged Meetings"),
        "messages": ("doughnut", "Messages", "Total Logged Messages"),
        "scheduled_meetings": ("doughnut", "Scheduled Meetings", "By Status"),
        "tasks": ("doughnut", "Tasks", "Total Tasks/Follow-ups"),
        "created_tens": ("doughnut", "Created TENs", "Total Created Tasks, Events, Notes"),
    }

    # Check if the chart type is recognized
    if chart in switch:
        # Get chart parameters from the switch dictionary
        chart_params = switch[chart]
        # Call the prepare_chart function with the provided data and chart parameters
        return prepare_chart(data.get(chart, []), *chart_params)
    else:
        # If chart type is not recognized, return an error message
        return {"error": f"Unknown This Chart: {chart}"}


def generate_agents_report(total_figures):
    # Prepare labels and values for output based on the aggregated data
    labels = list(total_figures.keys())
    values = [total_figures[label] for label in labels]

    # Return data in the required format for generating a report
    return {
        "datasets": {
            "labels": labels,
            "values": values
        }
    }
