from flask import request, jsonify

from app import db
from app.services.validator import validateRequestInputs


def meetingsByTeamReport():
    # Get request data
    request_data = request.get_json()

    # Check for mandatory fields
    required_fields = ["subdomain_id", "start_date", "end_date"]
    validation_result = validateRequestInputs(request_data, required_fields)

    # Check if validation failed
    if isinstance(validation_result, tuple):
        start_date, end_date = validation_result
    else:
        return validation_result

    # Extract subdomain_id and user_id and charts from the request data
    subdomain_id = request_data["subdomain_id"]
    groups_ids = request_data.get('groups_ids', [])

    # Define criteria for database query
    criteria = {
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        },
        "SubdomainId": subdomain_id,
    }

    if groups_ids:
        criteria["GroupId"] = {"$in": groups_ids}

    # Query the database
    records = db.agent_reports.find(criteria)

    # Process records and calculate totals for each figure for each user
    group_totals = {}

    for record in records:
        group_id = record.get("GroupId")
        if group_id not in group_totals:
            group_totals[group_id] = {figure: 0 for figure in ["activities", "task", "scheduled_meetings"]}

        for figure in record.get("Figures", []):
            name = figure["name"].replace(" ", "_")
            if name in group_totals[group_id]:
                group_totals[group_id][name] += figure["value"]

    # Transform data response for each user
    transformed_data = []
    for group_id, totals in group_totals.items():
        user_data = {"group_id": group_id, "data": [{"label": label, "value": value} for label, value in totals.items()]}
        transformed_data.append(user_data)

    return transformed_data
