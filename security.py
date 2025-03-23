"""from werkzeug.security import safe_str_cmp
from models import User
from flask import jsonify, request

def authenticate(email, password):
    user = User.find_by_email(email)
    if user and safe_str_cmp(user.mot_de_passe, password):
        return jsonify(user.to_dict())
    else:
        return jsonify({"message": "Invalid email or password"})

def identity(payload):
    user_id = payload['identity']
    return jsonify(User.find_by_id(user_id).to_dict())


"""