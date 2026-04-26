from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask app
app = Flask(__name__)

# --- Database Configuration ---
# This creates a database file named 'hotel_reservations.db' in an 'instance' folder.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'hotel_reservations.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model ---
# This defines the structure of our 'reservation' table.
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    check_in = db.Column(db.String(20), nullable=False) # Storing as string for simplicity in a prototype
    check_out = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Reservation {self.guest_name}>'

# Create the database and table if they don't exist
with app.app_context():
    # Ensure the instance folder exists
    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))
    db.create_all()


# --- Routes ---

# 1. Welcome Page
@app.route('/')
def index():
    # Renders the main entry page with "Book a Room" and "Manager" buttons
    return render_template('index.html')

# 2. Reservation Page (handles both GET to show form and POST to save data)
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        # Get data from the form
        g_name = request.form.get('name')
        c_in = request.form.get('check_in')
        c_out = request.form.get('check_out')
        r_type = request.form.get('room_type')

        # Create a new Reservation object
        new_reservation = Reservation(
            guest_name=g_name,
            check_in=c_in,
            check_out=c_out,
            room_type=r_type
        )

        # Add to session and commit to save to the database
        db.session.add(new_reservation)
        db.session.commit()

        # Redirect to the confirmation page, passing the guest's name
        return redirect(url_for('confirm', name=g_name, check_in=c_in, check_out=c_out))

    # If it's a GET request, just show the blank form
    return render_template('reserve.html')

# 3. Confirmation Page
@app.route('/confirmation/<name>')
def confirm(name):
    # This page confirms the booking. It receives dynamic data from the URL.
    c_in = request.args.get('check_in')
    c_out = request.args.get('check_out')
    return render_template('confirm.html', name=name, check_in=c_in, check_out=c_out)

# 4. Reservation List (Manager's View)
@app.route('/reservations')
def list_reservations():
    # This route queries all reservations and displays them.
    # It is intended for the "Manager" view.
    all_reservations = Reservation.query.all()
    return render_template('list.html', reservations=all_reservations)


if __name__ == '__main__':
    app.run(debug=True)