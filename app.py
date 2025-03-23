
from dotenv.parser import Reader
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from models import db, User, Inventory, Recipe, Ingredient, InventoryIngredient, RecipeIngredient, ShoppingList, \
    ShoppingListItem
from auth import Login, Register, RefreshToken
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from flask_cors import CORS  # Ajoute l'importation
from datetime import datetime

#from security import authenticate, identity

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.config["JWT_SECRET_KEY"] = "48737ebc2a1ad5952afecba257a5fca48577545238770085bfdey"

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 604800   # 7 jours

app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 jours

jwt = JWTManager(app)



db.init_app(app)

with app.app_context():
    db.create_all()

api = Api(app)


@app.route('/logout', methods=['POST'])
@jwt_required(refresh=True)  # Nécessite un refresh token valide
def logout():
    jti = get_jwt()['jti']  # Récupérer l'identifiant du token (JTI)
    # Ajouter le JTI à une liste noire (par exemple, dans une base de données Redis)
    # Cela empêchera le refresh token d'être réutilisé
    return {"message": "Déconnexion réussie"}, 200

class IngredientViews(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        print(data)
        if data:
            print('data is not empty')
            new_ingredient = Ingredient(nom=data['nom'], unite_mesure=data['unite_mesure'],
                                        prix_unitaire=data['prix_unitaire'],
)
            #recettes=data['recettes'], inventaires=data['inventaires']) iquantite_dsponible=data['quantite_disponible']
            print(new_ingredient)
            db.session.add(new_ingredient)
            db.session.commit()
            return jsonify({'message': 'Ingredient created successfully'})

        else:
            return jsonify({'message': 'Invalid data'}, 400)
    def get(self, id=''):
        if id:
            ingredient = Ingredient.query.get(id)
            if ingredient:
                return jsonify(ingredient.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            ingredients = Ingredient.query.all()
            return jsonify([ingredient.to_dict() for ingredient in ingredients])

    def delete(self, id):
        if id:
            ingredient = Ingredient.query.get(id)
            print(ingredient)
            if ingredient:
                db.session.delete(ingredient)
                db.session.commit()
                return jsonify({'message': 'Ingredient deleted'}, 200)
            else:
                return jsonify({'message': 'Ingredient not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)
        
    def put(self, id):
        data = request.get_json()
        if id:
            ingredient = Ingredient.query.get(id)
            ingredient.nom = data.get("nom", ingredient.nom)
            ingredient.unite_mesure = data.get("unite_mesure", ingredient.unite_mesure)          
            ingredient.prix_unitaire = data.get("prix_unitaire", ingredient.prix_unitaire)
            db.session.commit()
            return jsonify({"message": f"l' ingredient {ingredient.nom } a bien été mise ajour "}, 200)         
        else:
            return jsonify({"message": 'la mise a jour requièt un id valid'})




api.add_resource(IngredientViews, '/ingredients/', '/ingredients/<int:id>/')


class UserView(Resource):
    def get(self, id=''):
        if id:
            user = User.query.get(id)
            if user:
                return jsonify(user.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            users = User.query.all()
            return jsonify([user.to_dict() for user in users])

    def post(self):
        data = request.get_json()

        nom = data['nom']
        email = data['email']
        mot_de_passe = data['mot_de_passe']
        date_creation = data['date_creation']
        #recettes = data['recettes']
        #inventaires = data['inventaires']

        new_user = User(nom=nom, email=email, date_creation=date_creation)
        new_user.set_password(mot_de_passe=mot_de_passe)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict())

    def delete(self, id):
        if id:
            user = User.query.get(id)
            print(user)
            if user:
                db.session.delete(user)
                db.session.commit()
                return jsonify({'message': f'user "{user.nom}" deleted'}, 200)
            else:
                return jsonify({'message': 'user not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)


api.add_resource(UserView, '/user/', '/user/<int:id>/')


class InventoryViews(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        if data:
            print('data is not empty')
            new_inventory = Inventory(nom=data['nom'], utilisateur_id=data['utilisateur_id'])
            #                               """ingredients=data['ingredients'])
            print(new_inventory)
            db.session.add(new_inventory)
            db.session.commit()
            return jsonify({'message': 'Inventory created successfully'})

        else:
            return jsonify({'message': 'Invalid data'}, 400)

    def get(self, id=''):
        print(id)
        if id:
            inventory = Inventory.query.get(id)
            if inventory:
                return jsonify(inventory.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            inventorys = Inventory.query.all()
            return jsonify([inventory.to_dict() for inventory in inventorys])

    def delete(self, id):
        if id:
            inventory = Ingredient.query.get(id)
            print(inventory)
            if inventory:
                db.session.delete(inventory)
                db.session.commit()
                return jsonify({'message': 'Inventory deleted'}, 200)
            else:
                return jsonify({'message': 'Inventory not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)

# api.add_resource(InventoryViews, '/inventory/<int:id>/')
api.add_resource(InventoryViews, '/inventory/', '/inventory/<int:id>/')


class RecipeView(Resource):
    @jwt_required()
    def get(self, id=''):
        """
        Récupère une recette spécifique ou toutes les recettes de l'utilisateur connecté.
        """
        user_id = get_jwt_identity()

        if id:
            # Récupérer une recette spécifique
            recipe = Recipe.query.filter_by(id=id, utilisateur_id=user_id).first()
            if recipe:
                return jsonify(recipe.to_dict())
            else:
                return {'message': 'Recette non trouvée ou non autorisée'}, 404
        else:
            # Récupérer toutes les recettes de l'utilisateur
            recipes = Recipe.query.filter_by(utilisateur_id=user_id).all()
            return jsonify([recipe.to_dict() for recipe in recipes])

    @jwt_required()
    def post(self):
        """
        Crée une nouvelle recette avec les ingrédients associés.
        """
        data = request.get_json()
        user_id = get_jwt_identity()
        print(user_id)

        # Validation des données
        required_fields = ['titre', 'description', 'temps_preparation', 'temps_cuisson', 'est_publique']
        if not all(field in data for field in required_fields):
            return {'message': 'Données manquantes'}, 400

        try:
            # Créer la recette
            new_recipe = Recipe(
                titre=data['titre'],
                description=data['description'],
                temps_preparation=data['temps_preparation'],
                temps_cuisson=data['temps_cuisson'],
                est_publique=data['est_publique'],
                utilisateur_id=user_id
            )
            print(new_recipe)
            
            db.session.add(new_recipe)
            db.session.flush()  # Génère l'ID de la recette avant de créer les ingrédients

            # Ajouter les ingrédients associés
            ingredients = data.get('ingredients', [])
            print(ingredients)
            for ing in ingredients:
                # Vérifier si l'ingrédient existe déjà
                ingredient = Ingredient.query.filter_by(nom=ing['nom']).first()
                if not ingredient:
                    # Créer un nouvel ingrédient s'il n'existe pas
                    ingredient = Ingredient(
                        nom=ing['nom'],
                        unite_mesure=ing['unite_mesure'],
                        prix_unitaire=ing.get('prix_unitaire', 0.0),  # Valeur par défaut pour le prix
                        #utilisateur_id=user_id
                    )
                    db.session.add(ingredient)
                    db.session.flush()

                # Associer l'ingrédient à la recette
                recipe_ingredient = RecipeIngredient(
                    recette_id=new_recipe.id,
                    ingredient_id=ingredient.id,
                    quantite=ing['quantite']
                )
                db.session.add(recipe_ingredient)

            # Valider la transaction
            db.session.commit()
            return 201

        except Exception as e:
            db.session.rollback()  # Annuler la transaction en cas d'erreur
            return {'message': f'Erreur lors de la création de la recette : {str(e)}'}, 500

    @jwt_required()
    def put(self, id):
        """
        Met à jour une recette existante et ses ingrédients associés.
        """
        user_id = get_jwt_identity()
        data = request.get_json()

        if not id:
            return {'message': 'ID de recette manquant'}, 400

        # Récupérer la recette à mettre à jour
        recipe = Recipe.query.filter_by(id=id, utilisateur_id=user_id).first()
        if not recipe:
            return {'message': 'Recette non trouvée ou non autorisée'}, 404

        try:
            # Mettre à jour les informations de base de la recette
            recipe.titre = data.get('titre', recipe.titre)
            recipe.description = data.get('description', recipe.description)
            recipe.temps_preparation = data.get('temps_preparation', recipe.temps_preparation)
            recipe.temps_cuisson = data.get('temps_cuisson', recipe.temps_cuisson)
            recipe.est_publique = data.get('est_publique', recipe.est_publique)
            print(type(data.get('ingredients')))
           
                # Ajouter les nouveaux ingrédients
            for ing in data['ingredients']:
                print(ing.to_dict())
                ingredient = Ingredient.query.filter_by(nom=ing['nom']).first()
                if not ingredient:
                    # Créer un nouvel ingrédient s'il n'existe pas
                    ingredient = Ingredient(
                        nom=ing['nom'],
                        unite_mesure=ing['unite_mesure'],
                        prix_unitaire=ing.get('prix_unitaire', 0.0),
                        utilisateur_id=user_id
                    )
                    db.session.add(ingredient)
                    db.session.flush()

                # Associer l'ingrédient à la recette
                recipe_ingredient = RecipeIngredient(
                    recette_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantite=ing['quantite']
                )
                db.session.add(recipe_ingredient)

            # Valider la transaction
            db.session.commit()
            return 200

        except Exception as e:
            db.session.rollback()  # Annuler la transaction en cas d'erreur
            return {'message': f'Erreur lors de la mise à jour de la recette : {str(e)}'}, 500

    @jwt_required()
    def delete(self, id):
        """
        Supprime une recette spécifique.
        """
        user_id = get_jwt_identity()

        if not id:
            return {'message': 'ID de recette manquant'}, 400

        recipe = Recipe.query.filter_by(id=id, utilisateur_id=user_id).first()
        if not recipe:
            return {'message': 'Recette non trouvée ou non autorisée'}, 404

        try:
            # Supprimer la recette et ses associations
            db.session.delete(recipe)
            db.session.commit()
            return {'message': f'Recette "{recipe.titre}" supprimée avec succès'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erreur lors de la suppression de la recette : {str(e)}'}, 500
    @app.route('/recipe/public/', methods=['GET'])
    def get_public_recipes():
        # Récupérer toutes les recettes publiques
        public_recipes = Recipe.query.filter_by(est_publique=True).all()
        return jsonify([recipe.to_dict() for recipe in public_recipes]), 200

# Ajouter la ressource à l'API
api.add_resource(RecipeView, '/recipe/', '/recipe/<int:id>/')


class InventoryIngredientViews(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        if data:
            print('data is not empty')
            new_ingredient = InventoryIngredient(quantite_disponible=data['quantite_disponible'],inventaire_id=data['inventaire_id'],ingredient_id=data['ingredient_id'])
            #recettes=data['recettes'], inventaires=data['inventaires'])
            print(new_ingredient)
            db.session.add(new_ingredient)
            db.session.commit()
            return jsonify({'message': 'InventoryIngredient created successfully'})

        else:
            return jsonify({'message': 'Invalid data'}, 400)

    def get(self, id=''):
        if id:
            ingredient = InventoryIngredient.query.get(id)
            if ingredient:
                return jsonify(ingredient.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            ingredients = InventoryIngredient.query.all()
            return jsonify([ingredient.to_dict() for ingredient in ingredients])

    def delete(self, id):
        if id:
            ingredient = InventoryIngredient.query.get(id)
            print(ingredient)
            if ingredient:
                db.session.delete(ingredient)
                db.session.commit()
                return jsonify({'message': 'InventoryIngredient deleted'}, 200)
            else:
                return jsonify({'message': 'InventoryIngredient not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)


api.add_resource(InventoryIngredientViews, '/inventoryingredient/', '/inventoryingredient/<int:id>/')


class RecipeIngredientViews(Resource):

    def get(self, id=''):
        if id:
            recipe = RecipeIngredient.query.get(id)
            if recipe:
                return jsonify(recipe.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            recipes = RecipeIngredient.query.all()
            return jsonify([recipe.to_dict() for recipe in recipes])

    def post(self):
        data = request.get_json()
        recette_id = data['recette_id']
        ingredient_id = data['ingredient_id']
        quantite = data['quantite']
        print(data)
        if RecipeIngredient.query.filter_by(recette_id=recette_id, ingredient_id=ingredient_id).first():
            return jsonify({"message": "ingredient exist deja dans la recette"})
        new_recipe = RecipeIngredient(recette_id=recette_id, quantite=quantite,
                                      ingredient_id=ingredient_id)
        print(new_recipe)
        db.session.add(new_recipe)
        db.session.commit()
        recipe = RecipeIngredient.query.get(new_recipe.id)
        recipe.update_ingredient_quantity()
        print(recipe.to_dict())
        return jsonify(new_recipe.to_dict())

    def delete(self, id):
        if id:
            recipe = RecipeIngredient.query.get(id)
            print(recipe)
            if recipe:
                db.session.delete(recipe)
                db.session.commit()
                return jsonify({'message': f'RecipeIngredient  deleted'}, 200)
            else:
                return jsonify({'message': 'RecipeIngredient not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)

    def patch(self):
        pass


api.add_resource(RecipeIngredientViews, '/recipeingredient/', '/recipeingredient/<int:id>/')


class ShoppingListViews(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        if data:
            print('data is not empty')
            new_shoppingList = ShoppingList(date_creation=data['date_creation'], utilisateur_id=data['utilisateur_id'])
            #                               """ingredients=data['ingredients'])
            print(new_shoppingList)
            db.session.add(new_shoppingList)
            db.session.commit()
            return jsonify({'message': 'ShoppingList created successfully'})

        else:
            return jsonify({'message': 'Invalid data'}, 400)

    def get(self, id=''):
        if id:
            shoppingList = ShoppingList.query.get(id)
            if shoppingList:
                return jsonify(shoppingList.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            shoppingLists = ShoppingList.query.all()
            return jsonify([shoppingList.to_dict() for shoppingList in shoppingLists])

    def delete(self, id):
        if id:
            shoppingList = ShoppingList.query.get(id)
            print(shoppingList)
            if shoppingList:
                db.session.delete(shoppingList)
                db.session.commit()
                return jsonify({'message': 'ShoppingList deleted'}, 200)
            else:
                return jsonify({'message': 'ShoppingList not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)


api.add_resource(ShoppingListViews, '/shoppingList/', '/shoppingList/<int:id>/')


class ShoppingListItemViews(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        if data:
            print('data is not empty')
            new_shoppingItem = ShoppingListItem(date_creation=data['date_creation'], quantite=data['quantite'],
                                                utilisateur_id=data['utilisateur_id'], ingredient_id=data['ingredient_id'])
            #                               """ingredients=data['ingredients'])
            print(new_shoppingItem)
            db.session.add(new_shoppingItem)
            ingredient = InventoryIngredient.query.get(id=data['ingredient_id'])
            ingredient.update_ingredient_quantity(data['quantite'])
            db.session.commit()
            return jsonify({'message': 'ShoppingListItem created successfully'})

        else:
            return jsonify({'message': 'Invalid data'}, 400)

    def get(self, id=''):
        if id:
            shoppingItem = ShoppingListItem.query.get(id)
            if shoppingItem:
                return jsonify(shoppingItem.to_dict())
            else:
                return jsonify({'message': 'Invalid id'}, 400)
        else:
            shoppingItems = ShoppingListItem.query.all()
            return jsonify([shoppingItem.to_dict() for shoppingItem in shoppingItems])

    def delete(self, id):
        if id:
            shoppingItem = ShoppingListItem.query.get(id)
            print(shoppingItem)
            if shoppingItem:
                db.session.delete(shoppingItem)
                db.session.commit()
                return jsonify({'message': 'ShoppingListItem deleted'}, 200)
            else:
                return jsonify({'message': 'ShoppingListItem not found'}, 404)
        else:
            return jsonify({'message': 'Invalid id'}, 400)


api.add_resource(ShoppingListItemViews, '/shoppingItem/', '/shoppingItem/<int:id>/')




from sqlalchemy.orm import joinedload

class RecipeDetail(Resource):
    @jwt_required()
    def get(self, recette_id):
        #utilisateur_id = get_jwt_identity()

        # Récupérer la recette avec les ingrédients et leurs détails
        recipe = Recipe.query.options(joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)) \
            .filter_by(id=recette_id) \
            .first()

        if not recipe:
            return jsonify({'message': 'Recette non trouvée'}), 404

        # Formater les données de la recette
        recipe_data = {
            'id': recipe.id,
            'titre': recipe.titre,
            'description': recipe.description,
            'temps_preparation': recipe.temps_preparation,
            'temps_cuisson': recipe.temps_cuisson,
            'ingredients': [{
                'nom': ri.ingredient.nom,  # Accéder au nom de l'ingrédient via la relation
                'quantite': ri.quantite,
                #'unite_mesure': ri.unite_mesure
            } for ri in recipe.ingredients]
        }

        return jsonify(recipe_data)

# Mettre à jour l'URL pour correspondre au frontend
api.add_resource(RecipeDetail, '/recipe-detail/<int:recette_id>/')

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from models import Recipe, RecipeIngredient, InventoryIngredient, ShoppingList, ShoppingListItem, db, Ingredient

class GenerateShoppingList(Resource):
    @jwt_required()  # Sécuriser la route avec JWT
    def post(self):
        user_id = get_jwt_identity()  # Récupérer l'utilisateur connecté
        data = request.get_json()
        recette_id = data.get("recette_id")
        inventaire_id = data.get("inventaire_id")

        # Vérifier que la recette existe
        recette = Recipe.query.get(recette_id)
        if not recette:
            return {"error": "Recette introuvable"}, 404

        # Récupérer les ingrédients de la recette avec leurs noms
        ingredients_recette = (
            db.session.query(RecipeIngredient, Ingredient.nom, Ingredient.unite_mesure)
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .filter(RecipeIngredient.recette_id == recette_id)
            .all()
        )

        # Récupérer les ingrédients disponibles dans l'inventaire
        inventaire_ingredients = {
            i.ingredient_id: i.quantite_disponible
            for i in InventoryIngredient.query.filter_by(inventaire_id=inventaire_id).all()
        }

        ingredients_manquants = []

        for ingredient_recette, nom_ingredient, unite_mesure in ingredients_recette:
            ingredient_id = ingredient_recette.ingredient_id
            quantite_requise = ingredient_recette.quantite
            quantite_disponible = inventaire_ingredients.get(ingredient_id, 0)

            # Vérifier si la quantité disponible est insuffisante
            if quantite_disponible < quantite_requise:
                quantite_a_acheter = quantite_requise - quantite_disponible
                ingredients_manquants.append({
                    "ingredient_id": ingredient_id,
                    "nom": nom_ingredient,  # Ajouter le nom de l'ingrédient
                    "quantite_a_acheter": quantite_a_acheter,
                    "unite_mesure": unite_mesure  # Ajouter l'unité de mesure
                })

        # Sauvegarder la liste de courses
        if ingredients_manquants:
            new_shopping_list = ShoppingList(utilisateur_id=user_id)
            db.session.add(new_shopping_list)
            db.session.commit()

            for item in ingredients_manquants:
                new_shopping_item = ShoppingListItem(
                    liste_id=new_shopping_list.id,
                    ingredient_id=item["ingredient_id"],
                    quantite=item["quantite_a_acheter"]
                )
                db.session.add(new_shopping_item)

            db.session.commit()

            return {
                "message": "Liste de courses générée",
                "ingredients_manquants": ingredients_manquants
            }, 201

        return {"message": "Tous les ingrédients sont disponibles, aucune liste de courses générée"}, 200
# Ajouter la route dans l'API



class GetShoppingListDetails(Resource):
    @jwt_required()
    def get(self, list_id):
        user_id = get_jwt_identity()  # Récupérer l'utilisateur connecté

        # Vérifier que la liste de courses appartient à l'utilisateur
        shopping_list = ShoppingList.query.filter_by(id=list_id, utilisateur_id=user_id).first()
        if not shopping_list:
            return {"error": "Liste de courses introuvable"}, 404

        # Récupérer les détails de la liste de courses
        items = (
            db.session.query(ShoppingListItem, Ingredient.nom, Ingredient.unite_mesure)
            .join(Ingredient, ShoppingListItem.ingredient_id == Ingredient.id)
            .filter(ShoppingListItem.liste_id == list_id)
            .all()
        )

        # Formater la réponse
        shopping_list_details = [
            {
                "ingredient_id": item.ShoppingListItem.ingredient_id,
                "nom": item.nom,  # Nom de l'ingrédient
                "quantite": item.ShoppingListItem.quantite,
                "unite_mesure": item.unite_mesure  # Unité de mesure
            }
            for item in items
        ]

        return {
            "id": shopping_list.id,
            "date_creation": shopping_list.date_creation.isoformat(),
            "items": shopping_list_details
        }, 200

# Ajouter la route dans l'API
api.add_resource(GetShoppingListDetails, '/shopping-list/details/<int:list_id>')

api.add_resource(GenerateShoppingList, '/list-course/')
class GetAllShoppingLists(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()  # Récupérer l'utilisateur connecté

        # Récupérer toutes les listes de courses de l'utilisateur
        shopping_lists = ShoppingList.query.filter_by(utilisateur_id=user_id).all()

        # Formater la réponse
        shopping_lists_data = [
            {
                "id": sl.id,
                "date_creation": sl.date_creation.isoformat(),  # Formater la date
                "nombre_ingredients": len(sl.items)  # Nombre d'ingrédients dans la liste
            }
            for sl in shopping_lists
        ]

        return {"shopping_lists": shopping_lists_data}, 200

# Ajouter la route dans l'API
api.add_resource(GetAllShoppingLists, '/shopping-list/all')


# Gestion des erreurs JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Le token a expiré", "error": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Token invalide", "error": "invalid_token"}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"message": "Accès non autorisé", "error": "unauthorized"}), 401

# Exemple de route protégée
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify(message="Accès autorisé"), 200

if __name__ == '__main__':
    app.run(debug=True)

api.add_resource(Register, "/register/")
api.add_resource(Login, "/login/")
api.add_resource(RefreshToken, "/refresh-token/")



@app.route('/')
def home():
    return 'salut les zeros'


if __name__ == '__main__':
    app.run(port=5000, debug=True)
