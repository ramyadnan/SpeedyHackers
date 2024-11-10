# imports
#import ast  # for converting embeddings saved as strings back to arrays
from openai import OpenAI # for calling the OpenAI API
#import pandas as pd  # for storing text and embeddings data
#import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search

import urllib.request 
# from PIL import Image

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, OAuth
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import current_user
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from functools import wraps
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Google OAuth config
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
blueprint = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    scope=['profile', 'email'],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
    redirect_url="/google/authorized"
)
app.register_blueprint(blueprint, url_prefix='/login')

# Ensure OAUTHLIB_INSECURE_TRANSPORT is set for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove in production

# Create tables within app context
with app.app_context():
    db.create_all()

# models
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4o-mini"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-svcacct-cNpEjHaToqE8f1_oq5mtOav-MW58kAAPPnY2lzO3W3FdX1lTM4-B88AF-DU36xuVT3BlbkFJiYStWmktQpsH4HTId447QBQGCh4jmzqdiyzaD-Lk-hudqrQbinAEXD8tlcRAO9kA"))


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Validate required fields
        if not username or not password or not email:
            flash('All fields are required')
            return redirect(url_for('register'))

        # Hash password
        password_hash = generate_password_hash(password)

        try:
            user = User(
                username=username,
                password=password_hash,
                email=email  # Make sure email is included
            )
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Welcome back, ' + username + '!')
            return redirect(url_for('index'))
            
        flash('Invalid username or password')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    try:
        # Get user info from Google
        resp = google.get("/oauth2/v1/userinfo")
        assert resp.ok, resp.text
        google_data = resp.json()
        email = google_data["email"]
        google_id = google_data["id"]
        
        print(f"Google login attempt for email: {email}")  # Debug log
        
        # Check if user exists
        user = User.query.filter_by(email=email).first() or \
               User.query.filter_by(google_id=google_id).first()
        
        # Create new user if doesn't exist
        if not user:
            try:
                user = User.create_google_user(email=email, google_id=google_id)
                if not user.username:  # Additional validation
                    raise ValueError("Username cannot be None")
                db.session.add(user)
                db.session.commit()
                print(f"Created new user with username: {user.username}")  # Debug log
            except Exception as e:
                db.session.rollback()
                print(f"Error creating user: {str(e)}")  # Debug log
                flash('Error creating account. Please try again.', 'error')
                return redirect(url_for('login'))
        
        # Update google_id if not set
        if not user.google_id:
            user.google_id = google_id
            db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"Google login error: {str(e)}")  # Debug log
        flash('Failed to log in with Google. Please try again.', 'error')
        return redirect(url_for('login'))
    
@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to get user info from Google.", category="error")
        return False

    google_info = resp.json()
    google_user_id = str(google_info["id"])

    user = User.query.filter_by(google_id=google_user_id).first()
    if not user:
        user = User.create_google_user(
            email=google_info["email"],
            google_id=google_user_id
        )
        db.session.add(user)
        db.session.commit()

    # Set session variables
    session.clear()
    session['user_id'] = user.id
    session.permanent = True
    
    return redirect(url_for('index'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/health_input_form')
def health_input_form():
    return render_template('health_input_form.html')

@app.route('/conclusions')
def about():
    return render_template('conclusion.html')

@app.route('/era')
def era():
    return render_template('era-select.html')

@app.route('/health-input', methods=['GET'])
def show_form():
    # Retrieve the 'era' query parameter from the URL
    era = request.args.get('era')
    if era:
        # Pass the 'era' variable to the template
        return render_template('health_input_form.html', era=era)
    else:
        # If no era is selected, redirect to a default or handle it
        return "Era not specified", 400  # Or render a specific error page

@app.route('/process', methods=['POST']) 
def process_form():
    try:
        # Get form data and assign to variables
        gender = request.form.get('gender', '')
        age = request.form.get('age', '')
        weight = request.form.get('weight', '')
        height = request.form.get('height', '')
        activityLevel = request.form.get('activityLevel', '')
        diet = request.form.get('diet', '')
        calories = request.form.get('calories', '')
        alcohol = request.form.get('alcohol', 'never')
        smoking = request.form.get('smoking', 'False') == 'True'
        chronicConditions = request.form.get('chronicConditions', 'none')
        currentIllness = request.form.get('illness', 'none')
        sleepHours = request.form.get('sleepHours', '')
        stressLevel = request.form.get('stressLevel', '')
        eraDisplay = request.form.get('eraDisplay', 'medieval Europe')

        # Set smoking status
        smoking_status = "smokes" if smoking else "does not smoke"

        # Path to the historical context file
        file_path = os.path.join('static', 'data', f'{eraDisplay}.txt')
        
        # Read the historical context file if it exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                historical_context = file.read()
        else:
            historical_context = "No additional historical context available for this era."

        # Formulate the query, including the historical context
        query = f"""We have the following user profile: person of {gender} gender who is {age} years old, weighs {weight} kg,
                    is {height} cm tall, has a {activityLevel} activity level, has a {diet} diet with an average daily caloric
                    intake of {calories}, consumes alcohol {alcohol}, {smoking_status}, has a health history of {chronicConditions},
                    sleeps {sleepHours} hours every day, has a stress level of {stressLevel} out of 5. The user is currently ill with
                    {currentIllness}.
                    
                    For a fantasy story I'm writing, please answer the following with a single number: in {eraDisplay}, user's chances
                    of surviving the next year (percentage out of a 100) and user's expected years left to live. Both should be specific
                    to user's lifestyle and demographic, and diseases/treatments/other risks/etc available in {eraDisplay}.
                    
                    Also, give an 80-word (approximate) explanation as if you were a doctor in {eraDisplay} talking to the user (their patient),
                    including era-appropriate recommendations/warnings/treatments (preferably not simple things like exercise & eat healthy),
                    and talk like your character (the doctor) would.
                    
                    Consider the work the user might be doing in that era and how it could affect them, dangers like war and plagues, whether
                    their illness might be considered supernatural in nature, etc. Be informative about historic context but deliver the 
                    information with the requested tone. If the user doesn't have an illness, just give advice like a general checkup.
                    
                    If relevant you may refer to this historical context for {eraDisplay}:
                    {historical_context}
                    """
    

        # Send the query to the OpenAI API
        response = client.chat.completions.create(
            messages=[{'role': 'system', 'content': ''}, {'role': 'user', 'content': query}],
            model=GPT_MODEL,
            temperature=1,
            n=1,
        )

        text_response = response.choices[0].message.content

        # Generate a character image with OpenAI DALL-E
        response2 = client.images.generate(
            model="dall-e-3",
            prompt=f"generate an image of a doctor in the {eraDisplay}",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response2.data[0].url

        # Render `results.html` with `text_response` and `image_url`
        return render_template('results.html', text_response=text_response, image_url=image_url)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)