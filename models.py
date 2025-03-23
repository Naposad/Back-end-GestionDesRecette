
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask import jsonify

db = SQLAlchemy()
bcrypt = Bcrypt()

# Modèle Utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    recettes = db.relationship('Recipe', backref='auteur', lazy=True)
    inventaires = db.relationship('Inventory', backref='proprietaire', lazy=True)

    def set_password(self, mot_de_passe):
        self.mot_de_passe = bcrypt.generate_password_hash(mot_de_passe).decode('utf-8')

    def check_password(self, mot_de_passe):
        return bcrypt.check_password_hash(self.mot_de_passe, mot_de_passe)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'password': self.mot_de_passe
        }


# Modèle Recette
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    temps_preparation = db.Column(db.Integer, nullable=False)
    temps_cuisson = db.Column(db.Integer, nullable=False)
    est_publique = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    ingredients = db.relationship('RecipeIngredient', backref='recette', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "temps_preparation": self.temps_preparation,
            "temps_cuisson": self.temps_cuisson,
            "est_publique": self.est_publique,
            "date_creation": self.date_creation.isoformat(),  # Format ISO 8601
            "utilisateur_id": self.utilisateur_id
        }


# Modèle Ingrédient
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    unite_mesure = db.Column(db.String(50), nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    #quantite_disponible = db.Column(db.Integer, default=0)
    #utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    recettes = db.relationship('RecipeIngredient', backref='ingredient', lazy=True)
    inventaires = db.relationship('InventoryIngredient', backref='ingredient', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'unite_mesure': self.unite_mesure,
            'prix_unitaire': self.prix_unitaire,
            #'utilisateur_id': self.utilisateur_id,

            #'quantite_disponible': self.quantite_disponible
        }



# Modèle de liaison entre Recette et Ingrédient
class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recette_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantite = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'recette_id': self.recette_id,
            'ingredient_id': self.ingredient_id,
            'quantite': self.quantite
        }

    def update_ingredient_quantity(self):
        print(self.ingredient_id)
        ingredient = InventoryIngredient.query.get(self.ingredient_id)
        if not ingredient:
            return jsonify({'message:': 'ingredient not found'})

        elif ingredient.quantite_disponible == 0:
            return jsonify({'message:': 'la quantité d ingredient est null '})
        elif ingredient.quantite_disponible < self.quantite:
            return jsonify({'message:' 'la quantité d ingredient est insufficient'})

        ingredient.ingredient_quantity_decrement(self.quantite)
        return jsonify({'message:': 'ingredient updated'})





# Modèle Inventaire
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    ingredients = db.relationship('InventoryIngredient', backref='inventaire', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'utilisateur_id': self.utilisateur_id,
            'ingredients': self.ingredients
        }

# Modèle de liaison entre Inventaire et Ingrédient
class InventoryIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventaire_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantite_disponible = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'inventaire_id': self.inventaire_id,
            'ingredient_id': self.ingredient_id,
            'quantite_disponible': self.quantite_disponible
        }

    def update_ingredient_quantity(self, quantite):
        self.quantite_disponible += quantite
        db.session.commit()
        return jsonify({'message:': 'ingredient updated'})
    def ingredient_quantity_decrement(self, quantite):
        self.quantite_disponible -= quantite
        db.session.commit()
        return jsonify({'message:': 'ingredient updated'})

class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec les éléments de la liste de courses
    items = db.relationship('ShoppingListItem', backref='liste', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'utilisateur_id': self.utilisateur_id,
            'date_creation': self.date_creation.isoformat(),  # Convertir la date en chaîne
            'items': [item.to_dict() for item in self.items]  # Convertir chaque élément en dictionnaire
        }

# Modèle Élément de la Liste de Courses
class ShoppingListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    liste_id = db.Column(db.Integer, db.ForeignKey('shopping_list.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantite = db.Column(db.Float, nullable=False)

    # Relation avec l'ingrédient
    ingredient = db.relationship('Ingredient', backref='shopping_list_items')

    def to_dict(self):
        return {
            'id': self.id,
            'liste_id': self.liste_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_nom': self.ingredient.nom if self.ingredient else None,  # Ajouter le nom de l'ingrédient
            'quantite': self.quantite,
            'unite_mesure': self.ingredient.unite_mesure if self.ingredient else None  # Ajouter l'unité de mesure
        }