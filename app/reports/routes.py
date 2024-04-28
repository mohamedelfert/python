from datetime import datetime

from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.reports import bp
from app.reports.activities.agents import report
from app.reports.activities.overall import overall

# store data
@bp.route('/store-update', methods=["POST"])
@jwt_required()
def store_update():
    request_data = request.get_json()

    # Check if the request data is a list
    if not isinstance(request_data, list):
        return jsonify({
            "status": False,
            "message": "Request data must be a list of dictionaries."
        }), 422

    # Initialize counters for successful and failed records
    successful_count = 0
    failed_count = 0

    # Process each data point in the list
    for data_point in request_data:
        try:
            # Check mandatory fields for each data point
            mandatory_fields = ["SubdomainId", "Date", "UserId", "GroupId"]
            for mandatory_field in mandatory_fields:
                if mandatory_field not in data_point:
                    failed_count += 1
                    continue

            # Prepare the query data
            data = {key: value for key, value in data_point.items() if key in mandatory_fields and value}

            # Process the Date field
            data["Date"] = datetime.strptime(data["Date"], '%Y-%m-%d')

            # Check if the record exists
            record = db.agent_reports.find_one(data)

            if record:
                # If record exists, process Figures
                if "Figures" in data_point:
                    for figure in data_point["Figures"]:
                        name = figure["name"]
                        value = figure["value"]

                        # Update existing Figures or add new ones
                        updated = False
                        for index, record_figure in enumerate(record["Figures"]):
                            if record_figure["name"] == name:
                                record["Figures"][index]["value"] = value
                                updated = True
                                break

                        # Add new Figure if it doesn't exist
                        if not updated:
                            record["Figures"].append(figure)

                # Update the record in the database
                db.agent_reports.update_one(data, {"$set": {"Figures": record["Figures"]}})
                successful_count += 1
            else:
                # Insert a new record if it doesn't exist
                data["Figures"] = data_point["Figures"]
                db.agent_reports.insert_one(data)
                successful_count += 1

        except Exception as e:
            # Handle any exceptions during processing
            failed_count += 1
            print(f"Error processing data point: {e}")

    # Return the final response
    return jsonify({
        "status": True,
        "message": f"Processed {successful_count} data points successfully, {failed_count} data points failed."
    }), 200


# overall activities
@bp.route('/overall-activities', methods=["POST"])
@jwt_required()
def overall_activities():
    return jsonify(overall())


# agents report
@bp.route('/agents-report', methods=["POST"])
@jwt_required()
def agents_report():
    return jsonify(report())

# @bp.route('/report', methods=["POST"])
# @jwt_required()
# def report():
#     request_data = request.get_json()
#
#     # Validate required fields
#     required_fields = ["subdomain_id", "start_date", "end_date"]
#     if not all(field in request_data for field in required_fields):
#         return jsonify({
#             "status": False,
#             "message": "Missing required fields: 'subdomain_id', 'start_date' and 'end_date'"
#         }), 422
#
#     # Convert dates and handle formatting errors
#     try:
#         start_date = datetime.strptime(request_data["start_date"], '%Y-%m-%d')
#         end_date = datetime.strptime(request_data["end_date"], '%Y-%m-%d')
#     except ValueError:
#         return jsonify({
#             "status": False,
#             "message": "Invalid date format. Use 'YYYY-MM-DD'."
#         }), 422
#
#     users_ids = request_data.get('users_ids', [])
#
#     # Define the figures to calculate
#     figures = [
#         "Outbound", "Inbound", "Outside", "Inhouse", "Online",
#         "Email", "Whatsapp", "SMS", "Skype", "Viber", "FB_Messages",
#         "Completed", "Not_Started", "Task", "Events", "Note", "Scheduled_Meetings"
#     ]
#     totals = {figure: 0 for figure in figures}
#
#     # Build the MongoDB query criteria
#     criteria = {
#         "Date":
#             {
#                 "$gte": start_date,
#                 "$lte": end_date
#             },
#         "SubdomainId": request_data.get("subdomain_id")
#     }
#
#     if users_ids:
#         criteria["UserId"] = {"$in": users_ids}
#
#     # Query the database
#     try:
#         records = db.agent_reports.find(criteria)
#     except ValueError:
#         return jsonify({
#             "status": False,
#             "message": "Failed to fetch data from database"
#         }), 500
#
#     # Process records and calculate totals
#     for record in records:
#         for figure in record.get("Figures", []):
#             name = figure["name"].replace(" ", "_")
#             if name in totals:
#                 totals[name] += figure["value"]
#
#     # Build response data dynamically
#     response_data = []
#     response_data.append(
#         create_response_item(
#             ["Outbound", "Inbound"],
#             "calls",
#             "Total Logged Outbound & Inbound Calls",
#             totals
#         )
#     )
#     response_data.append(
#         create_response_item(
#             ["Outside", "Inhouse", "Online"],
#             "Meetings",
#             "Total Logged Meetings",
#             totals
#         )
#     )
#     response_data.append(
#         create_response_item(
#             ["Email", "Whatsapp", "SMS", "Skype", "Viber", "FB_Messages"],
#             "Messages",
#             "Total Logged Messages",
#             totals
#         )
#     )
#     response_data.append(
#         create_response_item(
#             ["Completed"],
#             "Tasks",
#             "Total Tasks/Follow-ups",
#             totals
#         )
#     )
#     response_data.append(
#         create_response_item(
#             ["Not_Started"],
#             "Scheduled Meetings",
#             "By Status",
#             totals
#         )
#     )
#     response_data.append(
#         create_response_item(
#             ["Tasks", "Events", "Note"],
#             "Created TENs",
#             "Total Created Tasks, Events, Notes",
#             totals
#         )
#     )
#
#     return jsonify({
#         "status": True,
#         "message": "Retrieved successfully",
#         "data": response_data
#     }), 200
#
#
# def create_response_item(figure_names, title, subtitle, totals):
#     return {
#         "title": title,
#         "subtitle": subtitle,
#         "datasets": {
#             "labels": figure_names,
#             "data": [totals.get(figure, 0) for figure in figure_names]
#         }
#     }
