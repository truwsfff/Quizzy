# ------ Импорт прочих библиотек
import datetime
import os
from time import time
from PIL import Image
from werkzeug.utils import secure_filename

from config import SECRET_KEY

# ------ Импорт flask инструментов
from flask import (Flask, render_template, redirect, jsonify, url_for,
                   request, abort)

# ------ Импорт инструментов для регистрации
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user)
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.profile_general_form import ProfileGeneralForm
from forms.profile_password_form import ProfilePasswordForm

# ------ Импорт всего связанного с бд
from data import db_session
from data.users import User

# ------ Конфигурация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# ------ обработка ошиброк


@app.errorhandler(400)
def handle_400(error):
    return jsonify(error=error.description), 400


@app.errorhandler(413)
def handle_413(error):
    return jsonify(error='Загружаемый файл превышает 4 МБ'), 413


@app.errorhandler(415)
def handle_415(error):
    return jsonify(error=error.description), 415


# ------ Все роуты приложения
# ------ Главная страница
@app.route('/')
def start_window():
    return render_template('start.html')


# ------ Роуты аутентификации
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        # Валидатор никнеймов
        if len(form.nickname.data) < 5 or len(form.nickname.data) > 15:
            return render_template('register.html',
                                   error_message='\
Никнейм не должен превышать 15 символов и быть меньше 5 символов.',
                                   form=form)

        for i in r"""!"#$%&'()*+,-./:;<=>?@[\]^`{|}~ 
        абвгдеёжзийклмнопрстуфхцчшщъыьэюя""":
            if i in form.nickname.data.strip().lower():
                return render_template('register.html',
                                       error_message='\
Никнейм не должен содержать специальных символов/пробелы/буквы русского '
                                                     'алфавита.',
                                       form=form)

        # Валидатор паролей
        if len(form.password.data) < 5:
            return render_template('register.html',
                                   error_message='\
Пароль должен содержать 5 и более символов.',
                                   form=form)

        if form.password.data != form.password_repeat.data:
            return render_template('register.html',
                                   error_message='\
        Пароли не совпадают.',
                                   form=form)

        # Валидатор О себе
        if form.about.data != '':
            if len(form.about.data) > 100:
                return render_template('register.html',
                                       error_message='\
Превышен лимит символов в графе "О себе": должно быть не более 100.',
                                       form=form)

        # Записываем пользователя в бд
        user = User(
            name=form.nickname.data,
            about=form.about.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               error_message='Неправильный логин или пароль',
                               form=form)
    return render_template('login.html', form=form)


# ------ роут выхода из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# ------ роуты профиля
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    tests_list = [
    ]
    form = ProfileGeneralForm()
    password_form = ProfilePasswordForm()
    return render_template('profile.html', form=form,
                           password_form=password_form, tests=tests_list)


@app.route('/profile/avatar', methods=['POST'])
@login_required
def avatar_handler():
    if 'avatar' not in request.files:
        abort(400, description='файл не найден')

    file = request.files['avatar']

    if file.filename == '':
        abort(415, description='Файл не выбран')

    if not allowed_extension(file.filename):
        abort(415, description='Недопустимый тип файла')

    if not is_image(file.stream):
        abort(415, description='Файл не является изображением')

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.email == current_user.email).first()

    if user.avatar != 'avatars/quizzy_logo.png':
        os.remove(f'static/{user.avatar}')

    extens = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f'avatar_{next(generator_names())}.{extens}')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    user.avatar = f'avatars/{filename}'
    db_sess.commit()

    return jsonify(
        {'avatar_url': url_for('static', filename=user.avatar)})


def allowed_extension(filename):
    allowed = ['png', 'jpg', 'jpeg']
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed:
        return True
    else:
        return False


def is_image(file):
    try:
        image = Image.open(file)
        image.verify()
        file.seek(0)
        return True
    except:
        return False


def generator_names():
    while True:
        text = '{}'
        t = time()
        yield text.format(''.join(str(t).split('.')))


# ------ роут конструктора тестов
@app.route('/constructor')
def constructor():
    return render_template('constructor.html')


if __name__ == '__main__':
    db_session.global_init("db/quizzy.db")
    app.run(port=8080, host='0.0.0.0')
