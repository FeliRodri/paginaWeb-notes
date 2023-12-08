from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, PasswordResetToken
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail 
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from datetime import datetime, timedelta
import secrets

socketio = SocketIO()

auth = Blueprint('auth', __name__)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        # user = current_user if current_user.is_authenticated else None

        if user:
            # Crear un token de restablecimiento de contraseña y enviar un correo electrónico con el enlace
            token = secrets.token_urlsafe(32)
            expiration_time = datetime.utcnow() + timedelta(hours=1)
            reset_token = PasswordResetToken(token=token, user_id=user.id, expiration_time=expiration_time)
            db.session.add(reset_token)
            db.session.commit()

            reset_link = url_for('auth.reset_password', token=token, _external=True)
            subject = 'Password Reset Request'
            body = f'Hello {user.first_name},\n\nTo reset your password, click on the following link:\n{reset_link}\n\nIf you did not request a password reset, please ignore this email.'
            msg = Message(subject, recipients=[email], body=body)
            mail.send(msg)

            flash('An email with instructions to reset your password has been sent.', 'info')
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
            flash('Email does not exists. Please sign up', category='error')
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

    return render_template("sign_up.html", user=current_user)    

