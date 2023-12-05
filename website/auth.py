from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from . import db 
from flask_login import login_user, login_required, logout_user, current_user

socketio = SocketIO()

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('logged in succesfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exists.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('El Email ya se encuentra registrado', category='error')
                return render_template("sign_up.html")

            if len(email) < 4:
                flash('El Email debe tener mas de 3 caracteres.', category='error')
            elif len(first_name) < 2:
                flash('El primer nombre debe tener mas de 1 caracteres.', category='error')
            elif password1 != password2:
                flash('Las contraseñas no coinciden.', category='error')
            elif len(password1) < 7:
                flash('La contraseña debe tener al menos 7 caracteres.', category='error')
            else:
                new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Cuenta creada satisfactoriamente!', category='success')
                return redirect(url_for('views.home'))
        
        except Exception as e:
            print(f"Error: {e}")
            flash('Ocurrió un error durante la creación de la cuenta.', category='error') 
            return render_template("sign_up.html")      

    
    socketio.emit('update_notes', namespace='/')   
    return redirect(url_for('views.home'))
