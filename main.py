# ------ Импорт прочих библиотек
import datetime
import os
from time import time
from PIL import Image
from werkzeug.utils import secure_filename
from config import SECRET_KEY
from resources.tests_resource import TestsResource
from requests import get

# ------ Импорт flask инструментов
from flask import (Flask, render_template, redirect, jsonify, url_for,
                   request, abort)
from flask_wtf.csrf import CSRFProtect
from flask_restful import Api

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
from data.questions import Question

# ------ Конфигурация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
api = Api(app)
api.add_resource(TestsResource, '/api/v2/tests')
csrf = CSRFProtect(app)
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
    data = get('http://localhost:8080/api/v2/tests').json()
    tests = list(data.values())[0]
    return render_template('start.html', tests=tests)


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
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.email == current_user.email).first()
    tests_list = user.questions
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


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    form = ProfileGeneralForm()
    password_form = ProfilePasswordForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.email == current_user.email).first()
    tests_list = user.questions

    if form.validate_on_submit():
        if form.name.data != '':
            user.name = form.name.data
        if form.email.data != '':
            user.email = form.email.data
        if form.about.data != '':
            user.about = form.about.data
        db_sess.commit()

    return render_template('profile.html', form=form,
                           password_form=password_form, tests=tests_list)


@app.route("/profile/password_update", methods=["POST"])
@login_required
def update_profile_password():
    form = ProfileGeneralForm()
    password_form = ProfilePasswordForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.email == current_user.email).first()
    tests_list = user.questions

    if form.validate_on_submit():
        if user.check_password(password_form.old_password.data):
            if password_form.new_password.data == password_form.repeat_password.data:
                user.set_password(password_form.new_password.data)
                db_sess.commit()

    return render_template('profile.html', form=form,
                           password_form=password_form, tests=tests_list)


# ------ роут конструктора тестов
@app.route('/constructor')
@login_required
def constructor():
    return render_template('constructor.html')


@app.route('/constructor/create_test', methods=['GET', 'POST'])
@login_required
def constructor_create_test():
    datas = request.get_json()
    print(datas)
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.email == current_user.email).first()
    question = Question()
    question.user_id = user.id
    question.title = datas['title']
    question.description = datas['description']
    question.is_private = datas['is_private']
    question.test_type = datas['test_type']
    question.criteria = datas['criteria']
    question.questions = datas['questions']
    db_sess.add(question)
    db_sess.commit()
    return jsonify(success=True), 200


@app.route('/constructor/success', methods=['GET', 'POST'])
@login_required
def constructor_create_success():
    return jsonify(success=True), 200


# ------ роуты проведения тестов
@app.route('/tests/<int:test_id>', methods=['GET'])
@login_required
def take_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Question).get(test_id)
    if not test:
        abort(404)

    return render_template('take_test.html', test=test)


@app.route('/tests/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_test(test_id):
    db_sess = db_session.create_session()
    test = db_sess.query(Question).get(test_id)
    if not test:
        abort(404)

    form = request.form
    total = len(test.questions or [])
    correct_count = 0
    details = []

    for idx, q in enumerate(test.questions or []):
        field = f'ans-{idx}'
        q_type = q.get('type')

        if q_type == 'single':
            raw = form.get(field)
            try:
                user_choice = int(raw) if raw is not None else None
            except ValueError:
                user_choice = None
            is_ok = (user_choice == q.get('correct'))
            answer_representation = user_choice

        elif q_type == 'multiple':
            raw_list = form.getlist(field)
            try:
                user_choice = [int(x) for x in raw_list]
            except ValueError:
                user_choice = []
            is_ok = sorted(user_choice) == sorted(q.get('correct', []))
            answer_representation = user_choice

        elif q_type == 'text':
            user_txt = form.get(field, '').strip().lower()
            correct_txt = q.get('answer', '').strip().lower()
            is_ok = (user_txt == correct_txt)
            answer_representation = user_txt

        else:
            is_ok = False
            answer_representation = None

        if is_ok:
            correct_count += 1

        details.append({
            'question_index': idx,
            'type': q_type,
            'user_answer': answer_representation,
            'is_correct': is_ok
        })

    score = (correct_count / total * 100) if total else 0

    return render_template(
        'test_result.html',
        test=test,
        total=total,
        correct=correct_count,
        score=score,
        details=details
    )


if __name__ == '__main__':
    db_session.global_init("db/quizzy.db")
    app.run(port=8080, host='0.0.0.0')
