from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=4)])
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=7, message='La contraseña debe tener al menos 7 caracteres.'),
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]+$', message='La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un carácter especial.'),
        EqualTo('confirm_password', message='Las contraseñas no coinciden.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class CreateNoteForm(FlaskForm):
    note = TextAreaField('Note', validators=[DataRequired()])
    category = StringField('Category')
    reminder = DateTimeField('Reminder', format='%Y-%m-%dT%H:%M', render_kw={'type': 'datetime-local'})
    submit = SubmitField('Create Note')

class EditNoteForm(FlaskForm):
    note = TextAreaField('Note')
    category = StringField('Category')
    reminder = DateTimeField('Reminder', format='%Y-%m-%dT%H:%M', render_kw={'type': 'datetime-local'})
    submit = SubmitField('Save Changes')