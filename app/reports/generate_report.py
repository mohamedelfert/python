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
    report = []
    for label, value in zip(labels, values):
        report.append(
            {
                "label": label,
                "value": value
            }
        )
    return report


def generate_meetings_report(users_ids, agents, total_figures, total):
    # Prepare the datasets for the doughnut chart "By Agents"
    datasets_agents = {
        "backgroundColor": ["red", "green"],
        "data": [
            sum(users_ids[agent_id][label] for label in ["outside", "inhouse", "online"]) for agent_id in agents
        ],
        "labels": agents
    }

    # Prepare the datasets for the doughnut chart "By Types"
    datasets_type = {
        "backgroundColor": ["red", "green"],
        "data": [total_figures[label] for label in ["outside", "inhouse", "online"]],
        "labels": ["outside", "inhouse", "online"]
    }

    # Return the response with the generated datasets
    return {
        "data": [
            {
                "datasets": datasets_agents,
                "subtitle": "By Agents",
                "title": "Meetings",
                "type": "doughnut"
            },
            {
                "datasets": datasets_type,
                "subtitle": "Meetings",
                "title": "By Type",
                "type": "doughnut"
            },
            {"Total": total}
        ]
    }
