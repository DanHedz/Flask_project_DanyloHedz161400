from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Offer
from flask_migrate import Migrate
# Initialize the Flask application and set up configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'mysecret'
db.init_app(app)
migrate = Migrate(app, db)

# Initialize LoginManager for user authentication
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for Home page, showing all offers
@app.route('/')
def home():
    offers = Offer.query.all()
    return render_template('home.html', offers=offers)

# Route for Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

# Route for Logout, logging out the current user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Route for Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/profile')
def profile():
    return "This is the profile page"

# Route to create a new offer
@app.route('/create_offer', methods=['GET', 'POST'])
@login_required
def create_offer():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        discount = request.form.get('discount', None)
        offer = Offer(name=name, description=description, price=price, discount=discount, user_id=current_user.id)
        db.session.add(offer)
        db.session.commit()
        flash('Offer created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_offer.html')

# Route to edit an offer
@app.route('/edit_offer/<int:offer_id>', methods=['GET', 'POST'])
@login_required
def edit_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if offer.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to edit this offer.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        offer.name = request.form['name']
        offer.description = request.form['description']
        offer.price = float(request.form['price'])
        offer.discount = request.form.get('discount', None)
        db.session.commit()
        flash('Offer updated!', 'success')
        return redirect(url_for('home'))

    return render_template('edit_offer.html', offer=offer)

# Route to delete an offer
@app.route('/delete_offer/<int:offer_id>', methods=['POST'])
@login_required
def delete_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if offer.user_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to delete this offer.', 'danger')
        return redirect(url_for('home'))

    db.session.delete(offer)
    db.session.commit()
    flash('Offer deleted!', 'success')
    return redirect(url_for('home'))
# Main entry point for the Flask application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)