from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth config
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="google.authorized",
    authorized_url="/login/google/authorized"  # Change from redirect_url
)
app.register_blueprint(google_bp, url_prefix="/login")

# Ensure OAUTHLIB_INSECURE_TRANSPORT is set for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove in production

db.init_app(app)

# Create tables within app context
with app.app_context():
    db.create_all()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))
                
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    email = resp.json()["email"]
    
    # Check if user exists, if not create new user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=email, email=email)
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    flash('Successfully logged in with Google.')
    return redirect(url_for('dashboard'))

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Google.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", category="error")
        return False

    google_info = resp.json()
    google_user_id = google_info["id"]
    return False  # Don't create default Flask-Dance models

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully')
    return redirect(url_for('landing'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=user.username)

@app.route('/health-input-form')
def health_input_form():
    era = request.args.get('era')
    return render_template('health-input-form.html', selected_era=era)

if __name__ == '__main__':
    app.run(debug=True)