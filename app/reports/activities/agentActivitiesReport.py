from datetime import datetime

from flask import request, jsonify

from app import db
from app.reports.generate_report import generate_agents_report
from app.services.validator import validateInputs


def agentActivitiesReport():
    # Get request data
    request_data = request.get_json()

    # Check for mandatory fields
    required_fields = ["subdomain_id", "start_date", "end_date"]
    validateInputs(request_data, required_fields)

    try:
        # Extract data from the request and convert dates
        subdomain_id = request_data["subdomain_id"]
        start_date = datetime.strptime(request_data["start_date"], '%Y-%m-%d')
        end_date = datetime.strptime(request_data["end_date"], '%Y-%m-%d')
    except ValueError:
        return jsonify({
            "status": False,
            "message": "Invalid date format. Use 'YYYY-MM-DD'."
        }), 422

    # Extract user_ids and groups_ids from the request data
    users_ids = request_data.get('users_ids', [])
    groups_ids = request_data.get('groups_ids', [])

    # Define criteria for database query
    criteria = {
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        },
        "SubdomainId": subdomain_id,
    }
    if users_ids:
        criteria["UserId"] = {"$in": users_ids}

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

    # Generate reports based on the calculated totals
    report_data = generate_reports(total_figures)

    # Return the response
    return report_data


def generate_reports(total_figures):
    # Generate reports using the total figures
    report = generate_agents_report(total_figures)

    # Return the generated report
    return {
        "data": report,
        "message": "Retrieved all reports successfully.",
        "status": True
    }
