from flask_wtf import FlaskForm
from wtforms import EmailField, SubmitField, StringField, \
    TextAreaField


class ProfileGeneralForm(FlaskForm):
    name = StringField('Новый никнейм')
    email = EmailField('Новая почта')
    about = TextAreaField('О себе (не более 100 символов)')
    submit = SubmitField('Сохранить изменения')
