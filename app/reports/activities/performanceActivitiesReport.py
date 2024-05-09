from flask import request, jsonify

from app import db
from app.services.validator import validateRequestInputs


def performanceActivitiesReport():
    # Get request data
    request_data = request.get_json()

    # Check for mandatory fields
    required_fields = ["subdomain_id", "user_id", "start_date", "end_date"]
    validation_result = validateRequestInputs(request_data, required_fields)

    # Check if validation failed
    if isinstance(validation_result, tuple):
        start_date, end_date = validation_result
    else:
        return validation_result

    # Extract subdomain_id and user_id and charts from the request data
    subdomain_id = request_data["subdomain_id"]
    user_id = request_data.get('user_id')

    # Define criteria for database query
    criteria = {
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        },
        "SubdomainId": subdomain_id,
        "UserId": user_id,
    }

    # Query the database
    records = db.agent_reports.find(criteria)

    # Process records and calculate totals for each figure
    figures = [
        "assignments_in_range", "score", "active_assignments_in_range",
        "average_daily_views", "total_revenues", "open_amount",
        "closing_this_month", "lost_deals", "open_deals", "total_durations",
        "avg_call_duration", "longest_call", "shortest_call", "calls", "notes"
    ]

    totals = {figure: 0 for figure in figures}

    for record in records:
        for figure in record.get("Figures", []):
            name = figure["name"].replace(" ", "_")
            if name in totals:
                totals[name] += figure["value"]

    # Transform data response as ( label , value )
    transformed_data = [
        {"label": label, "value": value} for label, value in totals.items()
    ]

    return transformed_data
