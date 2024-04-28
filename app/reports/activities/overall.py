from datetime import datetime

from flask import request, jsonify

from app import db
from app.reports.generate_report import generate_chart_report


def overall():
    # Get request data
    request_data = request.get_json()

    # Check for mandatory fields
    required_fields = ["charts", "subdomain_id", "start_date", "end_date"]
    if any(field not in request_data for field in required_fields):
        return jsonify({
            "status": False,
            "message": f"Request data must include {', '.join(required_fields)}."
        }), 422

    # Convert dates and handle invalid format
    try:
        subdomain_id = request_data["subdomain_id"]
        start_date = datetime.strptime(request_data["start_date"], '%Y-%m-%d')
        end_date = datetime.strptime(request_data["end_date"], '%Y-%m-%d')
    except ValueError:
        return jsonify({
            "status": False,
            "message": "Invalid date format. Use 'YYYY-MM-DD'."
        }), 422

    # Extract user_ids and charts from the request data
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
