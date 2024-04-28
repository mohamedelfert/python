import os

from flask import jsonify, request, make_response
from flask_jwt_extended import create_access_token

from app.auth import bp


@bp.route('/login', methods=['POST'])
def auth():
    data = request.get_json()

    client_id = data['client_id'] if 'client_id' in data else None
    client_secret = data['client_secret'] if 'client_secret' in data else None

    if client_id and client_id == os.environ.get("CLIENT_ID") and client_secret and client_secret == os.environ.get("CLIENT_SECRET"):
        return jsonify({'access_token': create_access_token(identity=client_secret)})

    return make_response({'msg': 'Unauthorized'}, 401)
