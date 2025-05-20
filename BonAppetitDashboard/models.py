from app import db
from datetime import datetime

class Category(db.Model):
    """Model for recipe categories"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    recipes = db.relationship('Recipe', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

class Recipe(db.Model):
    """Model for recipes"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __repr__(self):
        return f"<Recipe {self.title}>"
    
    def ingredients_list(self):
        """Return the ingredients as a list"""
        return [ingredient.strip() for ingredient in self.ingredients.splitlines() if ingredient.strip()]
    
    def steps_list(self):
        """Return the steps as a list"""
        return [step.strip() for step in self.steps.splitlines() if step.strip()]
