from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from models import User, db
from flask_restful import Resource
from datetime import timedelta



class Register(Resource):
    def post(self):
        data = request.get_json()
        nom = data.get("nom")
        email = data.get("email")
        mot_de_passe = data.get("mot_de_passe")

        if not nom or not email or not mot_de_passe:
            return jsonify({"message": "Tous les champs sont obligatoires"}), 400

        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Cet email est déjà utilisé"})

        # Créer un nouvel utilisateur
        new_user = User(nom=nom, email=email)
        new_user.set_password(mot_de_passe)  # Hash le mot de passe
        print('ok')
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Inscription réussie"})


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        mot_de_passe = data.get("mot_de_passe")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(mot_de_passe):
            return jsonify({"message": "Identifiants incorrects"})

        # Générer un token JWT
        access_token = create_access_token(identity=user.id,expires_delta=timedelta(minutes=10080))
        token_refresh =create_refresh_token(identity=user.id)
        return jsonify({"access_token": access_token, "refresh_token": token_refresh, "id": user.id, "nom": user.nom, "email": user.email})


class RefreshToken(Resource):
    @jwt_required(refresh=True)  # Seul le refresh token est requis
    def refresh_token():
        try:
            # Extraire l'identité de l'utilisateur à partir du refresh token
            user_id = get_jwt_identity()
            
            # Créer un nouveau token d'accès
            new_access_token = create_access_token(identity=user_id)
            
            return {"access_token": new_access_token}, 200
        except ExpiredSignatureError:
            return {"error": "Le refresh token a expiré. Veuillez vous reconnecter."}, 401