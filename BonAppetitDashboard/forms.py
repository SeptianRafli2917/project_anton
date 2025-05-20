from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class RecipeForm(FlaskForm):
    """Form for adding or editing a recipe"""
    title = StringField('Recipe Title', validators=[
        DataRequired(), 
        Length(min=3, max=100, message="Title must be between 3 and 100 characters")
    ])
    
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500, message="Description must be less than 500 characters")
    ])
    
    ingredients = TextAreaField('Ingredients (one per line)', validators=[
        DataRequired(),
        Length(min=5, message="Ingredients are required")
    ])
    
    steps = TextAreaField('Steps (one per line)', validators=[
        DataRequired(),
        Length(min=5, message="Preparation steps are required")
    ])
    
    category = SelectField('Category', coerce=int, validators=[Optional()])
    
    image = FileField('Recipe Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    
    submit = SubmitField('Save Recipe')

class SearchForm(FlaskForm):
    """Form for searching recipes"""
    query = StringField('Search Recipes', validators=[
        DataRequired(),
        Length(min=2, message="Search query must be at least 2 characters")
    ])
    
    search_type = SelectField('Search By', choices=[
        ('title', 'Title'),
        ('ingredients', 'Ingredients')
    ], default='title')
    
    submit = SubmitField('Search')
