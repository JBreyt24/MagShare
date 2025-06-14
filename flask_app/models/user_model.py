from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    myDB = "Exam_erd"

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

# Validation

    @staticmethod
    def validate_user(user_form_data):
        is_valid = True
        query = """
        SELECT * FROM users 
        WHERE email = %(email)s;
        """
        results = connectToMySQL("Exam_erd").query_db(query, user_form_data)

        if len(results) >= 1:
            flash("Email is already registered. Please log in", "register")
            is_valid = False
        if not user_form_data['first_name'].isalpha():
            flash('First name can ONLY contain letters', "register")
            is_valid = False
        if len(user_form_data['first_name']) < 2:
            flash('First name must be at least 2 characters', "register")
            is_valid = False
        if not user_form_data['last_name'].isalpha():
            flash('Last name can ONLY contain letters', "register")
            is_valid = False
        if len(user_form_data['last_name']) < 2:
            flash('Last name must be at least 2 characters', "register")
            is_valid = False
        if not EMAIL_REGEX.match(user_form_data['email']):
            flash("Invalid email format", "register")
            is_valid = False
        if len(user_form_data['password']) < 8:
            flash('Password must be at least 8 characters', "register")
            is_valid = False
        if user_form_data['password'] != user_form_data['password_confirmation']:
            flash('Passwords do not match. Please try again', "register")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_user_at_edit(user_form_data):
        is_valid = True
        if len(user_form_data["first_name"]) < 2:
            flash('First name must be at least 2 characters', "account")
            is_valid = False
        if len(user_form_data["last_name"]) < 2:
            flash('Last name must be at least 2 characters', "account")
            is_valid = False
        if not EMAIL_REGEX.match(user_form_data["email"]):
            flash("Invalid email. Must be a valid email", "account")
            is_valid = False
        return is_valid

# Create

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO users (first_name, last_name, email, password)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """
        return connectToMySQL(cls.myDB).query_db(query, data)

# Read

    @classmethod
    def get_one(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        data = { 'id': user_id }
        results = connectToMySQL(cls.myDB).query_db(query, data)
        return cls(results[0])

    @classmethod
    def find_user_login(cls, email_dict):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.myDB).query_db(query, email_dict)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def find_user_register(cls, email_dict):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.myDB).query_db(query, email_dict)
        if len(results) > 1:
            return False
        return cls(results[0])

    @classmethod
    def rename(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.myDB).query_db(query)
        print(results)
        return results

# Update

    @classmethod
    def update_user(cls, data):
        query = """
        UPDATE users
        SET first_name = %(first_name)s,
            last_name = %(last_name)s,
            email = %(email)s,
            updated_at = NOW()
        WHERE id = %(id)s;
        """
        return connectToMySQL(cls.myDB).query_db(query, data)
