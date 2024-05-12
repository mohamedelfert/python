from flask import request

from app import db
from app.reports.generate_report import generate_meetings_report, generate_chart_report
from app.services.validator import validateRequestInputs


def scheduledMeetingsReport():
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

    # Define categories and initialize totals
    categories = {
        "type": ["none", "sales_meeting", "site_visit", "developer_meeting", "eoi_meeting", "reservation_meeting",
                 "contracting_meeting", "cancellation_meeting"],
        "status": ["not_started", "in_progress", "completed", "waiting", "deferred", "canceled"]
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

    charts = ["type", "status"]

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
