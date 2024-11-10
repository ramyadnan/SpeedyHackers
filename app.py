from flask import Flask, render_template, request, redirect, url_for, session, flash
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

load_dotenv()  # Load environment variables

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

@app.route('/')
def landing():
    return render_template('landing.html')

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
            return redirect(url_for('dashboard'))
            
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
        return redirect(url_for('dashboard'))
        
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
    
    return redirect(url_for('dashboard'))

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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user)

@app.route('/health-input-form')
def health_input_form():
    era = request.args.get('era')
    return render_template('health-input-form.html', selected_era=era)

if __name__ == '__main__':
    app.run(debug=True)