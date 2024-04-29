from datetime import datetime

from flask import request, jsonify

from app import db
from app.reports.generate_report import generate_chart_report
from app.services.validator import validateRequestInputs


def overallActivitiesReport():
    # Get request data
    request_data = request.get_json()

    # Check for mandatory fields
    required_fields = ["charts", "subdomain_id", "start_date", "end_date"]
    validation_result = validateRequestInputs(request_data, required_fields)

    # Check if validation failed
    if isinstance(validation_result, tuple):
        start_date, end_date = validation_result
    else:
        return validation_result

    # Extract subdomain_id and user_ids and charts from the request data
    subdomain_id = request_data["subdomain_id"]
    users_ids = request_data.get('users_ids', [])
    charts = request_data.get('charts', [])

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

    # Execute database query
    records = db.agent_reports.find(criteria)

    # Define categories and initialize totals
    categories = {
        "calls": ["outbound", "inbound"],
        "meetings": ["outside", "inhouse", "online"],
        "messages": ["email", "whatsapp", "sms", "skype", "viber", "fb_messages"],
        "tasks": ["completed", "not_started"],
        "scheduled_meetings": ["scheduled_meetings"],
        "created_tens": ["task", "events", "note"]
    }

    totals = {
        category: {
            item: 0 for item in items
        }
        for category, items in categories.items()
    }

    # Process records to calculate totals
    for record in records:
        if "Figures" in record:
            for figure in record["Figures"]:
                for category, items in categories.items():
                    if figure["name"] in items:
                        totals[category][figure["name"]] += figure["value"]

    # Prepare the response data in the desired format
    data = {}
    for category, items in totals.items():
        data[category] = [{key: value} for key, value in items.items()]

    # Generate reports for each chart requested
    report_data = generate_reports(data, charts)

    # Return the response
    return report_data


def generate_reports(data, charts):
    all_reports = []
    # Generate report for each requested chart
    for chart in charts:
        report = generate_chart_report(data, chart)
        if "error" not in report:
            all_reports.append(report)
        else:
            return {"error": f"Unknown Chart : {chart}"}
    # Return all generated reports
    return {
        "data": all_reports,
        "message": "Retrieved all reports successfully.",
        "status": True
    }
