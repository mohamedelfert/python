from flask import jsonify


def validateInputs(request_data, required_fields):
    if any(field not in request_data for field in required_fields):
        return jsonify({
            "status": False,
            "message": f"Request data must include {', '.join(required_fields)}."
        }), 422
