import os
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from settings import DB_USER, DB_PASSWORD, DB_NAME

# Sử dụng DATABASE_URL từ biến môi trường, fallback là postgresql://student:student@localhost:5432/trivia nếu không có
DB_URL = 'postgresql://{}:{}@localhost:5432/{}'.format(DB_USER, DB_PASSWORD, DB_NAME)
print(DB_URL)

db = SQLAlchemy()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path if database_path else DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)  
    answer = Column(String, nullable=False)
    category = Column(Integer, ForeignKey('categories.id'), nullable=False) 
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)  # Đảm bảo dữ liệu không được để trống

    questions = db.relationship('Question', backref='categories', lazy=True)  # Thiết lập quan hệ một-nhiều với Question

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
