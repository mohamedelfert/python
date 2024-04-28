def prepare_chart(data, chart_type, title, subtitle):
    # Initialize empty lists to store labels and values
    labels = []
    values = []

    for item in data:
        # Iterate over each item in the data
        for key, value in item.items():
            # Append the key (label) and value to the respective lists
            labels.append(key)
            values.append(value)

    # Prepare the chart data in the desired format
    chart_data = {
        "type": chart_type,
        "title": title,
        "subtitle": subtitle,
        "datasets": {
            "labels": labels,
            "data": values,
            "backgroundColor": ["red", "green"]
        }
    }

    # Return the prepared chart data
    return chart_data

# def calls(data):
#     # Prepare data for calls chart
#     labels = []
#     values = []
#     for item in data:
#         for key, value in item.items():
#             labels.append(key)
#             values.append(value)
#
#     return {
#         "type": "doughnut",
#         "title": "Calls",
#         "subtitle": "Total Logged Outbound & Inbound Calls",
#         "datasets": {
#             "labels": labels,
#             "data": values,
#             "backgroundColor": ["red", "green"]
#         }
#     }

# def handle_tasks(data):
# request_data = request.get_json()
#
# # Check for mandatory fields: "charts" and "start_date" and "end_date"
# if "start_date" not in request_data or "end_date" not in request_data:
#     return jsonify({
#         "status": False,
#         "message": "Request data must include 'start_date' and 'end_date'."
#     }), 422
#
# # Convert start_date and end_date to datetime objects
# try:
#     start_date = datetime.strptime(request_data["start_date"], '%Y-%m-%d')
#     end_date = datetime.strptime(request_data["end_date"], '%Y-%m-%d')
# except ValueError:
#     return jsonify({
#         "status": False,
#         "message": "Invalid date format. Use 'YYYY-MM-DD'."
#     }), 422
#
# # Initialize totals
# total_completed = 0
# total_not_started = 0
#
# criteria = {
#     "Date": {
#         "$gte": start_date,
#         "$lte": end_date
#     }
# }
#
# if users_ids:
#     criteria["UserId"] = {"$in": users_ids}
#
# records = db.agent_reports.find(criteria)
#
# # Calculate totals from records
# for record in records:
#     # Check if the record has the "Figures" key
#     if "Figures" in record:
#         for figure in record["Figures"]:
#             if figure["name"] == "Completed":
#                 total_completed += figure["value"]
#             elif figure["name"] == "Not_Started":
#                 total_not_started += figure["value"]
#
# return {
#     "data": [
#         {
#             "type": "doughnut",
#             "title": "Tasks",
#             "subtitle": "Total Tasks/Follow-ups",
#             "datasets": {
#                 "labels": ["completed", "Not_Started"],
#                 "values": [total_completed, total_not_started]
#             }
#         }
#     ]
# }
