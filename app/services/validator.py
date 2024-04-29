from datetime import datetime


def validateRequestInputs(request_data, required_fields):
    # Check for missing or null required fields
    missing_fields = [field for field in required_fields if field not in request_data or request_data[field] is None]
    if missing_fields:
        return {
            "status": False,
            "message": f"Request data must include and not be null for: {', '.join(missing_fields)}."
        }

    # Convert dates and handle invalid format
    try:
        start_date = datetime.strptime(request_data["start_date"], '%Y-%m-%d')
        end_date = datetime.strptime(request_data["end_date"], '%Y-%m-%d')
    except ValueError:
        return {
            "status": False,
            "message": "Invalid date format. Use 'YYYY-MM-DD'."
        }

    return start_date, end_date
