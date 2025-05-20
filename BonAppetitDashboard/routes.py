import os
import uuid
from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from app import app, db
from models import Recipe, Category
from forms import RecipeForm, SearchForm

def save_image(form_image):
    """Save the uploaded image and return the path"""
    if not form_image:
        return None
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Generate unique filename
    filename = secure_filename(form_image.filename)
    random_hex = uuid.uuid4().hex
    _, file_extension = os.path.splitext(filename)
    image_filename = random_hex + file_extension
    
    # Save the file
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    form_image.save(image_path)
    
    # Return the relative path for storing in the database
    return os.path.join('static/uploads', image_filename)

@app.route('/')
def index():
    """Home page with featured recipes and search"""
    search_form = SearchForm()
    
    # Get recent recipes for the homepage
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(4).all()
    
    # Get all categories
    categories = Category.query.all()
    
    return render_template('index.html', 
                          recipes=recent_recipes, 
                          categories=categories,
                          search_form=search_form)

@app.route('/recipes')
def recipe_list():
    """List all recipes with optional filtering by category"""
    search_form = SearchForm()
    
    category_id = request.args.get('category', type=int)
    
    # If category is specified, filter by it
    if category_id:
        recipes = Recipe.query.filter_by(category_id=category_id).order_by(Recipe.title).all()
        category = Category.query.get_or_404(category_id)
        page_title = f"Recipes in {category.name}"
    else:
        recipes = Recipe.query.order_by(Recipe.title).all()
        page_title = "All Recipes"
    
    # Get all categories for the sidebar
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('recipe_list.html', 
                          recipes=recipes, 
                          categories=categories,
                          page_title=page_title,
                          search_form=search_form)

@app.route('/recipes/<int:recipe_id>')
def recipe_detail(recipe_id):
    """Show the detail of a specific recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/recipes/new', methods=['GET', 'POST'])
def new_recipe():
    """Add a new recipe"""
    form = RecipeForm()
    
    # Get all categories for the dropdown
    categories = Category.query.order_by(Category.name).all()
    form.category.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        # Handle image upload
        image_url = None
        if form.image.data:
            image_url = save_image(form.image.data)
        
        # Handle category selection (0 means no category)
        category_id = form.category.data if form.category.data != 0 else None
        
        # Create new recipe
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            ingredients=form.ingredients.data,
            steps=form.steps.data,
            image_url=image_url,
            category_id=category_id
        )
        
        db.session.add(recipe)
        db.session.commit()
        
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    
    return render_template('recipe_form.html', form=form, title="New Recipe")

@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    """Edit an existing recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)
    form = RecipeForm(obj=recipe)
    
    # Get all categories for the dropdown
    categories = Category.query.order_by(Category.name).all()
    form.category.choices = [(0, 'No Category')] + [(c.id, c.name) for c in categories]
    
    if request.method == 'GET':
        # Set the current category in the form
        form.category.data = recipe.category_id if recipe.category_id else 0
    
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_url = save_image(form.image.data)
            recipe.image_url = image_url
        
        # Update recipe data
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.steps = form.steps.data
        recipe.category_id = form.category.data if form.category.data != 0 else None
        
        db.session.commit()
        
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    
    return render_template('recipe_form.html', form=form, recipe=recipe, title="Edit Recipe")

@app.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
def delete_recipe(recipe_id):
    """Delete a recipe"""
    recipe = Recipe.query.get_or_404(recipe_id)
    
    db.session.delete(recipe)
    db.session.commit()
    
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('recipe_list'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for recipes by title or ingredients"""
    form = SearchForm()
    
    if form.validate_on_submit() or request.args.get('query'):
        # Get the query from either form submission or URL parameters
        query = form.query.data if form.validate_on_submit() else request.args.get('query')
        search_type = form.search_type.data if form.validate_on_submit() else request.args.get('search_type', 'title')
        
        # Prepare search query
        search_term = f"%{query}%"
        
        if search_type == 'ingredients':
            recipes = Recipe.query.filter(Recipe.ingredients.ilike(search_term)).order_by(Recipe.title).all()
        else:  # Default to title search
            recipes = Recipe.query.filter(Recipe.title.ilike(search_term)).order_by(Recipe.title).all()
        
        # Get all categories for the sidebar
        categories = Category.query.order_by(Category.name).all()
        
        return render_template('recipe_list.html', 
                              recipes=recipes, 
                              categories=categories, 
                              search_query=query,
                              page_title=f"Search Results for '{query}'",
                              search_form=form)
    
    return redirect(url_for('recipe_list'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    """Add or view categories"""
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        
        if category_name and len(category_name.strip()) > 0:
            # Check if category already exists
            existing = Category.query.filter(Category.name.ilike(category_name)).first()
            
            if existing:
                flash('Category already exists!', 'warning')
            else:
                new_category = Category(name=category_name)
                db.session.add(new_category)
                db.session.commit()
                flash('Category added successfully!', 'success')
    
    # Get all categories
    categories = Category.query.order_by(Category.name).all()
    
    return render_template('categories.html', categories=categories)

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.get_or_404(category_id)
    
    # Update recipes in this category to have no category
    for recipe in category.recipes:
        recipe.category_id = None
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('manage_categories'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
