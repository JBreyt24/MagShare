from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user_model import User
from flask_app.controllers.users_controller import User
from flask import flash, session, request
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class Magazine:
    myDB = "Exam_erd"

    def __init__(self, data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.title = data['title']
        self.description = data['description']
        self.image = data.get('image')  # optional if you later re-enable image uploads
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.author = None

# Create Magazine

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO magazines (user_id, title, description)
        VALUES (%(user_id)s, %(title)s, %(description)s);
        """
        return connectToMySQL(cls.myDB).query_db(query, data)

    @staticmethod
    def validate_magazine_at_create(magazine_form_data):
        is_valid = True
        if len(magazine_form_data['title']) < 2:
            flash('Title must be at least 2 characters', "magazine")
            is_valid = False
        if len(magazine_form_data['description']) < 10:
            flash('Description must be at least 10 characters', "magazine")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_magazine_at_edit(magazine_form_data):
        is_valid = True
        if len(magazine_form_data['title']) < 2:
            flash('Title must be at least 2 characters', "magazine")
            is_valid = False
        if len(magazine_form_data['description']) < 10:
            flash('Description must be at least 10 characters', "magazine")
            is_valid = False
        return is_valid

# Read Magazine

    @classmethod
    def get_one(cls, magazine_id):
        query = """
        SELECT * FROM magazines
        WHERE id = %(id)s;
        """
        data = {'id': magazine_id}
        results = connectToMySQL(cls.myDB).query_db(query, data)
        return cls(results[0])

    @classmethod
    def get_all_magazines_w_user(cls):
        query = """
        SELECT * FROM magazines
        LEFT JOIN users ON magazines.user_id = users.id
        """
        results = connectToMySQL(cls.myDB).query_db(query)
        magazine_by_user = []
        for magazine in results:
            one_magazine = cls(magazine)
            magazine_dict = {
                'id': magazine["users.id"],
                'first_name': magazine['first_name'],
                'last_name': magazine['last_name'],
                'email': magazine['email'],
                'password': None,
                'created_at': magazine['users.created_at'],
                'updated_at': magazine['users.updated_at']
            }
            one_magazine.author = User(magazine_dict)
            magazine_by_user.append(one_magazine)
        return magazine_by_user
    

    @classmethod
    def get_user_subscriptions(cls, user_id):
        query = """
        SELECT magazines.* FROM subscriptions
        JOIN magazines ON subscriptions.magazine_id = magazines.id
        WHERE subscriptions.user_id = %(user_id)s;
        """
        data = { "user_id": user_id }
        results = connectToMySQL(cls.myDB).query_db(query, data)
        
        if not results or isinstance(results, bool):
            return []  # Return an empty list if query failed or no subscriptions

        subscriptions = []
        for magazine in results:
            subscriptions.append(cls(magazine))
        return subscriptions



# Edit Magazine

    @classmethod
    def edit_magazine(cls, data):
        query = """
        UPDATE magazines
        SET title = %(title)s,
            description = %(description)s,
            updated_at = NOW()
        WHERE id = %(id)s;
        """
        return connectToMySQL(cls.myDB).query_db(query, data)

# Delete Magazine

    @classmethod
    def destroy_magazine(cls, magazine_id):
        query = """ 
        DELETE FROM magazines
        WHERE id = %(id)s;
        """
        data = {
            "id": magazine_id
        }
        return connectToMySQL(cls.myDB).query_db(query, data)

# Subscribe Magazine

@classmethod
def subscribe(cls, data):
    query = """
    INSERT INTO subscriptions (user_id, magazine_id)
    VALUES (%(user_id)s, %(magazine_id)s);
    """
    return connectToMySQL(cls.myDB).query_db(query, data)

@classmethod
def get_user_subscriptions(cls, user_id):
    query = """
    SELECT magazines.*, users.id AS author_id, users.first_name, users.last_name, users.email, users.created_at AS user_created_at, users.updated_at AS user_updated_at
    FROM subscriptions
    JOIN magazines ON subscriptions.magazine_id = magazines.id
    JOIN users ON magazines.user_id = users.id
    WHERE subscriptions.user_id = %(user_id)s;
    """
    results = connectToMySQL(cls.myDB).query_db(query, {'user_id': user_id})
    
    subscriptions = []
    for row in results:
        magazine = cls(row)
        magazine.author = User({
            'id': row['author_id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'password': None,
            'created_at': row['user_created_at'],
            'updated_at': row['user_updated_at']
        })
        subscriptions.append(magazine)
    return subscriptions
