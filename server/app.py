#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class Signup(Resource):
    @app.route('/users', methods=['POST'])
    def create_user():
        data = request.get_json()
        username_exists = User.query.filter_by(username=data['username']).first()
        if username_exists:
            return jsonify({"error": "Unprocessable Entity"}), 422

        new_user = User(
            username=data['name'],
            password= bcrypt.generate_password_hash( data['password'] ).decode('utf-8') ,
            image_url=data['image_url'],
            bio=data.get('bio'),
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": "User created successfully"}), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    'user_id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 200
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return {
                'user_id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        return {'error': 'Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return {}, 204
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes = Recipe.query.all()
            return [{
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'user_id': recipe.user.id,
                    'username': recipe.user.username,
                    'image_url': recipe.user.image_url,
                    'bio': recipe.user.bio
                }
            } for recipe in recipes], 200
        return {'error': 'Unauthorized'}, 401

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)