from flask import request

from app import db
from app.reports.generate_report import generate_meetings_report
from app.services.validator import validateRequestInputs


def meetingsReport():
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

    # Extract subdomain_id and users_ids and charts from the request data
    subdomain_id = request_data["subdomain_id"]

    # Define criteria for database query
    criteria = {
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        },
        "SubdomainId": subdomain_id,
    }

    # Execute database query
    records = db.agent_reports.find(criteria)

    # Define the specified total_figures
    total_figures = {"outside": 0, "inhouse": 0, "online": 0}
    users_ids = {}

    # Iterate over records to aggregate values for each category and each user ID
    for record in records:
        # get user_id
        user_id = record.get("UserId")
        if user_id not in users_ids:
            users_ids[user_id] = {"outside": 0, "inhouse": 0, "online": 0}
        if "Figures" in record:
            for figure in record["Figures"]:
                label = figure["name"]
                value = figure["value"]
                if label in users_ids[user_id]:
                    users_ids[user_id][label] += value
                if label in total_figures:
                    total_figures[label] += value

    # get list users_ids keys
    agents = list(users_ids.keys())

    # Convert total_figures to the desired format
    total_figures_list = [
        {"label": label, "value": value} for label, value in total_figures.items()
    ]

    # gat total of meetings
    total = sum(figure["value"] for figure in total_figures_list)

    # Generate reports for each chart requested
    report = generate_meetings_report(users_ids, agents, total_figures, total)

    # Return report
    return report
