from flask import Flask, request, session
from flask_restful import Api, Resource
from config import db, bcrypt
from models import User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key'

db.init_app(app)
bcrypt.init_app(app)

api = Api(app)


class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')
        
        # Check if username already exists
        existing_user = User.query.filter(User.username == username).first()
        if existing_user:
            return {'error': 'Username already exists'}, 422
        
        try:
            # Create new user
            new_user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
            new_user.password_hash = password
            
            db.session.add(new_user)
            db.session.commit()
            
            # Set session
            session['user_id'] = new_user.id
            
            return new_user.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 422


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 401
        
        return user.to_dict(), 200


class Login(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter(User.username == username).first()
        
        if not user or not user.authenticate(password):
            return {'error': 'Invalid username or password'}, 401
        
        session['user_id'] = user.id
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401
        session.pop('user_id', None)
        return {}, 200


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 401
        
        recipes = [recipe.to_dict() for recipe in user.recipes]
        return recipes, 200
    
    def post(self):
        user_id = session.get('user_id')
        
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 401
        
        data = request.get_json()
        
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')
        
        try:
            new_recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            
            db.session.add(new_recipe)
            db.session.commit()
            
            return new_recipe.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 422


api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')


if __name__ == '__main__':
    app.run(debug=True)

