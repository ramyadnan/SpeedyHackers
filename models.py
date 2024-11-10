from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    
    @staticmethod
    def create_google_user(email, google_id):
        # Extract username from email (everything before @)
        username = email.split('@')[0]
        
        # If username already exists, append numbers until unique
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        user = User(
            username=username,
            email=email,
            google_id=google_id
        )
        return user
    
    def __repr__(self):
        return f'<User {self.username}>'

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)