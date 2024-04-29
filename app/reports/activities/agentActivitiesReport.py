from flask import request

from app import db
from app.reports.generate_report import generate_agents_report
from app.services.validator import validateRequestInputs


def agentActivitiesReport():
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

    subdomain_id = request_data["subdomain_id"]
    users_ids = request_data.get('users_ids', [])
    groups_ids = request_data.get('groups_ids', [])

    # if no users_ids sent get all users based on subdomain_id
    if not users_ids:
        users_ids = db.agent_reports.distinct("UserId", {"SubdomainId": subdomain_id})

    # Initialize a dictionary to hold all report data for each user_id
    reports = {}

    # Iterate over each user_id
    for user_id in users_ids:
        # Define criteria for database query
        criteria = {
            "Date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "SubdomainId": subdomain_id,
            "UserId": user_id
        }

        # If groups_ids are provided, include them in criteria
        if groups_ids:
            criteria["GroupId"] = {"$in": groups_ids}

        # Execute database query to retrieve records
        records = db.agent_reports.find(criteria)

        # Initialize a dictionary to hold all totals
        total_figures = {}

        # Calculate totals from records dynamically
        for record in records:
            # Check if the record has the "Figures" key
            if "Figures" in record:
                for figure in record["Figures"]:
                    figure_name = figure["name"]
                    figure_value = figure["value"]
                    # If the figure name is already in the dictionary, add to its value
                    if figure_name in total_figures:
                        total_figures[figure_name] += figure_value
                    else:
                        # Otherwise, initialize it in the dictionary
                        total_figures[figure_name] = figure_value

        # Generate report for this user_id based on the calculated totals
        report_data = generate_reports(total_figures)

        # Add report data to the reports dictionary with user_id as key
        reports[user_id] = report_data["data"]

    # Return all generated reports for each user_id
    return {
        "data": reports,
        "message": "Retrieved all reports successfully.",
        "status": True
    }


def generate_reports(total_figures):
    # Generate reports using the total figures
    report = generate_agents_report(total_figures)

    # Return the generated report
    return {
        "data": report,
        "message": "Retrieved all reports successfully.",
        "status": True
    }
