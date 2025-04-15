from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, \
    StringField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nickname = StringField('О себе', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_repeat = PasswordField('Пароль', validators=[DataRequired()])
    about = TextAreaField('О себе')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')
