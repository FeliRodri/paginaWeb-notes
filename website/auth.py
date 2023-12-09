from sqlite3 import IntegrityError
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from . import mail 
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from datetime import datetime, timedelta
from .models import PasswordResetToken, db, User
from .forms import LoginForm, SignupForm 
import secrets

socketio = SocketIO()

auth = Blueprint('auth', __name__)

def send_reset_password_email(user, token):
    # Implementación de envío de correo electrónico para restablecimiento de contraseña
    reset_link = url_for('auth.reset_password', token=token, _external=True)
    subject = 'Password Reset Request'
    body = f'Hello {user.first_name},\n\nTo reset your password, click on the following link:\n{reset_link}\n\nIf you did not request a password reset, please ignore this email.'
    msg = Message(subject, recipients=[user.email], body=body)
    mail.send(msg)
    flash('An email with instructions to reset your password has been sent.', 'info')
    return redirect(url_for('auth.login'))

def generate_reset_token(user):
    # Implementación para generar un token de restablecimiento de contraseña
    token = secrets.token_urlsafe(32)
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    reset_token = PasswordResetToken(token=token, user_id=user.id, expiration_time=expiration_time)
    db.session.add(reset_token)
    db.session.commit()
    return token

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            token = generate_reset_token(user)
            send_reset_password_email(user, token)
            return redirect(url_for('auth.login'))

        flash('Email does not exist.', 'error')

    return render_template('forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if reset_token and reset_token.expiration_time > datetime.utcnow():
        try:
            if request.method == 'POST':
                new_password = request.form.get('new_password')
                reset_token.user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.delete(reset_token)
                db.session.commit()

                flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
                return redirect(url_for('auth.login'))

            return render_template('reset_password.html', token=token)   
        
        except Exception as e:
            print(f"Error resetting password: {e}")
            flash('An error occurred while resetting your password. Please try again.', 'error')
            return redirect(url_for('auth.forgot_password'))

    flash('Invalid or expired token. Please try again.', 'error')
    return redirect(url_for('auth.forgot_password'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')

        print("Received POST request to /login")
        print("Form data:", request.form)

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('logged in succesfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exists. Please sign up', category='error')
    return render_template("login.html", user=current_user, form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        first_name = form.firstName.data
        password1 = form.password.data
        password2 = form.confirm_password.data

        try:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('La dirección de correo electrónico ya está asociada con una cuenta existente. Por favor, usa otra dirección de correo electrónico.', category='error')
                return render_template("sign_up.html", form=form)

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
                return redirect(url_for('auth.login'))
        
        except IntegrityError:
            db.session.rollback()  # Deshacer cambios en caso de error de integridad
            flash('La dirección de correo electrónico ya está asociada con una cuenta existente. Por favor, usa otra dirección de correo electrónico.', category='error')
            return render_template("sign_up.html", form=form)
        except Exception as e:
            print(f"Error: {e}")
            flash('Ocurrió un error durante la creación de la cuenta. Por favor, inténtalo nuevamente más tarde.', category='error') 
            return render_template("sign_up.html", form=form)  

    return render_template("sign_up.html", form=form)    


